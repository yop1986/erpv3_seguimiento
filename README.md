# ERPv3 - Seguimiento

## Desarrollo

### Configuración del Ambiente

Esta aplicacion depende del [Modulo de usuarios](https://github.com/yop1986/erpv3_usuarios) 
por lo que es necesario instalar este y sus dependencias previamente.

Desde la consola de Git se procede a clonar este repositorio, en la raiz del 
proyecto.

    $ git clone https://github.com/yop1986/erpv3_seguimiento.git seguimiento

#### Settings

Es necesario modificar el archivo **settings.py** del proyecto general con la
siguiente informacion:

    INSTALLED_APPS = [
        ...
        'seguimiento',
    ]

    INFORMACION_APLICACIONES = {
        'seguimiento': {
            'nombre':       'Seguimiento',
            'descripcion':  _('Aplicación para seguimiento de proyectos y activiades.'),
            'url':          reverse_lazy('seguimiento:index'),
            'imagen':       'seguimiento_seguimiento.png',
        },
    }

#### Urls

Posterior a esta configuracion es necesario agregar las urls al proyecto base __< Base >/urls.py__

    path('seguimiento/', include('seguimiento.urls')),

#### Comandos adicionales de Django

    (venv) ERPv3> python manage.py check
    (venv) ERPv3> python manage.py migrate qliksense
