from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

from django_ckeditor_5.widgets import CKEditor5Widget

from usuarios.models import Usuario
from .models import (Proyecto, Proyecto_Usuario, Proyecto_Objetivo, 
    Proyecto_Meta, Proyecto_Fase, Proyecto_Tarea, Comentario)


class DateInput(forms.DateInput):
    input_type = 'date'


class ProyectoForm(forms.ModelForm): 
    class Meta:
        model = Proyecto
        fields = ('nombre', 'descripcion', 'enlace_cloud', 'finicio', 'ffin', 'estado', 'publico')
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

class Proyecto_Tarea_ModelCreateForm(forms.ModelForm):
    class Meta:
        model = Proyecto_Tarea
        fields = ['fase', 'descripcion', 'complejidad']

    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)
        try:
            self.fields['fase'].queryset = Proyecto_Fase.objects.filter(proyecto=args[0]).order_by('correlativo')
        except:
            pass

class Proyecto_Tarea_ModelUpdateForm(forms.ModelForm):
    class Meta:
        model = Proyecto_Tarea
        fields = ['fase', 'descripcion', 'complejidad', 'finalizado']

    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)
        try:
            tarea = kwargs['instance']
            fases = Proyecto_Fase.objects.filter(proyecto=tarea.fase.proyecto)
            #self.fields['fase'].disabled = True
            #self.fields['descripcion'].widget.attrs["readonly"] = True
            self.fields['fase'].queryset = fases
        except:
            pass

class Proyecto_Usuario_ModelForm(forms.ModelForm):
    class Meta:
        model = Proyecto_Usuario
        fields = ['proyecto', 'usuario']
        #widgets = {'proyecto': forms.HiddenInput()}
       
    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)
        try:
            if(args and args[0]=='proyecto'):
                self.fields['proyecto'].queryset = self.fields['proyecto'].queryset.filter(id=self.initial['proyecto'])
                self.fields['proyecto'].widget = forms.HiddenInput()
                usrs = Proyecto_Usuario.objects.filter(proyecto=self.initial['proyecto']).values_list('usuario')
                self.fields['usuario'].queryset = Usuario.objects.filter(is_active=True).exclude(id__in=usrs)
        except:
            pass

class Proyecto_Comentario_ModelForm(forms.ModelForm):
    class Meta:
        model = Comentario
        fields = ['descripcion', 'tipo', 'obj_id']
        widgets = {'tipo': forms.HiddenInput(), 'obj_id': forms.HiddenInput()}
    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)