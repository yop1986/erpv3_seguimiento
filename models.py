import uuid
from datetime import date
from functools import reduce
from operator import add

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Max, Sum, Avg, F
from django.db.models.constraints import UniqueConstraint
from django.utils.translation import gettext as _
from django.urls import reverse_lazy

from django_ckeditor_5.fields import CKEditor5Field
from simple_history.models import HistoricalRecords

from usuarios.personal_views import Configuracion

conf = Configuracion()

class Estado(models.Model):
    id      = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    descripcion  = models.CharField(verbose_name=_('Descripción'), max_length=30, unique=True)
    bloquea = models.BooleanField(_('Bloquea modificaciones'), default=False, help_text=_('Determina si bloquea modificaciones'))
    vigente    = models.BooleanField(_('Estado'), default=True)
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

class Tipo_Proyecto(models.Model):
    id      = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre  = models.CharField(verbose_name=_('Nombre'), max_length=90, unique=True)
    vigente = models.BooleanField(verbose_name=_('Estado'), default=True)

    history = HistoricalRecords(excluded_fields=[], user_model=settings.AUTH_USER_MODEL)

    def __str__(self):
        return self.nombre

    def get_vigente(self):
        return _('Si') if self.vigente else _('No')

    def url_create():
        return reverse_lazy('seguimiento:create_tipo_proyecto')

    def url_detail(self):
        return reverse_lazy('seguimiento:detail_tipo_proyecto', kwargs={'pk': self.id})

    def url_update(self):
        return reverse_lazy('seguimiento:update_tipo_proyecto', kwargs={'pk': self.id})

    def url_delete(self):
        if Proyecto.objects.filter(tipo=self).count()>0:
            return None
        return reverse_lazy('seguimiento:delete_tipo_proyecto', kwargs={'pk': self.id})

class Origen_Proyecto(models.Model):
    id      = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre  = models.CharField(verbose_name=_('Nombre'), max_length=90, unique=True)
    vigente = models.BooleanField(verbose_name=_('Estado'), default=True)

    history = HistoricalRecords(excluded_fields=[], user_model=settings.AUTH_USER_MODEL)

    def __str__(self):
        return self.nombre

    def get_vigente(self):
        return _('Si') if self.vigente else _('No')

    def url_create():
        return reverse_lazy('seguimiento:create_origen_proyecto')

    def url_detail(self):
        return reverse_lazy('seguimiento:detail_origen_proyecto', kwargs={'pk': self.id})

    def url_update(self):
        return reverse_lazy('seguimiento:update_origen_proyecto', kwargs={'pk': self.id})

    def url_delete(self):
        if Proyecto.objects.filter(origen=self).count()>0:
            return None
        return reverse_lazy('seguimiento:delete_origen_proyecto', kwargs={'pk': self.id})

class PM_Proyecto(models.Model):
    id      = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre  = models.CharField(verbose_name=_('Nombre'), max_length=90, unique=True)
    vigente = models.BooleanField(verbose_name=_('Estado'), default=True)

    history = HistoricalRecords(excluded_fields=[], user_model=settings.AUTH_USER_MODEL)

    def __str__(self):
        return self.nombre

    def get_vigente(self):
        return _('Si') if self.vigente else _('No')

    def url_create():
        return reverse_lazy('seguimiento:create_pm_proyecto')

    def url_detail(self):
        return reverse_lazy('seguimiento:detail_pm_proyecto', kwargs={'pk': self.id})

    def url_update(self):
        return reverse_lazy('seguimiento:update_pm_proyecto', kwargs={'pk': self.id})

    def url_delete(self):
        if Proyecto.objects.filter(pm=self).count()>0:
            return None
        return reverse_lazy('seguimiento:delete_pm_proyecto', kwargs={'pk': self.id})

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

    lider   = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('Lider'), blank=True, null=True, on_delete=models.RESTRICT)
    estado  = models.ForeignKey(Estado, verbose_name=_('Estado'), on_delete=models.RESTRICT)
    tipo    = models.ForeignKey(Tipo_Proyecto, verbose_name=_('Tipo de proyecto'), blank=True, null=True, on_delete=models.RESTRICT)
    origen  = models.ForeignKey(Origen_Proyecto, verbose_name=_('Origen de proyecto'), blank=True, null=True, on_delete=models.RESTRICT)
    pm      = models.ForeignKey(PM_Proyecto, verbose_name=_('Project Manager'), blank=True, null=True, on_delete=models.RESTRICT)
    history = HistoricalRecords(excluded_fields=['creacion', 'actualizacion'], user_model=settings.AUTH_USER_MODEL)

    class Meta:
        permissions = [
            ("proyect_admin", "Ver todos los proyectos y agregar usuarios"),
            ("reportes", "Permite visualizar las opciones de reportería"),
        ]

    def __str__(self):
        return self.nombre

    def clean(self):
        errores = []
        if (self.finicio >= self.ffin):
            errores.append(ValidationError(_('La fecha de inicio debe ser menor a fecha de finalización'), code='fecha_invalida'))
        if errores:
            raise ValidationError(errores)

    @property
    def get_porcentaje_completado(self):
        try:
            tareas = Proyecto_Tarea.objects.filter(proyecto_actividad__isnull=True)
            queryset = Proyecto_Tarea.objects.filter(fase__proyecto=self).exclude(id__in=tareas)
            total_complejidad = queryset.aggregate(total=Sum('complejidad'))['total']
            total_completado    = reduce(add, [obj.complejidad * obj.finalizado for obj in queryset])
            porcentaje = total_completado/total_complejidad if total_completado and total_complejidad > 0 else 0.0
        except Exception as ex:
            print(f'error en Proyecto.get_porcentaje_completado: {ex}')
            porcentaje = 0
        return round(porcentaje, 4)

    def get_tipo_permiso(self):
        return _('Público') if self.publico else _('Privado')

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
        try:
            proy_expira = int(conf.get_value('seguimiento', 'proy_expira'))
        except Exception as ex:
            print(f'error en Proyecto.get_modificable: {ex}')
            proy_expira = False

        return not (proy_expira and self.ffin < date.today()) and not self.estado.bloquea

    def get_usuarios(self):
        return list(Proyecto_Usuario.objects.filter(proyecto=self))

    def url_create():
        return reverse_lazy('seguimiento:create_proyecto')

    def url_detail(self):
        return reverse_lazy('seguimiento:detail_proyecto', kwargs={'pk': self.id})

    def url_update(self):
        return reverse_lazy('seguimiento:update_proyecto', kwargs={'pk': self.id})

    def url_delete(self):
        if self.proyecto_fase_set.count() > 0:
            return None
        return reverse_lazy('seguimiento:delete_proyecto', kwargs={'pk': self.id})

class Proyecto_Usuario(models.Model):
    id      = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    proyecto= models.ForeignKey(Proyecto, verbose_name=_('Proyecto'), on_delete=models.RESTRICT)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('Usuario'), on_delete=models.RESTRICT)  
    history = HistoricalRecords(excluded_fields=[], user_model=settings.AUTH_USER_MODEL)

    def __str__(self):
        return self.usuario

class Proyecto_Objetivo(models.Model):
    id      = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    descripcion = models.CharField(verbose_name=_('Descripción'), max_length=180, blank=True)
    alcanzado   = models.BooleanField(verbose_name=_('Alcanzado'), default=False)
    creacion    = models.DateField(_('Creación'), auto_now_add=True)
    actualizacion   = models.DateTimeField(_('Actualización'), auto_now=True)

    proyecto= models.ForeignKey(Proyecto, verbose_name=_('Proyecto'), on_delete=models.RESTRICT)

    history = HistoricalRecords(excluded_fields=['creacion', 'proyecto', 'actualizacion'], user_model=settings.AUTH_USER_MODEL)

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
    creacion    = models.DateField(_('Creación'), auto_now_add=True)
    actualizacion   = models.DateTimeField(_('Actualización'), auto_now=True)

    proyecto= models.ForeignKey(Proyecto, verbose_name=_('Proyecto'), on_delete=models.RESTRICT)

    history = HistoricalRecords(excluded_fields=['creacion', 'proyecto', 'actualizacion'], user_model=settings.AUTH_USER_MODEL)

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
    descripcion = models.CharField(verbose_name=_('Descripción'), max_length=180)
    creacion= models.DateField(_('Creación'), auto_now_add=True)
    cerrado = models.BooleanField(_('Cerrado'), default=False, help_text=_('Cierra de forma definitiva la fase (impide asignar nuevas tareas)'))

    proyecto= models.ForeignKey(Proyecto, verbose_name=_('Proyecto'), on_delete=models.RESTRICT)

    history = HistoricalRecords(excluded_fields=['correlativo', 'creacion', 'proyecto'], user_model=settings.AUTH_USER_MODEL)
    
    class Meta:
        constraints = [
            UniqueConstraint(fields=['correlativo', 'proyecto'], name='unq_pf_correlativo_proyecto'),
            UniqueConstraint(fields=['descripcion', 'proyecto'], name='unq_pf_descripcion_proyecto'),
        ]

    def __str__(self, max_length=60):
        return f'{self.descripcion}'

    @property
    def get_porcentaje_completado(self):
        try:
            tareas = Proyecto_Tarea.objects.filter(proyecto_actividad__isnull=True)
            queryset = Proyecto_Tarea.objects.filter(fase=self).exclude(id__in=tareas)

            total_complejidad   = queryset.aggregate(total=Sum('complejidad'))['total']
            total_completado    = reduce(add, [obj.complejidad * obj.finalizado for obj in queryset])
            porcentaje = total_completado/total_complejidad if total_completado and total_complejidad > 0 else 0.0
        except Exception as ex:
            print(f'error en Proyecto_Fase.get_porcentaje_completado: {ex}')
            porcentaje = 0
        return round(porcentaje, 4)

    def url_update(self):
        if self.proyecto.get_modificable():
            return reverse_lazy('seguimiento:update_proyectofase', kwargs={'pk': self.id})
        return None

    def url_delete(self):
        if self.proyecto.get_modificable() and Proyecto_Tarea.objects.filter(fase=self).count()==0:
            return reverse_lazy('seguimiento:delete_proyectofase', kwargs={'pk': self.id})
        return None

class Proyecto_Tarea(models.Model):
    PRIORIDADES = [
        (10, 'Baja'),
        (20, 'Media'),
        (30, 'Alta'),
    ]
    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    descripcion = models.CharField(verbose_name=_('Descripción'), max_length=180)
    prioridad   = models.PositiveSmallIntegerField(default=10, choices=PRIORIDADES)
    complejidad = models.PositiveSmallIntegerField(verbose_name=_('Complejidad'), default=1,
        validators=[ MaxValueValidator(100), MinValueValidator(1) ], help_text=_('Complejidad de 1 a 100'))
    creacion    = models.DateField(_('Creación'), auto_now_add=True)
    actualizacion   = models.DateTimeField(_('Actualización'), auto_now=True)

    fase    = models.ForeignKey(Proyecto_Fase, verbose_name=_('Fase'), on_delete=models.RESTRICT)

    history = HistoricalRecords(excluded_fields=['creacion', 'fase', 'actualizacion'], user_model=settings.AUTH_USER_MODEL)

    def __str__(self, max_length=60):
        return f'{self.descripcion}'
    
    def url_proyecto(self):
        return reverse_lazy('seguimiento:detail_proyecto', kwargs={'pk': self.fase.proyecto.id})

    def url_detail(self):
        fase = self.fase
        return reverse_lazy('seguimiento:detail_proyecto', kwargs={'pk': fase.proyecto.id, 'faseactiva': fase.id})
        
    def url_update(self):
        if self.fase.proyecto.get_modificable():
            return reverse_lazy('seguimiento:update_proyectotarea', kwargs={'pk': self.id})
        return None

    def url_delete(self):
        if Proyecto_Actividad.objects.filter(tarea=self).count()==0 and self.fase.proyecto.get_modificable():
            return reverse_lazy('seguimiento:delete_proyectotarea', kwargs={'pk': self.id})
        return None

    def get_cantidad_actividades(self):
        return Proyecto_Actividad.objects.filter(tarea=self).count()

    def get_actividades(self):
        return Proyecto_Actividad.objects.filter(tarea=self).order_by('finalizado', 'creacion')

    def get_full_parent(self):
        return f'{self.fase.proyecto} > {self.fase.correlativo:02d}: {self.fase.descripcion}'
    
    def get_imagen(self):
        if self.finalizado==100:
            return 'seguimiento_tarea_finalizada.png'
        else: 
            return f'seguimiento_prioridad_{self.prioridad}.png'

    @property
    def finalizado(self):
        if Proyecto_Actividad.objects.filter(tarea=self).count()==0:
            return 0
        return Proyecto_Actividad.objects.filter(tarea=self).aggregate(Avg('finalizado'))['finalizado__avg']

    @property
    def get_prioridad(self):
        return self.get_prioridad_display()

class Proyecto_Actividad(models.Model):
    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    descripcion = models.CharField(verbose_name=_('Descripción'), max_length=180)
    resolucion  = CKEditor5Field(verbose_name=_('Resolución'), blank=True, config_name='extends')
    creacion    = models.DateField(_('Creación'), auto_now_add=True)
    actualizacion   = models.DateTimeField(_('Actualización'), auto_now=True)
    finalizado  = models.PositiveSmallIntegerField(verbose_name=_('% Completado'), default=0,
        validators=[ MaxValueValidator(100), MinValueValidator(0) ], help_text=_('Porcentaje de activdad completada de 0 - 100%'))

    responsable = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('Responsable'), null=True, blank=True, on_delete=models.RESTRICT)
    tarea       = models.ForeignKey(Proyecto_Tarea, verbose_name=_('Tarea'), on_delete=models.RESTRICT)

    history = HistoricalRecords(excluded_fields=['tarea', 'creacion', 'actualizacion'], user_model=settings.AUTH_USER_MODEL)

    def __str__(self, max_length=60):
        return f'{self.descripcion}'

    def url_update(self):
        if self.tarea.fase.proyecto.get_modificable():
            return reverse_lazy('seguimiento:update_proyectoactividad', kwargs={'pk': self.id})
        return None

    def url_delete(self):
        if self.tarea.fase.proyecto.get_modificable():
            return reverse_lazy('seguimiento:delete_proyectoactividad', kwargs={'pk': self.id})
        return None

class Comentario(models.Model):
    TIPO_COMENTARIO =[
        ('P', _('Proyecto')),
        ('T', _('Tarea')),
        ('F', _('Fase')),
        ('A', _('Activdad')),
    ]
    id      = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    descripcion = CKEditor5Field(verbose_name=_('Descripción'), blank=True, config_name='extends')
    creacion= models.DateTimeField(_('Creación'), auto_now_add=True)
    tipo    = models.CharField(_('Tipo'), max_length=1, choices=TIPO_COMENTARIO, default='P')
    obj_id  = models.CharField(_('Objeto'), max_length=36, default='', blank=True)

    usuario    = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('Usuario'), on_delete=models.RESTRICT)

    def __str__(self, max_length=60):
        return f'({ self.get_objeto() }) { self.descripcion }'

    def url_detail(self):
        if self.tipo == 'P':
            return reverse_lazy('seguimiento:detail_proyecto', kwargs={'pk': self.obj_id})
        if self.tipo == 'F':
            fase = Proyecto_Fase.objects.get(id = self.obj_id)
            return reverse_lazy('seguimiento:detail_proyecto', kwargs={'pk': fase.proyecto.id, 'faseactiva': fase.id})
        if self.tipo == 'T':
            fase = Proyecto_Tarea.objects.get(id = self.obj_id).fase
            return reverse_lazy('seguimiento:detail_proyecto', kwargs={'pk': fase.proyecto.id, 'faseactiva': fase.id})
        if self.tipo == 'A':
            fase = Proyecto_Actividad.objects.get(id = self.obj_id).tarea.fase
            return reverse_lazy('seguimiento:detail_proyecto', kwargs={'pk': fase.proyecto.id, 'faseactiva': fase.id})
        return None


    def get_objeto(self):
        if self.tipo == 'P':
            return _('Proyecto: ') + f'{Proyecto.objects.get(id = self.obj_id)}'
        elif self.tipo == 'F':
            return _('Fase: ') + f'{Proyecto_Fase.objects.get(id = self.obj_id)}'
        elif self.tipo == 'T':
            return _('Tarea: ') + f'{Proyecto_Tarea.objects.get(id = self.obj_id)}'
        elif self.tipo == 'A':
            return _('Actividad: ') + f'{Proyecto_Actividad.objects.get(id = self.obj_id)}'
        else:
            return None


