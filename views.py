from datetime import date
from itertools import chain

from django.apps import apps
from django.contrib import messages
from django.db.models import Q
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.translation import gettext as _
from django.views.generic.base import TemplateView

from usuarios.personal_views import (PersonalContextMixin, PersonalCreateView, 
    PersonalUpdateView, PersonalListView, PersonalDetailView, PersonalDeleteView, 
    PersonalFormView, Configuracion)

from .models import (Estado, Tipo_Proyecto, Origen_Proyecto, PM_Proyecto, Proyecto, Proyecto_Objetivo, Proyecto_Meta, Proyecto_Fase,
	Proyecto_Tarea, Proyecto_Usuario, Comentario)
from .forms import (ProyectoForm, Proyecto_Objetivo_ModelForm, Proyecto_Meta_ModelForm,
    Proyecto_Fase_ModelForm, Proyecto_Tarea_ModelCreateForm, Proyecto_Tarea_ModelUpdateForm,
    Proyecto_Usuario_ModelForm, Proyecto_Comentario_ModelForm)

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
                'desc':     _('Agrupación de actividades por poryecto, medicion de \
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
            'lista': [ 'nombre', 'descripcion', 'creacion', 'actualizacion',
                'lider', 'estado', 'tipo', 'origen', 'pm', ],
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
        context['campos_extra'] = [
            { 'nombre': _('Periodo'), 'funcion': 'get_periodo' },
            { 'nombre': _('Publico'), 'funcion': 'get_tipo_permiso', },
            { 'nombre': _('Completado'), 'funcion': 'get_porcentaje_completado', },
            { 'nombre': _('Usuarios'), 'ul_lista': self.object.get_usuarios() },
        ]
        context['permisos'] = {
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
                            'action':   reverse_lazy('seguimiento:create_proyectoobjetivo')+'?next='+self.object.url_detail() if self.object.get_modificable() else None,
                            'form':     Proyecto_Objetivo_ModelForm('proyecto', instance=Proyecto_Objetivo(proyecto=self.object)),
                            'opciones': DISPLAYS['forms'],
                        })
        if self.request.user.has_perm('seguimiento.add_proyecto_meta'):
            formularios.append({
                            'modal':    'proyecto_meta', 
                            'display':  _('Definición de metas'),
                            'link_img': 'seguimiento_meta_add.png',
                            'action':   reverse_lazy('seguimiento:create_proyectometa')+'?next='+self.object.url_detail() if self.object.get_modificable() else None,
                            'form':     Proyecto_Meta_ModelForm('proyecto', instance=Proyecto_Meta(proyecto=self.object)),
                            'opciones': DISPLAYS['forms'],
                        })
        if self.request.user.has_perm('seguimiento.add_proyecto_fase'):
            formularios.append({
                            'modal':    'proyecto_fase', 
                            'display':  _('Definición de fases'),
                            'link_img': 'seguimiento_fase_add.png',
                            'action':   reverse_lazy('seguimiento:create_proyectofase')+'?next='+self.object.url_detail() if self.object.get_modificable() else None,
                            'form':     Proyecto_Fase_ModelForm('proyecto', instance=Proyecto_Fase(proyecto=self.object)),
                            'opciones': DISPLAYS['forms'],
                        })
        if self.request.user.has_perm('seguimiento.add_proyecto_tarea'):
            formularios.append({
                            'modal':    'proyecto_tarea', 
                            'display':  _('Definición de tareas'),
                            'link_img': 'seguimiento_tarea_add.png',
                            'action':   reverse_lazy('seguimiento:create_proyectotarea')+'?next='+self.object.url_detail() if self.object.get_modificable() else None,
                            'form':     Proyecto_Tarea_ModelCreateForm(self.object),
                            'opciones': DISPLAYS['forms'],
                        })
        if self.request.user.has_perm('seguimiento.proyect_admin'):
            formularios.append({
                            'modal':    'proyecto_usuario', 
                            'display':  _('Agregar usuario al proyecto'),
                            'link_img': 'seguimiento_add_usuario.png',
                            'action':   reverse_lazy('seguimiento:create_proyectousuario')+'?next='+self.object.url_detail() if self.object.get_modificable() else None,
                            'form':     Proyecto_Usuario_ModelForm('proyecto', instance=Proyecto_Objetivo(proyecto=self.object)),
                            'opciones': DISPLAYS['forms'],
                        })
        if self.request.user.has_perm('seguimiento.add_comentario'):
            formularios.append({
                            'modal':    'comentario',
                            'display':  _('Comentario'),
                            'link_img': 'seguimiento_comentario_add.png',
                            'action':   reverse_lazy('seguimiento:create_comentario')+'?next='+self.object.url_detail() if self.object.get_modificable() else None,
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
            context['fases'] = {
                            'enumerar':     -1,
                            'object_list':  Proyecto_Fase.objects.filter(proyecto=self.object).order_by('correlativo'),
                            'func_extra':   'get_porcentaje_completado',
                            'campos':       ['descripcion', 'get_prioridad', 'complejidad', 'get_finalizado'], #subtabla
                            'permisos_tarea': {
                                'update':   self.request.user.has_perm('seguimiento.change_proyecto_tarea'),
                                'delete':   self.request.user.has_perm('seguimiento.delete_proyecto_tarea'),
                            },
                            'opciones':     _('Opciones'),
                            'permisos': {
                                'comment':   self.request.user.has_perm('seguimiento.add_comentario'),
                                'update':   self.request.user.has_perm('seguimiento.change_proyecto_fase'),
                                'delete':   self.request.user.has_perm('seguimiento.delete_proyecto_fase'),
                            },
                            'next':         self.object.url_detail(),
                        }

        if self.object.ffin < date.today():
            messages.add_message(self.request, messages.WARNING, _('Proyecto expiró'))
        return context

class ProyectoUpdateView(PersonalUpdateView, SeguimientoContextMixin):
    permission_required = 'seguimiento.change_proyecto'
    template_name = 'template/forms.html'
    model = Proyecto
    #fields = []
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
    success_url = reverse_lazy('seguimiento:list_proyecto')
    extra_context = {
        'title': _('Eliminar proyecto'),
        'opciones': DISPLAYS['delete_form'],
    }



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
        proyecto_objetivo = Proyecto_Usuario(**data)
        proyecto_objetivo.save()
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
    model = Proyecto_Fase
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
    fields = ['descripcion']
    #form_class = 
    #success_url = 
    success_message = 'Actualización exitosa'
    extra_context = {
        'title': _('Modificar Fase'),
        'opciones': DISPLAYS['forms'],
    }

    def get_form_kwargs(self, **kwargs):
        kwargs = super().get_form_kwargs()
        redirect = self.request.GET.get('next')
        if redirect:
            self.success_url = redirect
        return kwargs

class Proyecto_FaseDeleteView(PersonalDeleteView, SeguimientoContextMixin):
    permission_required = 'seguimiento.delete_proyecto_fase'
    template_name = 'template/delete_confirmation.html'
    model = Proyecto_Fase
    #success_url =
    success_message = 'Eliminación exitosa'
    extra_context = {
        'title': _('Eliminar Fase'),
        'opciones': DISPLAYS['delete_form'],
    }

    def get_form_kwargs(self, **kwargs):
        kwargs = super().get_form_kwargs()
        redirect = self.request.GET.get('next')
        if redirect:
            self.success_url = redirect
        return kwargs



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
        },
        'campos_extra': [
            { 'nombre': _('Fase'), 'funcion': 'get_full_parent', },
            { 'nombre': _('% Completado'), 'valor': 'get_finalizado', },
            { 'nombre': _('Prioridad'), 'valor': 'get_prioridad', },
            { 'nombre': _('Ir'), 'url': 'url_proyecto', 'target': '_blank', 'img': 'seguimiento_ir.png'},
        ],
        'mensaje': {
            'vacio': DISPLAYS['tabla_vacia'],
        },
    }

    def get_queryset(self):
        queryset = super().get_queryset().filter(finalizado__lt = 100)
        queryset = queryset.select_related('fase')
        if self.request.user.has_perm('seguimiento.proyect_admin'):
            return queryset
        asignados = Proyecto_Usuario.objects.filter(usuario = self.request.user).values_list('proyecto', flat=True) 
        publicos = Proyecto.objects.filter(publico=True).values_list('id', flat=True)

        queryset = queryset.filter(fase__proyecto__in = chain(asignados, publicos))
        return queryset

class Proyecto_TareaFormView(PersonalFormView, SeguimientoContextMixin):
    permission_required = 'seguimiento.add_proyecto_tarea'
    template_name = 'template/forms.html'
    model = Proyecto_Tarea
    form_class = Proyecto_Tarea_ModelCreateForm
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
        proyecto_fase = Proyecto_Tarea(**data)
        proyecto_fase.save()
        return super().form_valid(form)

    def form_invalid(self, form):
        for error in form.errors.get("__all__"):
            messages.error(self.request, error)
        return redirect(self.success_url)

class Proyecto_TareaUpdateView(PersonalUpdateView, SeguimientoContextMixin):
    permission_required = 'seguimiento.change_proyecto_tarea'
    template_name = 'template/forms.html'
    model = Proyecto_Tarea
    #fields = 
    form_class = Proyecto_Tarea_ModelUpdateForm
    #success_url = 
    success_message = 'Actualización exitosa'
    extra_context = {
        'title': _('Modificar Tarea'),
        'opciones': DISPLAYS['forms'],
    }

    def get_form_kwargs(self, **kwargs):
        kwargs = super().get_form_kwargs()
        redirect = self.request.GET.get('next')
        if redirect:
            self.success_url = redirect
        return kwargs

class Proyecto_TareaDeleteView(PersonalDeleteView, SeguimientoContextMixin):
    permission_required = 'seguimiento.delete_proyecto_tarea'
    template_name = 'template/delete_confirmation.html'
    model = Proyecto_Tarea
    #success_url =
    success_message = 'Eliminación exitosa'
    extra_context = {
        'title': _('Eliminar Tarea'),
        'opciones': DISPLAYS['delete_form'],
    }

    def get_form_kwargs(self, **kwargs):
        kwargs = super().get_form_kwargs()
        redirect = self.request.GET.get('next')
        if redirect:
            self.success_url = redirect
        return kwargs



class Comentario_FormView(PersonalFormView, SeguimientoContextMixin):
    permission_required = 'seguimiento.add_comentario'
    template_name = 'template/forms.html'
    model = Comentario
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
            #-1: no enumera
            # 0: inicia numeración en 0
            # 1: inicia numeración en 1
            'enumerar': 1,
            # Si hay valor se muestra opciones por linea, de lo contrario no se muestran
            #'opciones': _('Opciones'),
            # Lista de campos que se deben mostrar en la tabla
            'lista': [
                'creacion', 'descripcion', 'usuario'
            ],
        },
        'campos_extra': [
            {
                'nombre':   _('Objeto'), #display
                # valor, constante o funcion 
                'funcion': 'get_objeto',  
            },
        ],
        'mensaje': {
            'vacio': DISPLAYS['tabla_vacia'],
        },
    }

    def get_context_data(self):
        context = super().get_context_data()
        context['title']= Proyecto.objects.get(pk=self.kwargs['pk']).__str__() + ': ' + _('Comentarios')
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        proy = Proyecto.objects.get(pk=self.kwargs['pk'])
        fases= Proyecto_Fase.objects.filter(proyecto = proy).values_list('id')
        tareas = Proyecto_Tarea.objects.filter(fase__in=fases).values_list('id')
        
        return (Comentario.objects.filter(tipo='P', obj_id=proy.id) | 
            Comentario.objects.filter(tipo='F', obj_id__in=fases) |
            Comentario.objects.filter(tipo='T', obj_id__in=tareas)).order_by('-creacion')
