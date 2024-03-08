from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

from django_ckeditor_5.widgets import CKEditor5Widget

from .models import Proyecto


class DateInput(forms.DateInput):
    input_type = 'date'


class ProyectoForm(forms.ModelForm): 
    class Meta:
        model = Proyecto
        fields = ('nombre', 'descripcion', 'finicio', 'ffin', 'estado')
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
