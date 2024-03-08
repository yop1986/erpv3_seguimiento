#import os, json
#
from django.apps import apps
#from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.translation import gettext as _
from django.views.generic.base import TemplateView
#
#from simple_history.utils import bulk_create_with_history
#
from usuarios.personal_views import (PersonalContextMixin, PersonalCreateView, 
    PersonalUpdateView, PersonalListView, PersonalDetailView, PersonalDeleteView, 
    PersonalFormView, Configuracion)
#
from .models import (Estado, Proyecto, Proyecto_Objetivos, Proyecto_Metas, Proyecto_Fases,
	Proyecto_Tareas, Comentario)
from .forms import ProyectoForm
#from .qliksenseapi import QSWebSockets # Configuracion as ApiConfig, ValidaArchivos
#
#gConfiguracion = Configuracion()
#
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
#    'disable_form': {
#        'confirmacion': _('¿Esta seguro de inhabilitar el elemento indicado?'),
#        'submit': _('Inhabilitar'),
#        'cancel': _('Cancelar'),
#    },
    'opciones': {
        'detail': _('Ver'),
        'update': _('Editar'),
        'delete': _('Eliminar'),
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
        'campos': {
            #-1: no enumera
            # 0: inicia numeración en 0
            # 1: inicia numeración en 1
            'enumerar': 1,
            # Si hay valor se muestra opciones por linea, de lo contrario no se muestran
            'opciones': _('Opciones'),
            # Lista de campos que se deben mostrar en la tabla
            'lista': [
                'descripcion', 
                'actualizacion', 
            ],
        },
        'campos_extra': [
            {
                'nombre':   _('Vigente'), #display
                # valor, constante o funcion 
                'funcion': 'get_vigente',  
            },
        ],
        'opciones': DISPLAYS['opciones'],
        'create' :{
            'display':  _('Nuevo'),
            'url':      Estado.url_create(),
        },
        'mensaje': {
            'vacio': DISPLAYS['tabla_vacia'],
        },
    }

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
            'opciones': _('Opciones'),
            'lista': [
                #'id',
                'descripcion', 
                'actualizacion', 
            ],
        },
        'opciones': DISPLAYS['opciones'],
    }

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['campos_adicionales'] = [ 
            {'display': _('Bloquea'), 'valor': self.object.get_bloquea()},
            {'display': _('Vigente'), 'valor': self.object.get_vigente()},
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
    success_url = reverse_lazy('qliksense:list_estado')
    extra_context = {
        'title': _('Eliminar estado'),
        'opciones': DISPLAYS['delete_form'],
    }



class ProyectoListView(PersonalListView, SeguimientoContextMixin):
    permission_required = 'seguimiento.view_proyecto'
    template_name = 'template/list.html'
    model = Proyecto
    ordering = ['-estado', 'nombre']
    paginate_by = 15
    extra_context = {
        'title': _('Proyectos'),
        'campos': {
            #-1: no enumera
            # 0: inicia numeración en 0
            # 1: inicia numeración en 1
            'enumerar': 1,
            # Si hay valor se muestra opciones por linea, de lo contrario no se muestran
            'opciones': _('Opciones'),
            # Lista de campos que se deben mostrar en la tabla
            'lista': [
                'nombre', 'finicio', 'ffin'
            ],
        },
        'campos_extra': [
            {
                'nombre':   _('Resumen'), #display
                # valor, constante o funcion 
                'funcion': 'get_resumen',  
            },
        ],
        'opciones': DISPLAYS['opciones'],
        'create' :{
            'display':  _('Nuevo'),
            'url':      Proyecto.url_create(),
        },
        'mensaje': {
            'vacio': DISPLAYS['tabla_vacia'],
        },
    }

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

class ProyectoDetailView(PersonalDetailView, SeguimientoContextMixin):
    permission_required = 'seguimiento.view_proyecto'
    template_name = 'template/detail.html'
    model = Proyecto
    extra_context = {
        'title': _('Proyecto'),
        'campos': {
            'opciones': _('Opciones'),
            'lista': [
                #'id',
                'nombre',
                'descripcion',
                'creacion',
                'actualizacion',
                'finicio',
                'ffin',
                'estado', 
            ],
        },
        'opciones': DISPLAYS['opciones'],
    }

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['campos_adicionales'] = [ 
            #{'display': _('Bloquea'), 'valor': self.object.get_bloquea()},
        ]
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
