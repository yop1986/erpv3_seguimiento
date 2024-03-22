from django.apps import apps
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.translation import gettext as _
from django.views.generic.base import TemplateView

from usuarios.personal_views import (PersonalContextMixin, PersonalCreateView, 
    PersonalUpdateView, PersonalListView, PersonalDetailView, PersonalDeleteView, 
    PersonalFormView, Configuracion)

from .models import (Estado, Proyecto, Proyecto_Objetivo, Proyecto_Meta, Proyecto_Fase,
	Proyecto_Tarea, Comentario)
from .forms import (ProyectoForm, Proyecto_Objetivo_ModelForm, Proyecto_Meta_ModelForm,
    Proyecto_Fase_ModelForm, Proyecto_Tarea_ModelCreateForm, Proyecto_Tarea_ModelUpdateForm)

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
        context['imagenes'] = {
            'update': 'seguimiento_update.png',
            'delete': 'seguimiento_delete.png',
        }
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
                'nombre': _('Bloquea'),
                'funcion': 'get_bloquea',
            },
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
    template_name = 'seguimiento/detail.html'
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
        context['forms'] = [
            {
                
                'modal':    'proyecto_objetivo', 
                'action':   reverse_lazy('seguimiento:create_proyectoobjetivo')+f'?next='+self.object.url_detail() if self.object.get_modificable() else None,
                'display':  _('Definición de objetivos'),
                'link_img': 'seguimiento_objetivo_add.png',
                'form':     Proyecto_Objetivo_ModelForm('proyecto', instance=Proyecto_Objetivo(proyecto=self.object)),
                'opciones': DISPLAYS['forms'],
            },
            {
                'modal':    'proyecto_meta', 
                'action':   reverse_lazy('seguimiento:create_proyectometa')+f'?next='+self.object.url_detail() if self.object.get_modificable() else None,
                'display':  _('Definición de metas'),
                'link_img': 'seguimiento_meta_add.png',
                'form':     Proyecto_Meta_ModelForm('proyecto', instance=Proyecto_Meta(proyecto=self.object)),
                'opciones': DISPLAYS['forms'],
            },
            {
                'modal':    'proyecto_fase', 
                'action':   reverse_lazy('seguimiento:create_proyectofase')+f'?next='+self.object.url_detail() if self.object.get_modificable() else None,
                'display':  _('Definición de fases'),
                'link_img': 'seguimiento_fase_add.png',
                'form':     Proyecto_Fase_ModelForm('proyecto', instance=Proyecto_Fase(proyecto=self.object)),
                'opciones': DISPLAYS['forms'],
            },
            {
                'modal':    'proyecto_tarea', 
                'action':   reverse_lazy('seguimiento:create_proyectotarea')+f'?next='+self.object.url_detail() if self.object.get_modificable() else None,
                'display':  _('Definición de tareas'),
                'link_img': 'seguimiento_tarea_add.png',
                'form':     Proyecto_Tarea_ModelCreateForm(self.object),
                'opciones': DISPLAYS['forms'],
            },
        ]
        context['tables'] = [
            {   
                'fin_columna':  2, #se coloca el indice del ultimo objeto de la fila
                'tipo':         'table',
                'title':        _('Objetivos'),
                'enumerar':     1,
                'object_list':  Proyecto_Objetivo.objects.filter(proyecto=self.object).order_by('descripcion'),
                'campos':       ['descripcion',],
                'campos_extra': [
                    {
                        'nombre':   _('Alcanzado'), #display
                        # valor, constante o funcion 
                        'funcion': 'get_alcanzado',  
                    },
                ],
                'opciones':     _('Opciones'),
                #Si tiene next, redirecciona a esa pagina
                'next':         self.object.url_detail(),
            },
            {
                'fin_columna': 2, #se coloca el indice del ultimo objeto de la fila
                'tipo':         'table',
                'title':        _('Metas'),
                'enumerar':     1,
                'object_list':  Proyecto_Meta.objects.filter(proyecto=self.object).order_by('descripcion'),
                'campos':       ['descripcion',],
                'campos_extra': [
                    {
                        'nombre':   _('Alcanzado'), #display
                        # valor, constante o funcion 
                        'funcion': 'get_alcanzado',  
                    },
                ],
                'opciones':     _('Opciones'),
                #Si tiene next, redirecciona a esa pagina
                'next':         self.object.url_detail(),
            },
            {
                'tipo':         'accordion',
                'enumerar':     -1,
                'object_list':  Proyecto_Fase.objects.filter(proyecto=self.object).order_by('correlativo'),
                'func_extra':   'get_porcentaje_completado',
                'campos':       ['descripcion', 'complejidad'],
                'campos_extra': [
                    {
                        # valor, constante o funcion 
                        #'nombre':   _('%Completado'), #display
                        #'funcion': 'get_porcentaje_completado',  
                    },
                ],
                'opciones':     _('Opciones'),
                #Si tiene next, redirecciona a esa pagina
                'next':         self.object.url_detail(),
            },
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
    permission_required = 'seguimiento.delete_proyecto_objetivo'
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



