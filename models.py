import uuid
from datetime import date

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Max, Sum
from django.db.models.constraints import UniqueConstraint
from django.utils.translation import gettext as _
from django.urls import reverse_lazy

from django_ckeditor_5.fields import CKEditor5Field
from simple_history.models import HistoricalRecords

from usuarios.models import Usuario

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
    #descripcion = models.TextField(verbose_name=_('Descripción'), blank=True)
    descripcion = CKEditor5Field(verbose_name=_('Descripción'), blank=True, config_name='extends')
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

    def get_resumen(self, max_length=60):
        suspensivos = '...' if len(self.descripcion) > max_length else ''
        resumen = self.descripcion[:max_length].replace("\n", "")
        return f'{resumen}{suspensivos}'

    def get_modificable(self):
        '''
            Determina si el estado del proyecto permite modificaciones sobre los objetos dependientes
        '''
        return not self.estado.bloquea

    def get_max_fase(self):
        return Proyecto_Fase.objects.filter(proyecto=self).aggregate(max_fase_correlativo=Max('correlativo'))

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
        return f'{self.correlativo}: {self.descripcion}'

    def get_porcentaje_completado(self):
        total_complejidad = Proyecto_Tarea.objects.filter(fase=self).aggregate(total = Sum('complejidad'))['total']
        total_complejidad = total_complejidad if total_complejidad else 0
        total_completado = Proyecto_Tarea.objects.filter(fase=self, finalizado=True).aggregate(com = Sum('complejidad'))['com']
        total_completado = total_completado if total_completado else 0
        porcentaje = total_completado*100/total_complejidad if total_complejidad > 0 else 0.0
        return round(porcentaje, 2)

    def get_subtable(self):
        return Proyecto_Tarea.objects.filter(fase=self).order_by('finalizado', 'creacion')

    def url_update(self):
        if self.proyecto.get_modificable():
            return reverse_lazy('seguimiento:update_proyectofase', kwargs={'pk': self.id})
        return None

    def url_delete(self):
        if self.proyecto.get_modificable() and self.correlativo==self.proyecto.get_max_fase()['max_fase_correlativo']:
            return reverse_lazy('seguimiento:delete_proyectofase', kwargs={'pk': self.id})
        return None

class Proyecto_Tarea(models.Model):
    id      = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    descripcion = models.CharField(verbose_name=_('Descripción'), max_length=180, blank=True)
    complejidad = models.PositiveSmallIntegerField(verbose_name=_('Complejidad'), default=1,
        validators=[ MaxValueValidator(100), MinValueValidator(1) ])
    creacion= models.DateField(_('Creación'), auto_now_add=True)
    finalizado  = models.BooleanField(_('Finalizado'), default=False)

    fase    = models.ForeignKey(Proyecto_Fase, verbose_name=_('Fase'), on_delete=models.RESTRICT)

    history = HistoricalRecords(excluded_fields=['creacion', 'fase'], user_model=settings.AUTH_USER_MODEL)

    def __str__(self, max_length=60):
        return f'{self.descripcion}'

    def url_update(self):
        if not self.finalizado and self.fase.proyecto.get_modificable():
            return reverse_lazy('seguimiento:update_proyectotarea', kwargs={'pk': self.id})
        return None

    def url_delete(self):
        if not self.finalizado and self.fase.proyecto.get_modificable():
            return reverse_lazy('seguimiento:delete_proyectotarea', kwargs={'pk': self.id})
        return None

    @property
    def get_finalizado(self):
        return _('Finalizado') if self.finalizado else _('')

class Comentario(models.Model):
    id         = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    descripcion = CKEditor5Field(verbose_name=_('Descripción'), blank=True, config_name='extends')
    creacion= models.DateField(_('Creación'), auto_now_add=True)

    usuario    = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('Usuario'), on_delete=models.RESTRICT)
    proyecto= models.ForeignKey(Proyecto, verbose_name=_('Proyecto'), on_delete=models.RESTRICT)

    history = HistoricalRecords(excluded_fields=['creacion', 'usuario', 'proyecto'], user_model=settings.AUTH_USER_MODEL)

    def __str__(self, max_length=60):
        return f'{self.descripcion}'
