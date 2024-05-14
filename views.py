# https://xlsxwriter.readthedocs.io/
import io, xlsxwriter, html2text
from datetime import date
from itertools import chain

from django.apps import apps
from django.contrib import messages
from django.db.models import Q, Count, Case, When, BooleanField
from django.http import FileResponse, HttpResponseRedirect #, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _
from django.views.generic.base import TemplateView

from usuarios.models import Usuario
from usuarios.personal_views import (PersonalContextMixin, PersonalCreateView, 
    PersonalUpdateView, PersonalListView, PersonalDetailView, PersonalDeleteView, 
    PersonalFormView, Configuracion)

from .models import (Estado, Tipo_Proyecto, Origen_Proyecto, PM_Proyecto, Proyecto, Proyecto_Objetivo, 
    Proyecto_Meta, Proyecto_Fase, Proyecto_Tarea, Proyecto_Actividad, Proyecto_Usuario, 
    Proyecto_Etiqueta, Comentario)
from .forms import (ProyectoForm, Proyecto_Objetivo_ModelForm, Proyecto_Meta_ModelForm,
    Proyecto_Fase_ModelForm, Proyecto_Tarea_ModelForm, Proyecto_Usuario_ModelForm, 
    Proyecto_Etiqueta_ModelForm, Proyecto_Comentario_ModelForm, Proyecto_Actividad_ModelForm, 
    Proyecto_Reporte_Avances, Proyecto_Reportes_Actividades)

#gConfiguracion = Configuracion()

DISPLAYS = {
    'forms': {
        'submit': _('Guardar'),
        'cancel': _('Cancelar'),
    },
    'delete_form': {
        'confirmacion': _('¿Esta seguro de eliminar el elemento indicado?'),
        'submit': _('Eliminar'),
        'cancel': _('Cancelar'),
    },
    'opciones': {
        'detail': _('Ver'),
        'detail_img': 'seguimiento_detail.png',
        'update': _('Editar'),
        'update_img': 'seguimiento_update.png',
        'delete': _('Eliminar'),
        'delete_img': 'seguimiento_delete.png',
    },
    'tabla_vacia': _('No hay elementos para mostrar'),
}

class SeguimientoContextMixin(PersonalContextMixin):
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['general']['menu_app'] = apps.get_app_config(__package__).name +'_menu.html'
        return context 

class IndexTemplateView(TemplateView, SeguimientoContextMixin):
    template_name = 'template/index.html'

    extra_context ={
        'title': _('Seguimiento'),
        'elementos': [
            {
                'display':  _('Proyecto'),
                'desc':     _('Agrupación de actividades por proyecto, medicion de \
                	avances y control sobre las tareas.'),
                'imagen':   _('seguimiento_proyecto.png'),
            },
            {
                'display':  _('Objetivos y metas'),
                'desc':     _('Definición de objetivos y metas esperadas para el proyecto.'),
                'imagen':   _('seguimiento_obj_meta.png'),
            },
            {
                'display':  _('Fase'),
                'desc':     _('Creación de fases para segmentar la forma de trabajo.'),
                'imagen':   _('seguimiento_fase.png'),
            },
            {
                'display':  _('Tareas'),
                'desc':     _('Definicion de tareas y su ponderación por complejidad  \
                	para una estimación mas apropiada.'),
                'imagen':   _('seguimiento_tarea.png'),
            },            
            {	'display':  _('Comentarios'),
                'desc':     _('Comentarios generales del proyecto, permite mantener \
                	al día sobre los pormenores.'),
                'imagen':   _('seguimiento_comentario.png'),
            },
        ],
    }


class EstadoListView(PersonalListView, SeguimientoContextMixin):
    permission_required = 'seguimiento.view_estado'
    template_name = 'template/list.html'
    model = Estado
    ordering = ['-vigente', 'descripcion']
    paginate_by = 10
    extra_context = {
        'title': _('Estados'),
        'create' :{
            'display':  _('Nuevo'),
            'url':      Estado.url_create(),
            'img':      'seguimiento_add.png',
        },
        'campos': {
            'enumerar': 1,
            'lista': [
                'descripcion', 
                'actualizacion', 
            ],
            'opciones': _('Opciones'),
        },
        'campos_extra': [
            { 'nombre': _('Bloquea'), 'funcion': 'get_bloquea' },
            { 'nombre':   _('Vigente'), 'funcion': 'get_vigente' },
        ],
        'opciones': DISPLAYS['opciones'],
        'mensaje': {
            'vacio': DISPLAYS['tabla_vacia'],
        },
    }

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['permisos'] = {
            'create': self.request.user.has_perm('seguimiento.add_estado'),
            'update': self.request.user.has_perm('seguimiento.change_estado'),
            'delete': self.request.user.has_perm('seguimiento.delete_estado'),
        }
        return context

class EstadoCreateView(PersonalCreateView, SeguimientoContextMixin):
    permission_required = 'seguimiento.add_estado'
    template_name = 'template/forms.html'
    model = Estado
    fields = ['descripcion', 'bloquea']
    #form_class = 
    success_url = reverse_lazy('seguimiento:list_estado')
    extra_context = {
        'title': _('Nuevo Estado'),
        'opciones': DISPLAYS['forms'],
    }

class EstadoDetailView(PersonalDetailView, SeguimientoContextMixin):
    permission_required = 'seguimiento.view_estado'
    template_name = 'template/detail.html'
    model = Estado
    extra_context = {
        'title': _('Estado'),
        'campos': {
            'lista': [ 'descripcion', 'actualizacion', ],
            'opciones': _('Opciones'),
        },
        'campos_extra': [ 
            {'nombre':   _('Bloquea'), 'funcion': 'get_bloquea'},
            {'nombre': _('Vigente'), 'funcion': 'get_vigente'},
        ],
        'opciones': DISPLAYS['opciones'],
    }

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['permisos'] = {
            'update': self.request.user.has_perm('seguimiento.change_estado'),
            'delete': self.request.user.has_perm('seguimiento.delete_estado'),
        }
        
        if self.request.user.has_perm('seguimiento.view_proyecto'):   
            context['tables'] = [
                {
                    'title':        _('Proyectos'),
                    'object_list':  Proyecto.objects.filter(estado=self.object).order_by('actualizacion'),
                    'enumerar':     1,
                    'lista':       ['nombre', 'actualizacion'],
                    'opciones':     _('Opciones'),
                    'permisos': {
                        'update':   self.request.user.has_perm('seguimiento.change_proyecto'),
                        'delete':   self.request.user.has_perm('seguimiento.delete_proyecto'),
                    },
                    'next':         self.object.url_detail(),
                },
            ]
        return context

class EstadoUpdateView(PersonalUpdateView, SeguimientoContextMixin):
    permission_required = 'seguimiento.change_estado'
    template_name = 'template/forms.html'
    model = Estado
    fields = ['descripcion', 'bloquea', 'vigente']
    extra_context = {
        'title': _('Modificar Estado'),
        'opciones': DISPLAYS['forms'],
    }

    def get_success_url(self):
        return self.object.url_detail()

class EstadoDeleteView(PersonalDeleteView, SeguimientoContextMixin):
    permission_required = 'qliksense.delete_estado'
    template_name = 'template/delete_confirmation.html'
    model = Estado
    success_url = reverse_lazy('seguimiento:list_estado')
    extra_context = {
        'title': _('Eliminar estado'),
        'opciones': DISPLAYS['delete_form'],
    }



class Tipo_ProyectoListView(PersonalListView, SeguimientoContextMixin):
    permission_required = 'seguimiento.view_tipo_proyecto'
    template_name = 'template/list.html'
    model = Tipo_Proyecto
    ordering = ['-vigente', 'nombre']
    paginate_by = 10
    extra_context = {
        'title': _('Tipo de proyecto'),
        'create' :{
            'url':      Tipo_Proyecto.url_create(),
            'display':  _('Nuevo'),
            'img':      'seguimiento_add.png',
        },
        'campos': {
            'enumerar': 1,
            'lista': [
                'nombre', 
            ],
            'opciones': _('Opciones'),
        },
        'campos_extra': [
            { 'nombre':   _('Vigente'), 'funcion': 'get_vigente', },
        ],
        'opciones': DISPLAYS['opciones'],
        'mensaje': {
            'vacio': DISPLAYS['tabla_vacia'],
        },
    }

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['permisos'] = {
            'create': self.request.user.has_perm('seguimiento.add_tipo_proyecto'),
            'update': self.request.user.has_perm('seguimiento.change_tipo_proyecto'),
            'delete': self.request.user.has_perm('seguimiento.delete_tipo_proyecto'),
        }
        return context

class Tipo_ProyectoCreateView(PersonalCreateView, SeguimientoContextMixin):
    permission_required = 'seguimiento.add_tipo_proyecto'
    template_name = 'template/forms.html'
    model = Tipo_Proyecto
    fields = ['nombre']
    #form_class = 
    success_url = reverse_lazy('seguimiento:list_tipo_proyecto')
    extra_context = {
        'title': _('Nuevo tipo de proyecto'),
        'opciones': DISPLAYS['forms'],
    }

class Tipo_ProyectoDetailView(PersonalDetailView, SeguimientoContextMixin):
    permission_required = 'seguimiento.view_tipo_proyecto'
    template_name = 'template/detail.html'
    model = Tipo_Proyecto
    extra_context = {
        'title': _('Tipo de proyecto'),
        'campos': {
            'lista': [ 'nombre', ],
            'opciones': _('Opciones'),
        },
        'campos_extra': [
            { 'nombre': _('Vigente'), 'funcion': 'get_vigente' },
        ],
        'opciones': DISPLAYS['opciones'],
    }

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['permisos'] = {
            'create': self.request.user.has_perm('seguimiento.add_tipo_proyecto'),
            'update': self.request.user.has_perm('seguimiento.change_tipo_proyecto'),
            'delete': self.request.user.has_perm('seguimiento.delete_tipo_proyecto'),
        }
        
        if self.request.user.has_perm('seguimiento.view_proyecto'):   
            context['tables'] = [
                {
                    'title':        _('Proyectos'),
                    'object_list':  Proyecto.objects.filter(tipo=self.object).order_by('actualizacion'),
                    'enumerar':     1,
                    'lista':       [ 'nombre', 'actualizacion', ],
                    'opciones':     _('Opciones'),
                    'permisos': {
                        'update':   self.request.user.has_perm('seguimiento.change_proyecto'),
                        'delete':   self.request.user.has_perm('seguimiento.delete_proyecto'),
                    },
                    'next':         self.object.url_detail(),
                },
            ]
        return context

class Tipo_ProyectoUpdateView(PersonalUpdateView, SeguimientoContextMixin):
    permission_required = 'seguimiento.change_tipo_proyecto'
    template_name = 'template/forms.html'
    model = Tipo_Proyecto
    fields = ['nombre', 'vigente']
    extra_context = {
        'title': _('Modificar tipo de proyecto'),
        'opciones': DISPLAYS['forms'],
    }

    def get_success_url(self):
        return self.object.url_detail()

class Tipo_ProyectoDeleteView(PersonalDeleteView, SeguimientoContextMixin):
    permission_required = 'qliksense.delete_tipo_proyecto'
    template_name = 'template/delete_confirmation.html'
    model = Tipo_Proyecto
    success_url = reverse_lazy('seguimiento:list_tipo_proyecto')
    extra_context = {
        'title': _('Eliminar tipo de proyecto'),
        'opciones': DISPLAYS['delete_form'],
    }



class Origen_ProyectoListView(PersonalListView, SeguimientoContextMixin):
    permission_required = 'seguimiento.view_origen_proyecto'
    template_name = 'template/list.html'
    model = Origen_Proyecto
    ordering = ['-vigente', 'nombre']
    paginate_by = 10
    extra_context = {
        'title': _('Origen de proyectos'),
        'create' :{
            'url':      Origen_Proyecto.url_create(),
            'display':  _('Nuevo'),
            'img':      'seguimiento_add.png',
        },
        'campos': {
            'enumerar': 1,
            'lista': [ 'nombre', ],
            'opciones': _('Opciones'),
        },
        'campos_extra': [
            { 'nombre':   _('Vigente'), 'funcion': 'get_vigente', },
            
        ],
        'opciones': DISPLAYS['opciones'],
        'mensaje': {
            'vacio': DISPLAYS['tabla_vacia'],
        },
    }

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['permisos'] = {
            'create': self.request.user.has_perm('seguimiento.add_origen_proyecto'),
            'update': self.request.user.has_perm('seguimiento.change_origen_proyecto'),
            'delete': self.request.user.has_perm('seguimiento.delete_origen_proyecto'),
        }
        return context

class Origen_ProyectoCreateView(PersonalCreateView, SeguimientoContextMixin):
    permission_required = 'seguimiento.add_origen_proyecto'
    template_name = 'template/forms.html'
    model = Origen_Proyecto
    fields = ['nombre']
    #form_class = 
    success_url = reverse_lazy('seguimiento:list_origen_proyecto')
    extra_context = {
        'title': _('Nuevo origen de proyecto'),
        'opciones': DISPLAYS['forms'],
    }

class Origen_ProyectoDetailView(PersonalDetailView, SeguimientoContextMixin):
    permission_required = 'seguimiento.view_origen_proyecto'
    template_name = 'template/detail.html'
    model = Origen_Proyecto
    extra_context = {
        'title': _('Origen de proyecto'),
        'campos': {
            'lista': [ 'nombre', ],
            'opciones': _('Opciones'),
        },
        'campos_extra': [ 
            { 'nombre': _('Vigente'), 'funcion': 'get_vigente'},
        ],
        'opciones': DISPLAYS['opciones'],
    }

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['permisos'] = {
            'update': self.request.user.has_perm('seguimiento.change_origen_proyecto'),
            'delete': self.request.user.has_perm('seguimiento.delete_origen_proyecto'),
        }
        
        if self.request.user.has_perm('seguimiento.view_proyecto'):   
            context['tables'] = [
                {
                    'title':        _('Proyectos'),
                    'object_list':  Proyecto.objects.filter(origen=self.object).order_by('actualizacion'),
                    'enumerar':     1,
                    'lista':        ['nombre', 'actualizacion'],
                    'opciones':     _('Opciones'),
                    'permisos': {
                        'update':   self.request.user.has_perm('seguimiento.change_proyecto'),
                        'delete':   self.request.user.has_perm('seguimiento.delete_proyecto'),
                    },
                    'next':         self.object.url_detail(),
                },
            ]
        return context

class Origen_ProyectoUpdateView(PersonalUpdateView, SeguimientoContextMixin):
    permission_required = 'seguimiento.change_origen_proyecto'
    template_name = 'template/forms.html'
    model = Origen_Proyecto
    fields = ['nombre', 'vigente']
    extra_context = {
        'title': _('Modificar origen de proyecto'),
        'opciones': DISPLAYS['forms'],
    }

    def get_success_url(self):
        return self.object.url_detail()

class Origen_ProyectoDeleteView(PersonalDeleteView, SeguimientoContextMixin):
    permission_required = 'qliksense.delete_origen_proyecto'
    template_name = 'template/delete_confirmation.html'
    model = Origen_Proyecto
    success_url = reverse_lazy('seguimiento:list_origen_proyecto')
    extra_context = {
        'title': _('Eliminar origen de proyecto'),
        'opciones': DISPLAYS['delete_form'],
    }



class PM_ProyectoListView(PersonalListView, SeguimientoContextMixin):
    permission_required = 'seguimiento.view_pm_proyecto'
    template_name = 'template/list.html'
    model = PM_Proyecto
    ordering = ['-vigente', 'nombre']
    paginate_by = 10
    extra_context = {
        'title': _('Project Manager'),
        'create' :{
            'url':      PM_Proyecto.url_create(),
            'display':  _('Nuevo'),
            'img':      'seguimiento_add.png',
        },
        'campos': {
            'enumerar': 1,
            'lista': [ 'nombre', ],
            'opciones': _('Opciones'),
        },
        'campos_extra': [
            { 'nombre':   _('Vigente'), 'funcion': 'get_vigente', },
        ],
        'opciones': DISPLAYS['opciones'],
        'mensaje': {
            'vacio': DISPLAYS['tabla_vacia'],
        },
    }

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['permisos'] = {
            'create': self.request.user.has_perm('seguimiento.add_pm_proyecto'),
            'update': self.request.user.has_perm('seguimiento.change_pm_proyecto'),
            'delete': self.request.user.has_perm('seguimiento.delete_pm_proyecto'),
        }
        return context

class PM_ProyectoCreateView(PersonalCreateView, SeguimientoContextMixin):
    permission_required = 'seguimiento.add_pm_proyecto'
    template_name = 'template/forms.html'
    model = PM_Proyecto
    fields = ['nombre']
    #form_class = 
    success_url = reverse_lazy('seguimiento:list_pm_proyecto')
    extra_context = {
        'title': _('Nuevo origen de proyecto'),
        'opciones': DISPLAYS['forms'],
    }

class PM_ProyectoDetailView(PersonalDetailView, SeguimientoContextMixin):
    permission_required = 'seguimiento.view_pm_proyecto'
    template_name = 'template/detail.html'
    model = PM_Proyecto
    extra_context = {
        'title': _('Origen de proyecto'),
        'campos': {
            'lista': [ 'nombre', ],
            'opciones': _('Opciones'),
        },
        'campos_extra': [ 
            { 'nombre': _('Vigente'), 'funcion': 'get_vigente', },
        ],
        'opciones': DISPLAYS['opciones'],
    }

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['permisos'] = {
            'update': self.request.user.has_perm('seguimiento.change_pm_proyecto'),
            'delete': self.request.user.has_perm('seguimiento.delete_pm_proyecto'),
        }
        
        if self.request.user.has_perm('seguimiento.view_proyecto'):   
            context['tables'] = [
                {
                    'title':        _('Proyectos'),
                    'object_list':  Proyecto.objects.filter(pm=self.object).order_by('actualizacion'),
                    'enumerar':     1,
                    'lista':       ['nombre', 'actualizacion'],
                    'opciones':     _('Opciones'),
                    'permisos': {
                        'update':   self.request.user.has_perm('seguimiento.change_proyecto'),
                        'delete':   self.request.user.has_perm('seguimiento.delete_proyecto'),
                    },
                    'next':         self.object.url_detail(),
                },
            ]
        return context

class PM_ProyectoUpdateView(PersonalUpdateView, SeguimientoContextMixin):
    permission_required = 'seguimiento.change_pm_proyecto'
    template_name = 'template/forms.html'
    model = PM_Proyecto
    fields = ['nombre', 'vigente']
    extra_context = {
        'title': _('Modificar origen de proyecto'),
        'opciones': DISPLAYS['forms'],
    }

    def get_success_url(self):
        return self.object.url_detail()

class PM_ProyectoDeleteView(PersonalDeleteView, SeguimientoContextMixin):
    permission_required = 'qliksense.delete_pm_proyecto'
    template_name = 'template/delete_confirmation.html'
    model = PM_Proyecto
    success_url = reverse_lazy('seguimiento:list_pm_proyecto')
    extra_context = {
        'title': _('Eliminar origen de proyecto'),
        'opciones': DISPLAYS['delete_form'],
    }



class ProyectoListView(PersonalListView, SeguimientoContextMixin):
    permission_required = 'seguimiento.view_proyecto'
    template_name = 'template/list.html'
    model = Proyecto
    ordering = ['estado__bloquea', 'nombre']
    paginate_by = 15
    extra_context = {
        'title': _('Proyectos'),
        'create' :{
            'url':      Proyecto.url_create(),
            'display':  _('Nuevo'),
            'img':      'seguimiento_add.png',
        },
        'campos': {
            'enumerar': 1,
            'lista': [ 'nombre', 'estado', ],
            'opciones': _('Opciones'),
        },
        'campos_extra': [
            { 'nombre': _('Periodo'), 'funcion': 'get_periodo', },
            { 'nombre':   _('Resumen'), 'funcion': 'get_resumen', },
        ],
        'opciones': DISPLAYS['opciones'],
        'mensaje': {
            'vacio': DISPLAYS['tabla_vacia'],
        },
    }

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.has_perm('seguimiento.proyect_admin'):
            return queryset.select_related('estado')
        proys = Proyecto_Usuario.objects.filter(usuario=self.request.user.id).values_list('proyecto')
        return queryset.select_related('estado').filter(Q(publico=True)|Q(id__in=proys))

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['permisos'] = {
            'create': self.request.user.has_perm('seguimiento.add_proyecto'),
            'update': self.request.user.has_perm('seguimiento.change_proyecto'),
            'delete': self.request.user.has_perm('seguimiento.delete_proyecto'),
        }
        return context

class ProyectoCreateView(PersonalCreateView, SeguimientoContextMixin):
    permission_required = 'seguimiento.add_proyecto'
    template_name = 'template/forms.html'
    model = Proyecto
    #fields = []
    form_class = ProyectoForm
    success_url = reverse_lazy('seguimiento:list_proyecto')
    extra_context = {
        'title': _('Nuevo Proyecto'),
        'opciones': DISPLAYS['forms'],
    }

    def form_valid(self, form):
        self.object = form.save()
        Proyecto_Usuario(proyecto=self.object, usuario=self.request.user).save()
        return redirect('seguimiento:detail_proyecto', pk=self.object.id)

class ProyectoDetailView(PersonalDetailView, SeguimientoContextMixin):
    permission_required = 'seguimiento.view_proyecto'
    template_name = 'seguimiento/detail.html'
    model = Proyecto
    extra_context = {
        'title': _('Proyecto'),
        'campos': {
            'lista': [ 'nombre', 'lider', 'estado', 'tipo', 
                'origen', 'pm', ],
            'opciones': _('Opciones'),
        },
        'opciones': DISPLAYS['opciones'],
    }

    def get_queryset(self, *args, **kwargs):
        queryset = super().get_queryset()
        queryset = queryset.select_related('estado').select_related('tipo')\
            .select_related('lider').select_related('origen').select_related('pm')\
            .filter(id = self.kwargs['pk'])
        if self.request.user.has_perm('seguimiento.proyect_admin') or queryset.filter(publico=True) or \
            Proyecto_Usuario.objects.filter(usuario=self.request.user, proyecto_id=self.kwargs['pk']).count():
            return queryset
        return None

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        estado_bloqueado = self.object.estado.bloquea

        context['faseactiva'] = self.kwargs['faseactiva'] if 'faseactiva' in self.kwargs else None
        context['opcion'] = self.kwargs['opcion'] if 'opcion' in self.kwargs else None
        context['campos_extra'] = [
            { 'nombre': _('Periodo'), 'funcion': 'get_periodo' },
            { 'nombre': _('Publico'), 'funcion': 'get_tipo_permiso', },
            { 'nombre': _('Completado'), 'porcentaje': self.object.get_porcentaje_completado, },
        ]
        context['permisos'] = {
            'bloqueado': estado_bloqueado,
            'update': self.request.user.has_perm('seguimiento.change_proyecto'),
            'delete': self.request.user.has_perm('seguimiento.delete_proyecto'),
        }
        
        botones = []
        if self.object.get_have_url():
            botones.append({ 
                'permiso': True,  
                'url': self.object.enlace_cloud,
                'display': 'Cloud',
                'img': 'seguimiento_cloud.png',
                'target': '_blank',
            })
        if self.request.user.has_perm('seguimiento.view_comentario'):
            botones.append({   
                'permiso': self.request.user.has_perm('seguimiento.view_comentario'),
                'url': reverse_lazy('seguimiento:list_comentario', kwargs={'pk': self.object.id}),
                'display': 'Ver comentarios',
                'img': 'seguimiento_comentario.png',
                'target': '_blank',
            })
        context['botones_extra'] = botones
        
        formularios = []
        if self.request.user.has_perm('seguimiento.add_proyecto_objetivo'):
            formularios.append({
                            'modal':    'proyecto_objetivo', 
                            'display':  _('Definición de objetivos'),
                            'link_img': 'seguimiento_objetivo_add.png',
                            'action':   reverse_lazy('seguimiento:create_proyectoobjetivo')+'?next='+self.object.url_detail(),
                            'form':     Proyecto_Objetivo_ModelForm('proyecto', instance=Proyecto_Objetivo(proyecto=self.object)),
                            'opciones': DISPLAYS['forms'],
                        })
        if self.request.user.has_perm('seguimiento.add_proyecto_meta'):
            formularios.append({
                            'modal':    'proyecto_meta', 
                            'display':  _('Definición de metas'),
                            'link_img': 'seguimiento_meta_add.png',
                            'action':   reverse_lazy('seguimiento:create_proyectometa')+'?next='+self.object.url_detail(),
                            'form':     Proyecto_Meta_ModelForm('proyecto', instance=Proyecto_Meta(proyecto=self.object)),
                            'opciones': DISPLAYS['forms'],
                        })
        if self.request.user.has_perm('seguimiento.add_proyecto_fase'):
            formularios.append({
                            'modal':    'proyecto_fase', 
                            'display':  _('Definición de fases'),
                            'link_img': 'seguimiento_fase_add.png',
                            'action':   reverse_lazy('seguimiento:create_proyectofase')+'?next='+self.object.url_detail(),
                            'form':     Proyecto_Fase_ModelForm('proyecto', instance=Proyecto_Fase(proyecto=self.object)),
                            'opciones': DISPLAYS['forms'],
                        })
        if self.request.user.has_perm('seguimiento.add_proyecto_tarea'):
            formularios.append({
                            'modal':    'proyecto_tarea', 
                            'display':  _('Definición de tareas'),
                            'link_img': 'seguimiento_tarea_add.png',
                            'action':   reverse_lazy('seguimiento:create_proyectotarea'),
                            'form':     Proyecto_Tarea_ModelForm('nuevo', self.object),
                            'opciones': DISPLAYS['forms'],
                        })
        if self.request.user.has_perm('seguimiento.add_proyecto_actividad'):
            formularios.append({
                            'modal':    'proyecto_actividad', 
                            'display':  _('Definición de actividades'),
                            'link_img': 'seguimiento_actividad.png',
                            'action':   reverse_lazy('seguimiento:create_proyectoactividad'),
                            'form':     Proyecto_Actividad_ModelForm(self.object),
                            'opciones': DISPLAYS['forms'],
                        })
        if self.request.user.has_perm('seguimiento.proyect_admin'):
            formularios.append({
                            'modal':    'proyecto_usuario', 
                            'display':  _('Agregar usuario al proyecto'),
                            'link_img': 'seguimiento_add_usuario.png',
                            'action':   reverse_lazy('seguimiento:create_proyectousuario')+'?next='+self.object.url_detail(),
                            'form':     Proyecto_Usuario_ModelForm('proyecto', instance=Proyecto_Objetivo(proyecto=self.object)),
                            'opciones': DISPLAYS['forms'],
                        })
        if self.request.user.has_perm('seguimiento.add_proyecto_etiqueta'):
            formularios.append({
                            'modal':    'proyecto_etiqueta', 
                            'display':  _('Agregar etiqueta al proyecto'),
                            'link_img': 'seguimiento_add_etiqueta.png',
                            'action':   reverse_lazy('seguimiento:create_proyectoetiqueta')+'?next='+self.object.url_detail(),
                            'form':     Proyecto_Etiqueta_ModelForm('proyecto', instance=Proyecto_Etiqueta(proyecto=self.object)),
                            'opciones': DISPLAYS['forms'],
                        })
        if self.request.user.has_perm('seguimiento.add_comentario'):
            formularios.append({
                            'modal':    'comentario',
                            'display':  _('Comentario'),
                            'link_img': 'seguimiento_comentario_add.png',
                            'action':   reverse_lazy('seguimiento:create_comentario')+'?next='+self.object.url_detail(),
                            'form':     Proyecto_Comentario_ModelForm('proyecto', instance=Comentario(tipo='P', obj_id=self.object.id)),
                            'opciones': DISPLAYS['forms'],
                            'tipo':     'P',
                            'id':       self.object.id,
                        })
        context['forms'] = formularios

        tablas = []
        if self.request.user.has_perm('seguimiento.view_proyecto_objetivo'):
            tablas.append({   
                            'title':        _('Objetivos'),
                            'object_list':  Proyecto_Objetivo.objects.filter(proyecto=self.object).order_by('descripcion'),
                            'enumerar':     1,
                            'lista':       ['descripcion',],
                            'campos_extra': [
                                { 'nombre':   _('Alcanzado'), 'funcion': 'get_alcanzado', },
                            ],
                            'opciones':     _('Opciones'),
                            'permisos': {
                                'update':   self.request.user.has_perm('seguimiento.change_proyecto_objetivo'),
                                'delete':   self.request.user.has_perm('seguimiento.delete_proyecto_objetivo'),
                            },
                            'next':         self.object.url_detail(),
                        })
        if self.request.user.has_perm('seguimiento.view_proyecto_meta'):
            tablas.append({
                            'title':        _('Metas'),
                            'object_list':  Proyecto_Meta.objects.filter(proyecto=self.object).order_by('descripcion'),
                            'enumerar':     1,
                            'lista':       ['descripcion',],
                            'campos_extra': [
                                { 'nombre':  _('Alcanzado'), 'funcion': 'get_alcanzado', },
                            ],
                            'opciones':     _('Opciones'),
                            'permisos': {
                                'update':   self.request.user.has_perm('seguimiento.change_proyecto_meta'),
                                'delete':   self.request.user.has_perm('seguimiento.delete_proyecto_meta'),
                            },
                            'next':         self.object.url_detail(),
                        })
        context['tables'] = tablas

        if self.request.user.has_perm('seguimiento.view_proyecto_fase'):
            context['fases'] = Proyecto_Fase.objects.filter(proyecto=self.object).order_by('descripcion')

        if self.object.ffin < date.today():
            messages.add_message(self.request, messages.WARNING, _('Proyecto expiró'))
        if estado_bloqueado:
            messages.add_message(self.request, messages.WARNING, _('El proyecto está en un estado bloqueado'))
        return context

class ProyectoUpdateView(PersonalUpdateView, SeguimientoContextMixin):
    permission_required = 'seguimiento.change_proyecto'
    template_name = 'template/forms.html'
    model = Proyecto
    form_class = ProyectoForm
    extra_context = {
        'title': _('Modificar Proyecto'),
        'opciones': DISPLAYS['forms'],
    }

    def get_success_url(self):
        return self.object.url_detail()

class ProyectoDeleteView(PersonalDeleteView, SeguimientoContextMixin):
    permission_required = 'seguimiento.delete_proyecto'
    template_name = 'template/delete_confirmation.html'
    model = Proyecto
    success_message = 'Eliminación exitosa'
    extra_context = {
        'title': _('Eliminar proyecto'),
        'opciones': DISPLAYS['delete_form'],
    }

    def get_success_url(self):
        return reverse_lazy('seguimiento:list_proyecto')



class Proyecto_UsuarioFormView(PersonalFormView, SeguimientoContextMixin):
    permission_required = 'seguimiento.proyect_admin'
    template_name = 'template/forms.html'
    model = Proyecto_Usuario
    form_class = Proyecto_Usuario_ModelForm
    success_url = reverse_lazy('seguimiento:list_proyecto')
    success_message = _('Usuario agregado correctamente')
    extra_context = {
        'title': _('Ingreso de usuario'),
        'opciones': DISPLAYS['forms'],
    }

    def get_form_kwargs(self, **kwargs):
        kwargs = super().get_form_kwargs()
        redirect = self.request.GET.get('next')
        if redirect:
            self.success_url = redirect
        return kwargs

    def form_valid(self, form, *args, **kwargs):
        data = form.cleaned_data
        usuario = Proyecto_Usuario(**data)
        usuario.save()
        return super().form_valid(form)

class Proyecto_UsuarioDeleteView(PersonalDeleteView, SeguimientoContextMixin):
    permission_required = 'seguimiento.proyect_admin'
    template_name = 'template/delete_confirmation.html'
    model = Proyecto_Usuario
    success_url = reverse_lazy('seguimiento:list_proyecto')
    extra_context = {
        'title': _('Remover usuario del proyecto'),
        'opciones': DISPLAYS['delete_form'],
    }

    def get_form_kwargs(self, **kwargs):
        kwargs = super().get_form_kwargs()
        redirect = self.request.GET.get('next')
        if redirect:
            self.success_url = redirect
        return kwargs



class Proyecto_EtiquetaFormView(PersonalFormView, SeguimientoContextMixin):
    permission_required = 'seguimiento.add_proyecto_etiqueta'
    template_name = 'template/forms.html'
    form_class = Proyecto_Etiqueta_ModelForm
    success_url = reverse_lazy('seguimiento:list_proyecto')
    success_message = _('Etiqueta agregada correctamente')
    extra_context = {
        'title': _('Ingreso de etiqueta'),
        'opciones': DISPLAYS['forms'],
    }

    def get_form_kwargs(self, **kwargs):
        kwargs = super().get_form_kwargs()
        redirect = self.request.GET.get('next')
        if redirect:
            self.success_url = redirect
        return kwargs

    def form_valid(self, form, *args, **kwargs):
        data = form.cleaned_data
        etiqueta = Proyecto_Etiqueta(**data)
        etiqueta.save()
        return super().form_valid(form)

    def form_invalid(self, form, *args, **kwargs):
        proy_id = form.cleaned_data['proyecto'].id
        for error in form.errors.as_data()['__all__']:
            messages.add_message(self.request, messages.WARNING, _(error.messages[0]))
        return HttpResponseRedirect(reverse_lazy('seguimiento:detail_proyecto', kwargs={'pk': proy_id}))
        
class Proyecto_EtiquetaListView(PersonalListView, SeguimientoContextMixin):
    permission_required = 'seguimiento.view_proyecto_etiqueta'
    template_name = 'template/list.html'
    model = Proyecto_Etiqueta
    ordering = ['-vigente', 'proyecto__nombre', 'descripcion']
    paginate_by = 10
    extra_context = {
        'title': _('Etiquetas de proyectos'),
        'campos': {
            'enumerar': 1,
            'lista': [ 'descripcion', 'proyecto', 'creacion'],
            'opciones': _('Opciones'),
        },
        'campos_extra': [
            { 'nombre':   _('Vigente'), 'funcion': 'get_vigente', },
            
        ],
        'opciones': DISPLAYS['opciones'],
        'mensaje': {
            'vacio': DISPLAYS['tabla_vacia'],
        },
    }

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['permisos'] = {
            'update': self.request.user.has_perm('seguimiento.change_proyecto_etiqueta'),
            'delete': self.request.user.has_perm('seguimiento.delete_proyecto_etiqueta'),
        }
        return context

class Proyecto_EtiquetaDetailView(PersonalDetailView, SeguimientoContextMixin):
    permission_required = 'seguimiento.view_proyecto_etiqueta'
    template_name = 'template/detail.html'
    model = Proyecto_Etiqueta
    extra_context = {
        'title': _('Etiquetas del proyecto'),
        'campos': {
            'lista': [ 'descripcion', 'creacion', 'actualizacion', 'proyecto', ],
            'opciones': _('Opciones'),
        },
        'campos_extra': [ 
            { 'nombre': _('Vigente'), 'funcion': 'get_vigente'},
        ],
        'opciones': DISPLAYS['opciones'],
    }

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['permisos'] = {
            'update': self.request.user.has_perm('seguimiento.change_proyecto_etiqueta'),
            'delete': self.request.user.has_perm('seguimiento.delete_proyecto_etiqueta'),
        }
        
        context['tables'] = [
            {
                'title':        _('Actividades'),
                'object_list':  Proyecto_Actividad.objects.none(), #filter(origen=self.object).order_by('actualizacion'),
                'enumerar':     1,
                'lista':        ['nombre', 'actualizacion'],
                'opciones':     _('Opciones'),
                'permisos': {
                    #'update':   self.request.user.has_perm('seguimiento.change_proyecto_etiqueta'),
                    #'delete':   self.request.user.has_perm('seguimiento.delete_proyecto_etiqueta'),
                },
                'next':         self.object.url_detail(),
            },
        ]
        return context

class Proyecto_EtiquetaUpdateView(PersonalUpdateView, SeguimientoContextMixin):
    permission_required = 'seguimiento.change_proyecto_etiqueta'
    template_name = 'template/forms.html'
    model = Proyecto_Etiqueta
    fields = ['descripcion', 'vigente']
    extra_context = {
        'title': _('Modificar etiqueta'),
        'opciones': DISPLAYS['forms'],
    }

    def get_success_url(self):
        return self.object.url_detail()

class Proyecto_EtiquetaDeleteView(PersonalDeleteView, SeguimientoContextMixin):
    permission_required = 'qliksense.delete_proyecto_etiqueta'
    template_name = 'template/delete_confirmation.html'
    model = Proyecto_Etiqueta
    success_url = reverse_lazy('seguimiento:list_proyectoetiqueta')
    extra_context = {
        'title': _('Eliminar etiqueta'),
        'opciones': DISPLAYS['delete_form'],
    }


class Proyecto_ObjetivoFormView(PersonalFormView, SeguimientoContextMixin):
    permission_required = 'seguimiento.add_proyecto_objetivo'
    template_name = 'template/forms.html'
    model = Proyecto_Objetivo
    form_class = Proyecto_Objetivo_ModelForm
    success_url = reverse_lazy('seguimiento:list_proyecto')
    success_message = _('Objetivo ingresado correctamente')
    extra_context = {
        'title': _('Ingreso de objetivo'),
        'opciones': DISPLAYS['forms'],
    }

    def get_form_kwargs(self, **kwargs):
        kwargs = super().get_form_kwargs()
        redirect = self.request.GET.get('next')
        if redirect:
            self.success_url = redirect
        return kwargs

    def form_valid(self, form, *args, **kwargs):
        data = form.cleaned_data
        proyecto_objetivo = Proyecto_Objetivo(**data)
        proyecto_objetivo.save()
        return super().form_valid(form)

class Proyecto_ObjetivoUpdateView(PersonalUpdateView, SeguimientoContextMixin):
    permission_required = 'seguimiento.change_proyecto_objetivo'
    template_name = 'template/forms.html'
    model = Proyecto_Objetivo
    fields = ['descripcion', 'alcanzado']
    #form_class = 
    #success_url = 
    success_message = 'Actualización exitosa'
    extra_context = {
        'title': _('Modificar Objetivo'),
        'opciones': DISPLAYS['forms'],
    }

    def get_form_kwargs(self, **kwargs):
        kwargs = super().get_form_kwargs()
        redirect = self.request.GET.get('next')
        if redirect:
            self.success_url = redirect
        return kwargs

class Proyecto_ObjetivoDeleteView(PersonalDeleteView, SeguimientoContextMixin):
    permission_required = 'seguimiento.delete_proyecto_objetivo'
    template_name = 'template/delete_confirmation.html'
    model = Proyecto_Objetivo
    #success_url =
    success_message = _('Eliminación exitosa')
    extra_context = {
        'title': _('Eliminar objetivo'),
        'opciones': DISPLAYS['delete_form'],
    }

    def get_form_kwargs(self, **kwargs):
        kwargs = super().get_form_kwargs()
        redirect = self.request.GET.get('next')
        if redirect:
            self.success_url = redirect
        return kwargs



class Proyecto_MetaFormView(PersonalFormView, SeguimientoContextMixin):
    permission_required = 'seguimiento.add_proyecto_meta'
    template_name = 'template/forms.html'
    model = Proyecto_Meta
    form_class = Proyecto_Meta_ModelForm
    success_url = reverse_lazy('seguimiento:list_proyecto')
    success_message = _('Meta ingresada correctamente')
    extra_context = {
        'title': _('Ingreso de meta'),
        'opciones': DISPLAYS['forms'],
    }

    def get_form_kwargs(self, **kwargs):
        kwargs = super().get_form_kwargs()
        redirect = self.request.GET.get('next')
        if redirect:
            self.success_url = redirect
        return kwargs

    def form_valid(self, form, *args, **kwargs):
        data = form.cleaned_data
        proyecto_meta = Proyecto_Meta(**data)
        proyecto_meta.save()
        return super().form_valid(form)

class Proyecto_MetaUpdateView(PersonalUpdateView, SeguimientoContextMixin):
    permission_required = 'seguimiento.change_proyecto_meta'
    template_name = 'template/forms.html'
    model = Proyecto_Meta
    fields = ['descripcion', 'alcanzado']
    #form_class = 
    #success_url = 
    success_message = 'Actualización exitosa'
    extra_context = {
        'title': _('Modificar Meta'),
        'opciones': DISPLAYS['forms'],
    }

    def get_form_kwargs(self, **kwargs):
        kwargs = super().get_form_kwargs()
        redirect = self.request.GET.get('next')
        if redirect:
            self.success_url = redirect
        return kwargs

class Proyecto_MetaDeleteView(PersonalDeleteView, SeguimientoContextMixin):
    permission_required = 'seguimiento.delete_proyecto_meta'
    template_name = 'template/delete_confirmation.html'
    model = Proyecto_Meta
    #success_url =
    success_message = 'Eliminación exitosa'
    extra_context = {
        'title': _('Eliminar meta'),
        'opciones': DISPLAYS['delete_form'],
    }

    def get_form_kwargs(self, **kwargs):
        kwargs = super().get_form_kwargs()
        redirect = self.request.GET.get('next')
        if redirect:
            self.success_url = redirect
        return kwargs



class Proyecto_FaseFormView(PersonalFormView, SeguimientoContextMixin):
    permission_required = 'seguimiento.add_proyecto_fase'
    template_name = 'template/forms.html'
    form_class = Proyecto_Fase_ModelForm
    success_url = reverse_lazy('seguimiento:list_proyecto')
    success_message = _('Fase ingresada correctamente')
    extra_context = {
        'title': _('Ingreso de fases'),
        'opciones': DISPLAYS['forms'],
    }

    def get_form_kwargs(self, **kwargs):
        kwargs = super().get_form_kwargs()
        redirect = self.request.GET.get('next')
        if redirect:
            self.success_url = redirect
        return kwargs

    def form_valid(self, form, *args, **kwargs):
        data = form.cleaned_data
        proyecto_fase = Proyecto_Fase(**data)
        proyecto_fase.save()
        return super().form_valid(form)

    def form_invalid(self, form):
        for error in form.errors.get("__all__"):
            messages.error(self.request, error)
        return redirect(self.success_url)

class Proyecto_FaseUpdateView(PersonalUpdateView, SeguimientoContextMixin):
    permission_required = 'seguimiento.change_proyecto_fase'
    template_name = 'template/forms.html'
    model = Proyecto_Fase
    fields = ['descripcion', 'cerrado']
    success_message = 'Actualización exitosa'
    extra_context = {
        'title': _('Modificar Fase'),
        'opciones': DISPLAYS['forms'],
    }

    def get_success_url(self):
        return reverse_lazy('seguimiento:detail_proyecto', 
            kwargs={'pk': self.object.proyecto.id, 'faseactiva': self.object.id})

class Proyecto_FaseDeleteView(PersonalDeleteView, SeguimientoContextMixin):
    permission_required = 'seguimiento.delete_proyecto_fase'
    template_name = 'template/delete_confirmation.html'
    model = Proyecto_Fase
    success_message = 'Eliminación exitosa'
    extra_context = {
        'title': _('Eliminar Fase'),
        'opciones': DISPLAYS['delete_form'],
    }

    def get_success_url(self):
        return reverse_lazy('seguimiento:detail_proyecto', 
            kwargs={'pk': self.object.proyecto.id})



class Proyecto_TareaListView(PersonalListView, SeguimientoContextMixin):
    permission_required = 'seguimiento.view_proyecto_tarea'
    template_name = 'template/list.html'
    model = Proyecto_Tarea
    ordering = ['-prioridad', 'creacion', 'descripcion']
    paginate_by = 50
    extra_context = {
        'title': _('Tareas pendientes'),
        'campos': {
            'enumerar': 1,
            'lista': [ 'descripcion', ],
            'opciones': _('Opciones'),
        },
        'opciones': DISPLAYS['opciones'],
        'campos_extra': [
            { 'nombre': _('Fase'), 'funcion': 'get_full_parent', },
            { 'nombre': _('% Completado'), 'porcentaje': 'finalizado', },
            { 'nombre': _('Prioridad'), 'valor': 'get_prioridad', },
        ],
        'mensaje': {
            'vacio': DISPLAYS['tabla_vacia'],
        },
        'busqueda': {
            'buscar':   _('Buscar'),
            'limpiar':  _('Limpiar'),
        },
    }

    def get_queryset(self):
        try:
            valor_busqueda = self.request.GET.get('valor').lower()
        except:
            valor_busqueda = None

        tareas = Proyecto_Actividad.objects.filter(finalizado__lt = 100).values_list('tarea_id').distinct()
        queryset = super().get_queryset().filter(proyecto_actividad__isnull=True) | Proyecto_Tarea.objects.filter(id__in = tareas)
        
        if valor_busqueda:
            if 'fase:' in valor_busqueda:
                fases = Proyecto_Fase.objects.filter(descripcion__icontains=valor_busqueda[5:].replace(' ', ''))
                queryset = queryset.filter(fase__in=fases)
            elif 'proyecto:' in valor_busqueda:
                proyectos = Proyecto.objects.filter(Q(nombre__icontains=valor_busqueda[9:])|Q(descripcion__icontains=valor_busqueda[9:]))
                queryset = queryset.filter(fase__proyecto__in=proyectos)
            else:
                queryset = queryset.filter(descripcion__icontains=valor_busqueda)

        if self.request.user.has_perm('seguimiento.proyect_admin'):
            return queryset
        asignados = Proyecto_Usuario.objects.filter(usuario = self.request.user).values_list('proyecto', flat=True) 
        publicos = Proyecto.objects.filter(publico=True).values_list('id', flat=True)

        queryset = queryset.filter(fase__proyecto__in = chain(asignados, publicos))
        return queryset

class Proyecto_TareaFormView(PersonalFormView, SeguimientoContextMixin):
    permission_required = 'seguimiento.add_proyecto_tarea'
    template_name = 'template/forms.html'
    form_class = Proyecto_Tarea_ModelForm
    success_url = reverse_lazy('seguimiento:list_proyecto')
    success_message = _('Tarea ingresada correctamente')
    extra_context = {
        'title': _('Ingreso de tareas'),
        'opciones': DISPLAYS['forms'],
    }

    def get_form_kwargs(self, **kwargs):
        kwargs = super().get_form_kwargs()
        redirect = self.request.GET.get('next')
        if redirect:
            self.success_url = redirect
        return kwargs

    def form_valid(self, form, *args, **kwargs):
        data = form.cleaned_data
        fase = Proyecto_Fase.objects.get(id = data['fase'].id)
        self.success_url = reverse_lazy('seguimiento:detail_proyecto', 
            kwargs={'pk': fase.proyecto.id, 'faseactiva': fase.id})
        proyecto_tarea = Proyecto_Tarea(**data)
        proyecto_tarea.save()
        return super().form_valid(form)

    def form_invalid(self, form):
        for error in form.errors.get("__all__"):
            messages.error(self.request, error)
        return redirect(self.success_url)

class Proyecto_TareaUpdateView(PersonalUpdateView, SeguimientoContextMixin):
    permission_required = 'seguimiento.change_proyecto_tarea'
    template_name = 'template/forms.html'
    model = Proyecto_Tarea
    form_class = Proyecto_Tarea_ModelForm
    success_message = 'Actualización exitosa'
    extra_context = {
        'title': _('Modificar tarea'),
        'opciones': DISPLAYS['forms'],
    }

    def get_success_url(self):
        return reverse_lazy('seguimiento:detail_proyecto', 
            kwargs={'pk': self.object.fase.proyecto.id, 'faseactiva': self.object.fase.id})

class Proyecto_TareaDeleteView(PersonalDeleteView, SeguimientoContextMixin):
    permission_required = 'seguimiento.delete_proyecto_tarea'
    template_name = 'template/delete_confirmation.html'
    model = Proyecto_Tarea
    #success_url =
    success_message = 'Eliminación exitosa'
    extra_context = {
        'title': _('Eliminar tarea'),
        'opciones': DISPLAYS['delete_form'],
    }

    def get_success_url(self):
        return reverse_lazy('seguimiento:detail_proyecto', 
            kwargs={'pk': self.object.fase.proyecto.id, 'faseactiva': self.object.fase.id})


class Proyecto_ActividadListView(PersonalListView, SeguimientoContextMixin):
    permission_required = 'seguimiento.view_proyecto_actividad'
    template_name = 'template/list.html'
    model = Proyecto_Actividad
    ordering = ['descripcion', '-finalizado', 'creacion']
    paginate_by = 50
    extra_context = {
        'title': _('Actividades pendientes'),
        'campos': {
            'enumerar': 1,
            'lista': [ 'descripcion', ],
            'opciones': _('Opciones'),
        },
        'opciones': DISPLAYS['opciones'],
        'campos_extra': [
            { 'nombre': _('Proyecto > Fase > Tarea'), 'funcion': 'get_full_parent', },
            { 'nombre': _('Avance'), 'funcion': 'get_porcentaje', },
        ],
        'mensaje': {
            'vacio': DISPLAYS['tabla_vacia'],
        },
        'busqueda': {
            'buscar':   _('Buscar'),
            'limpiar':  _('Limpiar'),
        },
    }

    def get_queryset(self):
        try:
            valor_busqueda = self.request.GET.get('valor').lower()
            queryset = super().get_queryset().select_related('tarea', 'tarea__fase')
        except:
            valor_busqueda = ''
            queryset = super().get_queryset().none()

        
        if 'tarea:' in valor_busqueda:
            tareas = Proyecto_Tarea.objects.filter(descripcion__icontains=valor_busqueda[6:].replace(' ', ''))
            queryset = queryset.filter(tarea__in=tareas)
        elif 'fase:' in valor_busqueda:
            fases = Proyecto_Fase.objects.filter(descripcion__icontains=valor_busqueda[5:].replace(' ', ''))
            queryset = queryset.filter(tarea__fase__in=fases)
        elif 'proyecto:' in valor_busqueda:
            proyectos = Proyecto.objects.filter(Q(nombre__icontains=valor_busqueda[9:])|Q(descripcion__icontains=valor_busqueda[9:]))
            queryset = queryset.filter(tarea__fase__proyecto__in=proyectos)
        else:
            queryset = queryset.filter(descripcion__icontains=valor_busqueda)

        asignados = Proyecto_Usuario.objects.filter(usuario = self.request.user).values_list('proyecto', flat=True) 
        publicos = Proyecto.objects.filter(publico=True).values_list('id', flat=True)

        queryset = queryset.filter(tarea__fase__proyecto__in = chain(asignados, publicos))
        return queryset

class Proyecto_ActividadFormView(PersonalFormView, SeguimientoContextMixin):
    permission_required = 'seguimiento.add_proyecto_actividad'
    template_name = 'template/forms.html'
    form_class = Proyecto_Actividad_ModelForm
    success_url = reverse_lazy('seguimiento:list_proyecto')
    success_message = _('Actividad ingresada correctamente')
    extra_context = {
        'title': _('Ingreso de actividades'),
        'opciones': DISPLAYS['forms'],
    }

    def get_form_kwargs(self, **kwargs):
        kwargs = super().get_form_kwargs()
        redirect = self.request.GET.get('next')
        if redirect:
            self.success_url = redirect
        return kwargs

    def form_valid(self, form, *args, **kwargs):
        data = form.cleaned_data
        fase = Proyecto_Fase.objects.get(id = data.pop('fase'))
        etiquetas = data.pop('etiqueta')
        self.success_url = reverse_lazy('seguimiento:detail_proyecto', 
            kwargs={'pk': fase.proyecto.id, 'faseactiva': fase.id})
        actividad = Proyecto_Actividad(**data)
        actividad.save()
        actividad.etiqueta.set(etiquetas)
        return super().form_valid(form)

    def form_invalid(self, form):
        for error in form.errors.get("__all__"):
            messages.error(self.request, error)
        return redirect(self.success_url)

class Proyecto_ActividadUpdateView(PersonalUpdateView, SeguimientoContextMixin):
    permission_required = 'seguimiento.change_proyecto_actividad'
    template_name = 'seguimiento/forms.html'
    model = Proyecto_Actividad
    form_class = Proyecto_Actividad_ModelForm
    success_message = 'Actualización exitosa'
    extra_context = {
        'title': _('Modificar actividad'),
        'opciones': DISPLAYS['forms'],
    }

    def get_success_url(self):
        fase = self.object.tarea.fase
        return reverse_lazy('seguimiento:detail_proyecto', 
            kwargs={'pk': fase.proyecto.id, 'faseactiva': fase.id})

class Proyecto_ActividadDeleteView(PersonalDeleteView, SeguimientoContextMixin):
    permission_required = 'seguimiento.delete_proyecto_actividad'
    template_name = 'template/delete_confirmation.html'
    model = Proyecto_Actividad
    success_message = 'Eliminación exitosa'
    extra_context = {
        'title': _('Eliminar Tarea'),
        'opciones': DISPLAYS['delete_form'],
    }

    def get_success_url(self):
        fase = self.object.tarea.fase
        return reverse_lazy('seguimiento:detail_proyecto', 
            kwargs={'pk': fase.proyecto.id, 'faseactiva': fase.id})

def combo_fase_tarea(request):
    if request.user.has_perm('seguimiento.add_proyecto_actividad'):
        tareas = Proyecto_Tarea.objects.filter(fase_id=request.GET.get('fase_id')).order_by('descripcion')
        return render(request, 'template/ajax_combo.html', {'options': tareas})
        
def accordion_tarea_actividad(request):
    if request.user.has_perm('seguimiento.view_proyecto_tarea'):
        fase = Proyecto_Fase.objects.get(id=request.GET.get('obj_id'))
        campos_actividad = ['creacion', 'descripcion', 'finalizado', 'responsable']
        tareas = Proyecto_Tarea.objects.filter(fase=fase)\
            .alias(
                pendiente = Count('proyecto_actividad', filter=Q(proyecto_actividad__finalizado__lt = 100)),
                sin_act = Count('proyecto_actividad'),
            ).annotate(
                fin=Case(
                    When(pendiente__gt=0, then=False),
                    When(sin_act = 0, then=False),
                    default = True, 
                    output_field=BooleanField()
                ),
            ).order_by('fin', 'descripcion') #'-prioridad', 
        context = {'fase': fase, 'tareas': tareas, 'campos': campos_actividad}
        return render(request, 'seguimiento/accordion_for_fase.html', context)

def tabla_pendiente(request):
    if request.user.has_perm('seguimiento.view_proyecto_pendiente'):
        pendientes = Proyecto_Actividad.objects.select_related('tarea', 'tarea__fase')\
            .filter(tarea__fase__proyecto=request.GET.get('obj_id'), finalizado__lt=100,
            responsable = request.user).order_by('tarea__descripcion', 'descripcion')
        context = {
            'table': {
                'title': _('Pendientes'),
                'object_list': pendientes,
                'lista': ['creacion', 'tarea', 'descripcion'],
                'campos_extra': [
                        { 'funcion': 'get_porcentaje' },
                    ],
                'opciones': _('Opciones'),
                'permisos': {
                    'detail_img': 'seguimiento_detail.png',
                    'update':   request.user.has_perm('seguimiento.change_proyecto_pendiente'),
                    'update_img': 'seguimiento_update.png',
                    'delete':   request.user.has_perm('seguimiento.delete_proyecto_pendiente'),
                    'delete_img': 'seguimiento_delete.png',
                },
            }
        }
    return render(request, 'template/tables.html', context)

def extrainfo_actividad(request):
    if request.user.has_perm('seguimiento.view_proyecto_actividad'):
        actividad = Proyecto_Actividad.objects.get(id=request.GET.get('obj_id'))
        lista_etiquetas = ', '.join([e.descripcion for e in actividad.etiqueta.all().order_by('descripcion')])
        context = {
            'etiquetas': lista_etiquetas, 
            'resolucion': mark_safe(actividad.resolucion)
        }
        return render(request, 'seguimiento/actividad_extrainfo.html', context)



class ComentarioFormView(PersonalFormView, SeguimientoContextMixin):
    permission_required = 'seguimiento.add_comentario'
    template_name = 'template/forms.html'
    form_class = Proyecto_Comentario_ModelForm
    success_url = reverse_lazy('seguimiento:list_proyecto')
    success_message = _('Comentario agregado correctamente')
    extra_context = {
        'title': _('Ingreso de comentario'),
        'opciones': DISPLAYS['forms'],
    }

    def get_form_kwargs(self, **kwargs):
        kwargs = super().get_form_kwargs()
        redirect = self.request.GET.get('next')
        if redirect:
            self.success_url = redirect
        return kwargs

    def form_valid(self, form, *args, **kwargs):
        data = form.cleaned_data
        comentario = Comentario(**data)
        comentario.usuario = self.request.user
        comentario.save()
        return super().form_valid(form)

    def form_invalid(self, form):
        for error in form.errors.get("__all__"):
            messages.error(self.request, error)
        return redirect(self.success_url)

class ComentarioListView(PersonalListView, SeguimientoContextMixin):
    permission_required = 'seguimiento.view_comentario'
    template_name = 'template/list.html'
    model = Comentario
    ordering = ['-creacion']
    paginate_by = 15
    extra_context = {
        'campos': {
            'enumerar': 1,
            'lista': [ 'creacion', 'descripcion', 'usuario' ],
            'opciones': _('Opciones'),
        },
        'opciones': DISPLAYS['opciones'],
        'campos_extra': [
            {
                'nombre':   _('Objeto'), 'funcion': 'get_objeto',  
            },
        ],
        'mensaje': {
            'vacio': DISPLAYS['tabla_vacia'],
        },
        'busqueda': {
            'buscar':   _('Buscar'),
            'limpiar':  _('Limpiar'),
        },
    }

    def get_context_data(self):
        context = super().get_context_data()
        context['title']= Proyecto.objects.get(pk=self.kwargs['pk']).__str__() + ': ' + _('Comentarios')
        context['permisos'] = {
                'delete': self.request.user.has_perm('seguimiento.delete_comentario'),
        }
        return context

    def get_queryset(self):
        try:
            valor_busqueda = self.request.GET.get('valor').lower()
        except:
            valor_busqueda = None
        
        proy = Proyecto.objects.filter(pk=self.kwargs['pk'])
        fases= Proyecto_Fase.objects.filter(proyecto__in = proy).values_list('id')
        tareas = Proyecto_Tarea.objects.filter(fase__in=fases).values_list('id')
        actividades = Proyecto_Actividad.objects.filter(tarea__in=tareas).values_list('id')
        data = {'proyecto': proy, 'fases': fases, 'tareas': tareas, 'actividades': actividades}
        
        if valor_busqueda:
            if 'usuario:' in valor_busqueda:
                usuario = Usuario.objects.get(username=valor_busqueda[8:].replace(' ', ''))
                return self.special_queryset(**data).filter(usuario=usuario)
            elif 'objeto:' in valor_busqueda:
                objeto = valor_busqueda[7:]
                proy    = proy.filter(Q(nombre__icontains=objeto)|Q(descripcion__icontains=objeto))
                fases   = fases.filter(descripcion__icontains=objeto)
                tareas  = tareas.filter(descripcion__icontains=objeto)
                actividades = actividades.filter(descripcion__icontains=objeto)
                data = {'proyecto': proy, 'fases': fases, 'tareas': tareas, 'actividades': actividades}
                return self.special_queryset(**data)
            else:
                return self.special_queryset(**data).filter(descripcion__icontains = valor_busqueda)
        return self.special_queryset(**data)

    def special_queryset(self, *args, **kwargs):
        queryset = Comentario.objects.filter(tipo='P', obj_id__in=kwargs['proyecto']) |\
            Comentario.objects.filter(tipo='F', obj_id__in=kwargs['fases']) |\
            Comentario.objects.filter(tipo='T', obj_id__in=kwargs['tareas']) |\
            Comentario.objects.filter(tipo='A', obj_id__in=kwargs['actividades'])

        return queryset.order_by('-creacion')

class ComentarioDeleteView(PersonalDeleteView, SeguimientoContextMixin):
    permission_required = 'seguimiento.delete_comentario'
    template_name = 'template/delete_confirmation.html'
    model = Comentario
    #success_url =
    success_message = 'Eliminación exitosa'
    extra_context = {
        'title': _('Eliminar comentario'),
        'opciones': DISPLAYS['delete_form'],
    }

    def get_success_url(self):
        print(self.object.get_proyecto_id())
        return reverse_lazy('seguimiento:list_comentario', kwargs={'pk': self.object.get_proyecto_id()})



class ReporteAvancesFormView(PersonalFormView, SeguimientoContextMixin):
    permission_required = 'seguimiento.view_proyecto'
    template_name = 'template/forms.html'
    form_class = Proyecto_Reporte_Avances
    extra_context = {
        'title': _('Reporte de avances'),
        'opciones': DISPLAYS['forms'],
    }

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['usuario'] = self.request.user.id
        return kwargs

    def form_valid(self, form, *args, **kwargs):
        data = form.cleaned_data
        return reporte_avance_proyecto(data['proyecto'])

class ReporteActividadesFormView(PersonalFormView, SeguimientoContextMixin):
    permission_required = 'seguimiento.view_proyecto'
    template_name = 'seguimiento/forms.html'
    form_class = Proyecto_Reportes_Actividades
    extra_context = {
        'title': _('Reporte de actividades (por última actualización)'),
        'opciones': DISPLAYS['forms'],
    }

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['usuario'] = self.request.user.id
        return kwargs

    def form_valid(self, form, *args, **kwargs):
        data = form.cleaned_data
        return reporte_actividades_proyecto(data['proyecto'], data['fini'], data['ffin'])

def combo_proyecto_usuario(request):
    if request.user.has_perm('seguimiento.view_proyecto'):
        usuarios = Proyecto_Usuario.objects.filter(proyecto_id=request.GET.get('proyecto_id')).values_list('usuario')
        usuarios = Usuario.objects.filter(id__in=usuarios)
        return render(request, 'template/ajax_combo.html', {'options': usuarios})



#REPORTES
def reporte_actividades_proyecto(proyecto_id, fecha_ini, fecha_fin, workbook=None, buffer=None):
    '''
        REPORTE DE ACTIVIDADES
    '''
    proyecto    = Proyecto.objects.get(id = proyecto_id)

    actividades = Proyecto_Actividad.objects.select_related('tarea__fase', 'tarea')\
            .filter(tarea__fase__proyecto=proyecto)
    
    if fecha_ini and fecha_fin:
        actividades = actividades.filter(actualizacion__gte=fecha_ini, actualizacion__lte=fecha_fin)
            
    actividades = actividades.order_by('descripcion')

    if not workbook:
        buffer = io.BytesIO()
        workbook = xlsxwriter.Workbook(buffer)
    worksheet = workbook.add_worksheet('Detalle')

    archivo = {
        'nombre': f'Actividades - {proyecto.nombre}', 
        'ancho_columnas':   [(0, 0, 15), (1, 1, 30), (2 , 2, 30), (3, 3, 90), (4, 6, 30)],
        }
    formatos = {
        'titulo':   workbook.add_format(reporte_formato('titulo')),
        'titulo%':  workbook.add_format(reporte_formato('titulo', 'porcentaje')),
        'subtitulo':workbook.add_format(reporte_formato('subtitulo')),
        '%':        workbook.add_format(reporte_formato('porcentaje')),
        'fecha':    workbook.add_format(reporte_formato('fecha')),
        'wrapping': workbook.add_format(reporte_formato('wrapping')),
    }
    
    #Ancho de columnas
    for columna in archivo['ancho_columnas']:
        worksheet.set_column(*columna)

    arreglo_data = []
    data  = []
    data.append(reporte_data(0, 0, 'string', proyecto.nombre, formatos['titulo']))
    data.append(reporte_data(None, 4, 'number', proyecto.get_porcentaje_completado/100, formatos['titulo%']))
    arreglo_data.append(data)

    #Titulos
    data  = []
    data.append(reporte_data(2, None, 'string', 'FECHA', formatos['subtitulo']))
    data.append(reporte_data(None, None, 'string', 'FASE', formatos['subtitulo']))
    data.append(reporte_data(None, None, 'string', 'TAREA', formatos['subtitulo']))
    data.append(reporte_data(None, None, 'string', 'ACTIVIDAD', formatos['subtitulo']))
    data.append(reporte_data(None, None, 'string', 'RESPONSABLE', formatos['subtitulo']))
    data.append(reporte_data(None, None, 'string', 'RESOLUCIÓN', formatos['subtitulo']))
    arreglo_data.append(data)

    for actividad in actividades:
        responsable = actividad.responsable
        responsable = actividad.history.all().last().history_user if not responsable else responsable
        responsable = '' if not responsable else responsable.get_full_name()

        data  = []
        data.append(reporte_data(None, None, 'datetime', actividad.actualizacion, formatos['fecha']))
        data.append(reporte_data(None, None, 'string', actividad.tarea.fase.descripcion, None))
        data.append(reporte_data(None, None, 'string', actividad.tarea.descripcion, None))
        data.append(reporte_data(None, None, 'string', actividad.descripcion, None))
        data.append(reporte_data(None, None, 'string', responsable, None))
        data.append(reporte_data(None, None, 'string', html2text.html2text(actividad.resolucion),  formatos['wrapping']))
        arreglo_data.append(data)

    repote_escribe(worksheet, arreglo_data)

    if workbook:
        workbook.close()
        buffer.seek(0)

    return FileResponse(buffer, as_attachment=True, filename=f'{archivo["nombre"]}.xlsx')

def reporte_avance_proyecto(proyecto_id):
    '''
        REPORTE DE AVANCES
    '''
    proyecto= Proyecto.objects.get(id = proyecto_id)
    fases   = Proyecto_Fase.objects.filter(proyecto=proyecto).order_by('descripcion')
    proy_usr= Proyecto_Usuario.objects.filter(proyecto=proyecto)
    
    buffer = io.BytesIO()
    workbook = xlsxwriter.Workbook(buffer)
    worksheet = workbook.add_worksheet('General')

    archivo = {
        'nombre': f'Avances - {proyecto.nombre}', 
        'ancho_columnas':   [(0, 0, 36), (1, 1, 120), (2 , 7, 15)],
        }
    formatos = {
        'titulo':   workbook.add_format(reporte_formato('titulo')),
        'titulo%':  workbook.add_format(reporte_formato('titulo', 'porcentaje')),
        'subtitulo':workbook.add_format(reporte_formato('subtitulo')),
        '%':        workbook.add_format(reporte_formato('porcentaje')),
        'wrapping': workbook.add_format(reporte_formato('wrapping')),
    }

    #Ancho de columnas
    for columna in archivo['ancho_columnas']:
        worksheet.set_column(*columna)
    
    arreglo_data = []
    data  = []
    
    data.append(reporte_data(0, 0, 'string', proyecto.nombre, formatos['titulo']))
    data.append(reporte_data(None, 7, 'number', proyecto.get_porcentaje_completado/100, formatos['titulo%']))
    arreglo_data.append(data)

    data  = []
    data.append(reporte_data(2, 0, 'string', 'FASE', formatos['subtitulo']))
    data.append(reporte_data(None, None, 'string', 'TAREA', formatos['subtitulo']))
    data.append(reporte_data(None, None, 'string', 'RESPONSABLE', formatos['subtitulo']))
    data.append(reporte_data(None, None, 'string', '# ACTIVIDADES', formatos['subtitulo']))
    data.append(reporte_data(None, None, 'string', 'PRIORIDAD', formatos['subtitulo']))
    data.append(reporte_data(None, None, 'string', 'COMPLEJIDAD', formatos['subtitulo']))
    data.append(reporte_data(None, None, 'string', 'ESTADO', formatos['subtitulo']))
    data.append(reporte_data(None, None, 'string', '% AVANCE', formatos['subtitulo']))
    arreglo_data.append(data)

    for fase in fases:
        data  = []
        
        for tarea in Proyecto_Tarea.objects.filter(fase=fase):
            usr_id = Proyecto_Actividad.objects.filter(tarea = tarea).values_list('responsable_id', flat=True).distinct()
            data = []
            data.append(reporte_data(None, None, 'string', fase.descripcion, None))
            data.append(reporte_data(None, None, 'string', tarea.descripcion, None))
            data.append(reporte_data(None, None, 'string', ', '.join([u.usuario.get_full_name() for u in proy_usr.filter(usuario_id__in=usr_id)]), None))
            data.append(reporte_data(None, None, 'number', tarea.get_cantidad_actividades(), None))
            data.append(reporte_data(None, None, 'string', tarea.get_prioridad_display(), None))
            data.append(reporte_data(None, None, 'number', tarea.complejidad, None))
            data.append(reporte_data(None, None, 'string', 'COMPLETADO' if tarea.finalizado==1 else 'PENDIENTE', None))
            data.append(reporte_data(None, None, 'number', tarea.finalizado/100, formatos['%']))
            arreglo_data.append(data)

    repote_escribe(worksheet, arreglo_data)

    worksheet = workbook.add_worksheet('Actividades')
    
    for columna in [(0, 0, 30), (1, 2, 66), (3 , 6, 21), (7 , 7, 60)]:
        worksheet.set_column(*columna)

    arreglo_data = []
    data  = []
    data.append(reporte_data(0, 0, 'string', 'FASE', formatos['subtitulo']))
    data.append(reporte_data(None, None, 'string', 'TAREA', formatos['subtitulo']))
    data.append(reporte_data(None, None, 'string', 'ACTIVIDAD', formatos['subtitulo']))
    data.append(reporte_data(None, None, 'string', 'ETIQUETAS', formatos['subtitulo']))
    data.append(reporte_data(None, None, 'string', 'RESPONSABLE', formatos['subtitulo']))
    data.append(reporte_data(None, None, 'string', 'ESTADO', formatos['subtitulo']))
    data.append(reporte_data(None, None, 'string', '% AVANCE', formatos['subtitulo']))
    data.append(reporte_data(None, None, 'string', 'RESOLUCIÓN', formatos['subtitulo']))
    arreglo_data.append(data)

    actividades = Proyecto_Actividad.objects.select_related('tarea', 'tarea__fase').filter(tarea__fase__proyecto=proyecto)

    for actividad in actividades:
        data = []
        responsable = actividad.responsable
        responsable = actividad.history.all().last().history_user if not responsable else responsable
        responsable = '' if not responsable else responsable.get_full_name()

        data.append(reporte_data(None, None, 'string', actividad.tarea.fase.descripcion, formatos['wrapping']))
        data.append(reporte_data(None, None, 'string', actividad.tarea.descripcion, formatos['wrapping']))
        data.append(reporte_data(None, None, 'string', actividad.descripcion, formatos['wrapping']))
        data.append(reporte_data(None, None, 'string', ', '.join([e.descripcion for e in actividad.etiqueta.all().order_by('descripcion')]), formatos['wrapping']))
        data.append(reporte_data(None, None, 'string', responsable, None))
        data.append(reporte_data(None, None, 'string', 'COMPLETADO' if actividad.finalizado==100 else 'PENDIENTE', None))
        data.append(reporte_data(None, None, 'number', actividad.finalizado/100, formatos['%']))
        data.append(reporte_data(None, None, 'string', html2text.html2text(actividad.resolucion),  formatos['wrapping']))
        arreglo_data.append(data)

    repote_escribe(worksheet, arreglo_data)

    if workbook:
        workbook.close()
        buffer.seek(0)

    return FileResponse(buffer, as_attachment=True, filename=f'{archivo["nombre"]}.xlsx')



def reporte_data(fila, columna, tipo, valor, formato):
    d = {}
    if fila:
        d['fila'] = fila
    if columna:
        d['columna'] = columna
    if tipo:
        d['tipo'] = tipo
    if valor is not None:
        d['valor'] = valor
    if formato:
        d['formato'] = formato
    return d

def reporte_formato(*args, custom=None):
    formato = {
        'titulo'    : {'font_size': 18, 'bold': True},
        'subtitulo' : {'font_size': 12, 'bold': True, 'italic': True},
        'wrapping'  : {'text_wrap': True},
        'porcentaje': {'num_format': '0.00%'},
        'fecha'     : {'num_format': 'dd/mm/yyyy'},
        'fecha_hora': {'num_format': 'dd/mm/yy hh:mm:ss'},
        'hora'      : {'num_format': 'hh:mm:ss'},
        'custom'    : {'custom': custom},
    }
    f = {} 
    for elemento in args:
        f.update(formato[f'{elemento}'])
    if custom:
        f.update(formato[f'{custom}'])
    return f
    
def repote_escribe(hoja, arreglo_data = [], fila_inicial=0, columna_inicial=0):
    fila, columna = fila_inicial, columna_inicial
    for data in arreglo_data:
        for registro in data:
            #print(registro)
            if 'fila' in registro:
                fila = registro['fila']

            if 'columna' in registro:
                columna = registro['columna']

            try:
                valor = registro['valor'] if 'valor' in registro else None
                formato = registro['formato'] if 'formato' in registro else None

                if registro['tipo']=='string':
                    hoja.write_string(fila, columna, valor, formato)
                elif registro['tipo']=='number':
                    hoja.write_number(fila, columna, valor, formato)
                elif registro['tipo']=='blank':
                    hoja.write_blank(fila, columna, valor, formato)
                elif registro['tipo']=='formula':
                    hoja.write_formula(fila, columna, valor, formato)
                elif registro['tipo']=='datetime':
                    hoja.write_datetime(fila, columna, valor, formato)
                elif registro['tipo']=='boolean':
                    hoja.write_boolean(fila, columna, valor, formato)
                elif registro['tipo']=='url':
                    hoja.write_url(fila, columna, valor, formato)
                else:
                    hoja.write(fila, columna, valor)
            except:
                hoja.write(fila, columna, valor)
            columna += 1
        fila, columna = fila+1, 0
