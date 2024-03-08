import uuid

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models.constraints import UniqueConstraint
from django.utils.translation import gettext as _
from django.urls import reverse_lazy

from django_ckeditor_5.fields import CKEditor5Field
from simple_history.models import HistoricalRecords

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
    ffin     = models.DateField(_('Fecha Fin'))

    estado  = models.ForeignKey(Estado, verbose_name=_('Estado'), on_delete=models.RESTRICT)
    history = HistoricalRecords(excluded_fields=['creacion', 'actualizacion'], user_model=settings.AUTH_USER_MODEL)

    def __str__(self):
        return self.nombre

    def get_resumen(self, max_length=60):
        return f'{self.descripcion[:max_length]}...'

    def url_create():
        return reverse_lazy('seguimiento:create_proyecto')

    def url_detail(self):
        return reverse_lazy('seguimiento:detail_proyecto', kwargs={'pk': self.id})

    def url_update(self):
        return reverse_lazy('seguimiento:update_proyecto', kwargs={'pk': self.id})

    def url_delete(self):
        if Proyecto_Objetivos.objects.filter(proyecto=self).count()>0:
            return None
        return reverse_lazy('seguimiento:delete_proyecto', kwargs={'pk': self.id})

class Proyecto_Objetivos(models.Model):
    id         = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    descripcion = models.TextField(verbose_name=_('Descripción'), blank=True)
    alcanzado     = models.BooleanField(verbose_name=_('Alcanzado'), default=False)
    creacion= models.DateField(_('Creación'), auto_now_add=True)

    proyecto= models.ForeignKey(Proyecto, verbose_name=_('Proyecto'), on_delete=models.RESTRICT)

    history = HistoricalRecords(excluded_fields=['creacion', 'proyecto'], user_model=settings.AUTH_USER_MODEL)

    def __str__(self, max_length=60):
        return f'{self.proyecto}:{self.descripcion[:max_length]}...'

class Proyecto_Metas(models.Model):
    id      = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    descripcion = models.TextField(verbose_name=_('Descripción'), blank=True)
    alcanzado     = models.BooleanField(verbose_name=_('Alcanzado'), default=False)
    creacion= models.DateField(_('Creación'), auto_now_add=True)

    proyecto= models.ForeignKey(Proyecto, verbose_name=_('Proyecto'), on_delete=models.RESTRICT)

    history = HistoricalRecords(excluded_fields=['creacion', 'proyecto'], user_model=settings.AUTH_USER_MODEL)

    def __str__(self, max_length=60):
        return f'{self.proyecto}:{self.descripcion[:max_length]}...'

class Proyecto_Fases(models.Model):
    id      = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    correlativo = models.PositiveSmallIntegerField(verbose_name=_('Correlativo'))
    descripcion = models.TextField(verbose_name=_('Descripción'), blank=True)
    creacion= models.DateField(_('Creación'), auto_now_add=True)

    estado  = models.ForeignKey(Estado, verbose_name=_('Estado'), on_delete=models.RESTRICT)
    proyecto= models.ForeignKey(Proyecto, verbose_name=_('Proyecto'), on_delete=models.RESTRICT)

    history = HistoricalRecords(excluded_fields=['correlativo', 'creacion', 'proyecto'], user_model=settings.AUTH_USER_MODEL)
    
    def __str__(self, max_length=60):
        return f'{self.correlativo}'

class Proyecto_Tareas(models.Model):
    id      = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    descripcion = models.TextField(verbose_name=_('Descripción'), blank=True)
    complejidad = models.PositiveSmallIntegerField(verbose_name=_('Complejidad'), default=1,
        validators=[ MaxValueValidator(100), MinValueValidator(1) ])
    creacion= models.DateField(_('Creación'), auto_now_add=True)

    estado  = models.ForeignKey(Estado, verbose_name=_('Estado'), on_delete=models.RESTRICT)
    fase     = models.ForeignKey(Proyecto_Fases, verbose_name=_('Fase'), on_delete=models.RESTRICT)

    history = HistoricalRecords(excluded_fields=['creacion', 'fase'], user_model=settings.AUTH_USER_MODEL)

    def __str__(self, max_length=60):
        return f'{self.descripcion}'

class Comentario(models.Model):
    id         = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    descripcion = CKEditor5Field(verbose_name=_('Descripción'), blank=True, config_name='extends')
    creacion= models.DateField(_('Creación'), auto_now_add=True)

    usuario    = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('Usuario'), on_delete=models.RESTRICT)
    proyecto= models.ForeignKey(Proyecto, verbose_name=_('Proyecto'), on_delete=models.RESTRICT)

    history = HistoricalRecords(excluded_fields=['creacion', 'usuario', 'proyecto'], user_model=settings.AUTH_USER_MODEL)

    def __str__(self, max_length=60):
        return f'{self.descripcion}'
