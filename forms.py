from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

from django_ckeditor_5.widgets import CKEditor5Widget

from usuarios.models import Usuario
from .models import (Proyecto, Proyecto_Usuario, Proyecto_Objetivo, 
    Proyecto_Meta, Proyecto_Fase, Proyecto_Tarea, Proyecto_Actividad, 
    Proyecto_Pendiente, Comentario)


class DateInput(forms.DateInput):
    input_type = 'date'

class DynamicChoiceField(forms.ChoiceField):
    def clean(self, value):
        return value


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
                self.fields['proyecto'].queryset = self.fields['proyecto'].queryset.filter(id=self.initial['proyecto'])
                self.initial['correlativo'] = Proyecto_Fase.objects.filter(proyecto_id=self.initial['proyecto']).count()+1
        except:
            pass

class Proyecto_Tarea_ModelForm(forms.ModelForm):
    class Meta:
        model = Proyecto_Tarea
        fields = ['fase', 'descripcion', 'prioridad', 'complejidad', 'finalizado']

    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)
        try:
            if args and 'nuevo' in args:
                self.fields['fase'].queryset = Proyecto_Fase.objects.filter(proyecto=args[1], cerrado=False).order_by('correlativo')
                self.fields['finalizado'].widget = forms.HiddenInput()
            else:
                self.fields['fase'].disabled = True
                self.fields['fase'].widget.attrs["readonly"] = True
                self.fields['fase'].queryset = kwargs['instance'].fase
        except:
            pass

class Proyecto_Actividad_ModelForm(forms.ModelForm):
    fase = DynamicChoiceField(label=_('Fase'))

    class Meta:
        model = Proyecto_Actividad
        fields = ['fase', 'tarea', 'descripcion']
        
    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)
        try:
            if kwargs and kwargs['instance']:
                tarea = kwargs['instance'].tarea
                fases = [(str(f.id), f.descripcion) for f in Proyecto_Fase.objects.filter(proyecto=tarea.fase.proyecto, cerrado=False).order_by('descripcion')]
                fases.insert(0, ('', '------------'))
                self.initial['fase'] = tarea.fase.id
                self.fields['tarea'].queryset = Proyecto_Tarea.objects.filter(fase=tarea.fase)
            else:
                fases = [(str(f.id), f.descripcion) for f in Proyecto_Fase.objects.filter(proyecto=args[0], cerrado=False).order_by('descripcion')]
                fases.insert(0, ('', '------------'))
                self.fields['tarea'].queryset = Proyecto_Tarea.objects.none()
            self.fields['fase'].choices = fases
        except :
            pass

class Proyecto_Pendiente_ModelForm(forms.ModelForm):
    class Meta:
        model = Proyecto_Pendiente
        fields = ['descripcion', 'responsable', 'finalizado', 'proyecto']
        widgets = {'proyecto': forms.HiddenInput()}
        
    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)
        try:
            if args and 'nuevo' in args:
                self.fields['finalizado'].widget = forms.HiddenInput()
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

class Proyecto_Comentario_ModelForm(forms.ModelForm):
    class Meta:
        model = Comentario
        fields = ['descripcion', 'tipo', 'obj_id']
        widgets = {'tipo': forms.HiddenInput(), 'obj_id': forms.HiddenInput()}
    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)