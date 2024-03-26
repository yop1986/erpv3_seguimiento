import uuid
from datetime import date

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Max, Sum, F, Value
from django.db.models.constraints import UniqueConstraint
from django.utils.translation import gettext as _
from django.urls import reverse_lazy

from django_ckeditor_5.fields import CKEditor5Field
from simple_history.models import HistoricalRecords

from usuarios.models import Usuario
from usuarios.personal_views import Configuracion

conf = Configuracion()

class Estado (models.Model):
    id      = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    descripcion  = models.CharField(verbose_name=_('Descripción'), max_length=30, unique=True)
    bloquea = models.BooleanField(_('Bloquea modificaciones'), default=False, help_text=_('Determina si bloquea modificaciones'))
    vigente    = models.BooleanField(_('Vigente'), default=True)
    actualizacion   = models.DateTimeField(_('Actualización'), auto_now=True)

    history = HistoricalRecords(excluded_fields=['actualizacion'], user_model=settings.AUTH_USER_MODEL)

    def __str__(self):
        return self.descripcion

    def get_vigente(self):
        return _('Si') if self.vigente else _('No')

    def get_bloquea(self):
        return _('Si') if self.bloquea else _('No')

    def url_create():
        return reverse_lazy('seguimiento:create_estado')

    def url_detail(self):
        return reverse_lazy('seguimiento:detail_estado', kwargs={'pk': self.id})

    def url_update(self):
        return reverse_lazy('seguimiento:update_estado', kwargs={'pk': self.id})

    def url_delete(self):
        if Proyecto.objects.filter(estado=self).count()>0:
            return None
        return reverse_lazy('seguimiento:delete_estado', kwargs={'pk': self.id})

class Proyecto(models.Model):
    id      = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre  = models.CharField(verbose_name=_('Nombre'), max_length=90, unique=True)
    descripcion = CKEditor5Field(verbose_name=_('Descripción'), blank=True, config_name='extends')
    enlace_cloud= models.URLField(verbose_name=_('URL'), blank=True)
    creacion= models.DateField(_('Creación'), auto_now_add=True)
    actualizacion   = models.DateTimeField(_('Actualización'), auto_now=True)
    finicio = models.DateField(_('Fecha Inicio'))
    ffin    = models.DateField(_('Fecha Fin'))
    publico = models.BooleanField(_('Público'), default=True, help_text=_('Define si el proyecto es visible para todos los usuarios'))

    estado  = models.ForeignKey(Estado, verbose_name=_('Estado'), on_delete=models.RESTRICT)
    history = HistoricalRecords(excluded_fields=['creacion', 'actualizacion'], user_model=settings.AUTH_USER_MODEL)

    class Meta:
        permissions = [
            ("proyect_admin", "Permite ver todos los proyectos, sean publicos o privados")
        ]

    def __str__(self):
        return self.nombre

    def clean(self):
        if (self.finicio >= self.ffin):
            raise ValidationError(_('La fecha de inicio debe ser menor a fecha de finalización'), code='invalid')
        if self.ffin < date.today():
            raise ValidationError(_('La fecha de finalización ya pasó'), code='invalid')

    def get_periodo(self):
        formato = conf.get_value('sitio', 'formato_fecha')
        if formato:
            finicio = self.finicio.strftime(formato)
            ffin = self.ffin.strftime(formato)
            return f'{finicio} - {ffin}'
        return f'{self.finicio} - {self.ffin}'

    def get_resumen(self, max_length=60):
        suspensivos = '...' if len(self.descripcion) > max_length else ''
        resumen = self.descripcion[:max_length].replace("\n", "")
        return f'{resumen}{suspensivos}'

    def get_have_url(self):
        if self.enlace_cloud:
            return True
        return False
        
    def get_modificable(self):
        '''
            Determina si el estado del proyecto permite modificaciones sobre los objetos dependientes
        '''
        return not self.estado.bloquea

    def get_usuarios(self):
        return list(Proyecto_Usuario.objects.filter(proyecto=self))

    def url_create():
        return reverse_lazy('seguimiento:create_proyecto')

    def url_detail(self):
        return reverse_lazy('seguimiento:detail_proyecto', kwargs={'pk': self.id})

    def url_update(self):
        return reverse_lazy('seguimiento:update_proyecto', kwargs={'pk': self.id})

    def url_delete(self):
        if Proyecto_Fase.objects.filter(proyecto=self).count()>0:
            return None
        return reverse_lazy('seguimiento:delete_proyecto', kwargs={'pk': self.id})

class Proyecto_Usuario(models.Model):
    id      = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    proyecto= models.ForeignKey(Proyecto, verbose_name=_('Proyecto'), on_delete=models.RESTRICT)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('Usuario'), on_delete=models.RESTRICT)  
    history = HistoricalRecords(excluded_fields=['creacion', 'actualizacion'], user_model=settings.AUTH_USER_MODEL)

    def __str__(self):
        return self.usuario

class Proyecto_Objetivo(models.Model):
    id      = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    descripcion = models.CharField(verbose_name=_('Descripción'), max_length=180, blank=True)
    alcanzado   = models.BooleanField(verbose_name=_('Alcanzado'), default=False)
    creacion= models.DateField(_('Creación'), auto_now_add=True)

    proyecto= models.ForeignKey(Proyecto, verbose_name=_('Proyecto'), on_delete=models.RESTRICT)

    history = HistoricalRecords(excluded_fields=['creacion', 'proyecto'], user_model=settings.AUTH_USER_MODEL)

    def __str__(self, max_length=60):
        return f'{self.proyecto}:{self.descripcion[:max_length]}...'

    def get_alcanzado(self):
        return _('Si') if self.alcanzado else _('No')

    def url_update(self):
        if self.proyecto.get_modificable() and not self.alcanzado:
            return reverse_lazy('seguimiento:update_proyectoobjetivo', kwargs={'pk': self.id})
        return None

    def url_delete(self):
        if self.proyecto.get_modificable() and not self.alcanzado:
            return reverse_lazy('seguimiento:delete_proyectoobjetivo', kwargs={'pk': self.id})
        return None

class Proyecto_Meta(models.Model):
    id      = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    descripcion = models.CharField(verbose_name=_('Descripción'), max_length=180, blank=True)
    alcanzado   = models.BooleanField(verbose_name=_('Alcanzado'), default=False)
    creacion= models.DateField(_('Creación'), auto_now_add=True)

    proyecto= models.ForeignKey(Proyecto, verbose_name=_('Proyecto'), on_delete=models.RESTRICT)

    history = HistoricalRecords(excluded_fields=['creacion', 'proyecto'], user_model=settings.AUTH_USER_MODEL)

    def __str__(self, max_length=60):
        return f'{self.proyecto}:{self.descripcion[:max_length]}...'

    def get_alcanzado(self):
        return _('Si') if self.alcanzado else _('No')

    def url_update(self):
        if self.proyecto.get_modificable() and not self.alcanzado:
            return reverse_lazy('seguimiento:update_proyectometa', kwargs={'pk': self.id})
        return None

    def url_delete(self):
        if self.proyecto.get_modificable() and not self.alcanzado:
            return reverse_lazy('seguimiento:delete_proyectometa', kwargs={'pk': self.id})
        return None

class Proyecto_Fase(models.Model):
    id      = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    correlativo = models.PositiveSmallIntegerField(verbose_name=_('Correlativo'))
    descripcion = models.CharField(verbose_name=_('Descripción'), max_length=180, blank=True)
    creacion= models.DateField(_('Creación'), auto_now_add=True)

    proyecto= models.ForeignKey(Proyecto, verbose_name=_('Proyecto'), on_delete=models.RESTRICT)

    history = HistoricalRecords(excluded_fields=['correlativo', 'creacion', 'proyecto'], user_model=settings.AUTH_USER_MODEL)
    
    class Meta:
        constraints = [
            UniqueConstraint(fields=['correlativo', 'proyecto'], name='unq_pf_correlativo_proyecto'),
            UniqueConstraint(fields=['descripcion', 'proyecto'], name='unq_pf_descripcion_proyecto'),
        ]

    def __str__(self, max_length=60):
        return f'{self.correlativo:02d}: {self.descripcion}'

    def get_porcentaje_completado(self):
        total_complejidad = Proyecto_Tarea.objects.filter(fase=self).aggregate(total=Sum('complejidad'))['total']
        total_completado = Proyecto_Tarea.objects.filter(fase=self).aggregate(total=Sum(F('complejidad')*F('finalizado')))['total']
        porcentaje = total_completado/total_complejidad if total_completado and total_complejidad > 0 else 0.0
        return round(porcentaje, 2)

    def get_todas_tareas(self):
        tareas_pendientes = Proyecto_Tarea.objects.filter(fase=self, finalizado__lt=100).annotate(custom_order=Value(1))
        tareas_finalizadas= Proyecto_Tarea.objects.filter(fase=self, finalizado=100).annotate(custom_order=Value(0))
        return tareas_pendientes.union(tareas_finalizadas).order_by('-custom_order', 'creacion')

    def url_update(self):
        if self.proyecto.get_modificable():
            return reverse_lazy('seguimiento:update_proyectofase', kwargs={'pk': self.id})
        return None

    def url_delete(self):
        tareas = Proyecto_Tarea.objects.filter(fase=self).count()
        if self.proyecto.get_modificable() and Proyecto_Tarea.objects.filter(fase=self).count()==0:
            return reverse_lazy('seguimiento:delete_proyectofase', kwargs={'pk': self.id})
        return None

class Proyecto_Tarea(models.Model):
    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    descripcion = models.CharField(verbose_name=_('Descripción'), max_length=180, blank=True)
    complejidad = models.PositiveSmallIntegerField(verbose_name=_('Complejidad'), default=1,
        validators=[ MaxValueValidator(100), MinValueValidator(1) ], help_text=_('Complejidad de 1 a 100'))
    creacion    = models.DateField(_('Creación'), auto_now_add=True)
    finalizado  = models.PositiveSmallIntegerField(verbose_name=_('% Completado'), default=0,
        validators=[ MaxValueValidator(100), MinValueValidator(0) ], help_text=_('Porcentaje de activdad completada de 0 - 100%'))

    fase    = models.ForeignKey(Proyecto_Fase, verbose_name=_('Fase'), on_delete=models.RESTRICT)

    history = HistoricalRecords(excluded_fields=['creacion', 'fase'], user_model=settings.AUTH_USER_MODEL)

    def __str__(self, max_length=60):
        return f'{self.descripcion}'

    def url_update(self):
        if self.finalizado<100 and self.fase.proyecto.get_modificable():
            return reverse_lazy('seguimiento:update_proyectotarea', kwargs={'pk': self.id})
        return None

    def url_delete(self):
        if self.finalizado<100 and self.fase.proyecto.get_modificable():
            return reverse_lazy('seguimiento:delete_proyectotarea', kwargs={'pk': self.id})
        return None

    @property
    def get_finalizado(self):
        return f'{self.finalizado}%'

class Comentario(models.Model):
    TIPO_COMENTARIO =[
        ('P', _('Proyecto')),
        ('T', _('Tarea')),
        ('F', _('Fase')),
    ]
    id      = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    descripcion = CKEditor5Field(verbose_name=_('Descripción'), blank=True, config_name='extends')
    creacion= models.DateField(_('Creación'), auto_now_add=True)
    tipo    = models.CharField(_('Tipo'), max_length=1, choices=TIPO_COMENTARIO, default='P')

    usuario    = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('Usuario'), on_delete=models.RESTRICT)
    proyecto= models.ForeignKey(Proyecto, verbose_name=_('Proyecto'), on_delete=models.RESTRICT)

    history = HistoricalRecords(excluded_fields=['creacion', 'usuario', 'proyecto'], user_model=settings.AUTH_USER_MODEL)

    def __str__(self, max_length=60):
        return f'{self.descripcion}'
