from datetime import datetime

from django import forms
from django.db.models import Max, Q
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

from django_ckeditor_5.widgets import CKEditor5Widget

from usuarios.models import Usuario
from .models import (Proyecto, Proyecto_Usuario, Proyecto_Objetivo, 
    Proyecto_Meta, Proyecto_Fase, Proyecto_Tarea, Proyecto_Actividad, 
    Proyecto_Etiqueta, Comentario)


class DateInput(forms.DateInput):
    input_type = 'date'

class DynamicChoiceField(forms.ChoiceField):
    def clean(self, value):
        return value



def elementos_combo(lista, vacio=True, extra=[]):
    datos = []
    if vacio:
        datos = [('', '---------'), ]
    if lista:
        datos += [ (elemento[0], elemento[1]) for elemento in lista ]
    if extra:
        datos += extra
    return datos



class ProyectoForm(forms.ModelForm): 
    class Meta:
        model = Proyecto
        fields = ('nombre', 'descripcion', 'enlace_cloud', 'finicio', 'ffin', 
            'lider', 'tipo', 'origen', 'pm', 'estado', 'publico')
        widgets = {
            'finicio': DateInput(format='%Y-%m-%d'),
            'ffin': DateInput(format='%Y-%m-%d'),
            'descripcion': CKEditor5Widget(
                  attrs={"class": "django_ckeditor_5"}, config_name="default"
              ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)
        try:
            self.fields['estado'].queryset = self.fields['estado'].queryset.filter(vigente=True)
            self.fields['tipo'].queryset = self.fields['tipo'].queryset.filter(vigente=True)
            self.fields['origen'].queryset = self.fields['origen'].queryset.filter(vigente=True)
            self.fields['pm'].queryset = self.fields['pm'].queryset.filter(vigente=True)
            self.fields['lider'].queryset = self.fields['lider'].queryset.filter(is_active=True)
        except:
            pass

class Proyecto_Objetivo_ModelForm(forms.ModelForm):
    class Meta:
        model = Proyecto_Objetivo
        fields = ['descripcion', 'alcanzado', 'proyecto']
        #widgets = {'proyecto': forms.HiddenInput()}
       
    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)
        try:
            if(args and args[0]=='proyecto'):
                self.fields['proyecto'].queryset = self.fields['proyecto'].queryset.filter(id=self.initial['proyecto'])
                self.fields['proyecto'].widget = forms.HiddenInput()
        except:
            pass

class Proyecto_Meta_ModelForm(forms.ModelForm):
    class Meta:
        model = Proyecto_Meta
        fields = ['descripcion', 'alcanzado', 'proyecto']
        #widgets = {'proyecto': forms.HiddenInput()}
       
    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)
        try:
            if(args and args[0]=='proyecto'):
                self.fields['proyecto'].queryset = self.fields['proyecto'].queryset.filter(id=self.initial['proyecto'])
                self.fields['proyecto'].widget = forms.HiddenInput()
        except:
            pass

class Proyecto_Fase_ModelForm(forms.ModelForm):
    class Meta:
        model = Proyecto_Fase
        fields = ['correlativo', 'descripcion', 'proyecto']
        widgets = {'correlativo':forms.HiddenInput(), 'proyecto': forms.HiddenInput()}
       
    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)
        try:
            if(args and args[0]=='proyecto'):
                max_correlativo = Proyecto_Fase.objects.filter(proyecto_id=self.initial['proyecto']).aggregate(Max('correlativo'))['correlativo__max']
                max_correlativo = max_correlativo if max_correlativo else 0
                self.fields['proyecto'].queryset = self.fields['proyecto'].queryset.filter(id=self.initial['proyecto'])
                self.initial['correlativo'] = max_correlativo+1
        except:
            pass

class Proyecto_Tarea_ModelForm(forms.ModelForm):
    class Meta:
        model = Proyecto_Tarea
        fields = ['fase', 'descripcion', 'prioridad', 'complejidad', 'etiqueta']

    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)
        try:
            if args and 'nuevo' in args:
                self.fields['fase'].queryset = Proyecto_Fase.objects.filter(proyecto=args[1], cerrado=False).order_by('descripcion')
                self.fields['etiqueta'].queryset = self.fields['etiqueta'].queryset.filter(proyecto = args[1]).order_by('descripcion')
            elif kwargs['instance']:
                fase = Proyecto_Fase.objects.get(id = self.initial['fase'])
                self.fields['fase'].queryset = Proyecto_Fase.objects.filter(proyecto=fase.proyecto).order_by('descripcion')
                self.fields['etiqueta'].queryset = self.fields['etiqueta'].queryset.filter(proyecto = fase.proyecto).order_by('descripcion')

                #self.fields['fase'].disabled = True
                #self.fields['fase'].widget.attrs["readonly"] = True
        except:
            pass

class Proyecto_Actividad_ModelForm(forms.ModelForm):
    fase = DynamicChoiceField(label=_('Fase'))

    class Meta:
        model = Proyecto_Actividad
        fields = ['fase', 'tarea', 'creacion', 'descripcion', 'responsable', 'resolucion', 'finalizado']
        widgets = { 'creacion': DateInput(format='%Y-%m-%d'), }
        
    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)
        try:
            if kwargs and 'instance' in kwargs:
                tarea   = kwargs['instance'].tarea
                proyecto = tarea.fase.proyecto
                usrs    = Proyecto_Usuario.objects.filter(proyecto = tarea.fase.proyecto).values_list('usuario_id')
                self.fields['fase'].choices = elementos_combo([(str(f.id), f.descripcion) for f in Proyecto_Fase.objects.filter(proyecto = proyecto, cerrado=False).order_by('descripcion')])
                self.fields['tarea'].queryset = Proyecto_Tarea.objects.filter(fase = tarea.fase).order_by('descripcion')
                
                self.fields['fase'].initial = tarea.fase.id

                #self.fields['fase'].disabled = True
                #self.fields['fase'].widget.attrs["readonly"] = True
            else:
                usrs    = Proyecto_Usuario.objects.filter(proyecto = args[0]).values_list('usuario_id')
                self.fields['fase'].choices = elementos_combo([(str(f.id), f.descripcion) for f in Proyecto_Fase.objects.filter(proyecto=args[0], cerrado=False).order_by('descripcion')])
                self.fields['tarea'].queryset = Proyecto_Tarea.objects.none()
                
                self.fields['creacion'].initial = datetime.now()

                self.fields['resolucion'].widget = forms.HiddenInput()
                self.fields['finalizado'].widget = forms.HiddenInput()
            self.fields['responsable'].queryset = Usuario.objects.filter(id__in = usrs)
        except :
            pass

class Proyecto_Usuario_ModelForm(forms.ModelForm):
    class Meta:
        model = Proyecto_Usuario
        fields = ['proyecto', 'usuario']
       
    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)
        try:
            if(args and args[0]=='proyecto'):
                self.fields['proyecto'].queryset = self.fields['proyecto'].queryset.filter(id=self.initial['proyecto'])
                self.fields['proyecto'].widget = forms.HiddenInput()
                usrs = Proyecto_Usuario.objects.filter(proyecto=self.initial['proyecto']).values_list('usuario')
                self.fields['usuario'].queryset = Usuario.objects.filter(is_active=True).exclude(id__in=usrs)\
                    .only('username', 'first_name', 'last_name')
        except:
            pass

class Proyecto_Etiqueta_ModelForm(forms.ModelForm):
    class Meta:
        model = Proyecto_Etiqueta
        fields = ['proyecto', 'descripcion']
       
    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)
        try:
            if(args and args[0]=='proyecto'):
                self.fields['proyecto'].queryset = self.fields['proyecto'].queryset.filter(id=self.initial['proyecto'])
                self.fields['proyecto'].widget = forms.HiddenInput()
        except:
            pass

class Proyecto_Comentario_ModelForm(forms.ModelForm):
    class Meta:
        model = Comentario
        fields = ['descripcion', 'tipo', 'obj_id']
        widgets = {'tipo': forms.HiddenInput(), 'obj_id': forms.HiddenInput()}
    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)

class Proyecto_Reporte_Avances(forms.Form):
    proyecto= forms.ChoiceField(label=_('Proyecto'), required=True)
    
    def __init__(self, *args, **kwargs):
        usr_id = kwargs.pop('usuario')
        super().__init__(**kwargs)
        
        proys = Proyecto_Usuario.objects.filter(usuario_id=usr_id).values_list('proyecto')
        
        try:
            self.fields['proyecto'].choices = elementos_combo(Proyecto.objects.filter(Q(publico=True)|Q(id__in=proys), estado__bloquea=False)\
                .values_list('id', 'nombre'))
        except:
            pass

class Proyecto_Reportes_Actividades(forms.Form):
    proyecto= forms.ChoiceField(label=_('Proyecto'), required=True)
    fini    = forms.DateField(label=_('Fecha Inicio'))
    ffin    = forms.DateField(label=_('Fecha Fin'))
    
    def __init__(self, *args, **kwargs):
        usr_id = kwargs.pop('usuario')
        super().__init__(**kwargs)
        
        proys   = Proyecto_Usuario.objects.filter(usuario_id=usr_id).values_list('proyecto')

        try:
            self.fields['proyecto'].choices = elementos_combo(Proyecto.objects.filter(Q(publico=True)|Q(id__in=proys), estado__bloquea=False)\
                .values_list('id', 'nombre'))
            #self.fields['usuario'].choices  = elementos_combo(None)
            self.fields['fini'].widget      = DateInput(format='%Y-%m-%d')
            self.fields['ffin'].widget      = DateInput(format='%Y-%m-%d')
        except:
            pass



