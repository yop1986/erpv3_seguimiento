from django.urls import path, include

from . import views

app_name = 'seguimiento'

urlpatterns = [
    path('', views.IndexTemplateView.as_view(), name='index'),

    path('estado/', views.EstadoListView.as_view(), name='list_estado'),
    path('estado/nueva/', views.EstadoCreateView.as_view(), name='create_estado'),
    path('estado/ver/<uuid:pk>', views.EstadoDetailView.as_view(), name='detail_estado'),
    path('estado/actualizar/<uuid:pk>', views.EstadoUpdateView.as_view(), name='update_estado'),
    path('estado/eliminar/<uuid:pk>', views.EstadoDeleteView.as_view(), name='delete_estado'),

    path('proyecto/', views.ProyectoListView.as_view(), name='list_proyecto'),
    path('proyecto/nueva/', views.ProyectoCreateView.as_view(), name='create_proyecto'),
    path('proyecto/ver/<uuid:pk>', views.ProyectoDetailView.as_view(), name='detail_proyecto'),
    path('proyecto/actualizar/<uuid:pk>', views.ProyectoUpdateView.as_view(), name='update_proyecto'),
    path('proyecto/eliminar/<uuid:pk>', views.ProyectoDeleteView.as_view(), name='delete_proyecto'),

    path('objetivo/nuevo/', views.Proyecto_ObjetivoFormView.as_view(), name='create_proyectoobjetivo'),
    path('objetivo/actualizar/<uuid:pk>', views.Proyecto_ObjetivoUpdateView.as_view(), name='update_proyectoobjetivo'),
    path('objetivo/eliminar/<uuid:pk>', views.Proyecto_ObjetivoDeleteView.as_view(), name='delete_proyectoobjetivo'),

    path('meta/nueva/', views.Proyecto_MetaFormView.as_view(), name='create_proyectometa'),
    path('meta/actualizar/<uuid:pk>', views.Proyecto_MetaUpdateView.as_view(), name='update_proyectometa'),
    path('meta/eliminar/<uuid:pk>', views.Proyecto_MetaDeleteView.as_view(), name='delete_proyectometa'),

    path('fase/nueva/', views.Proyecto_FaseFormView.as_view(), name='create_proyectofase'),
    path('fase/actualizar/<uuid:pk>', views.Proyecto_FaseUpdateView.as_view(), name='update_proyectofase'),
    path('fase/eliminar/<uuid:pk>', views.Proyecto_FaseDeleteView.as_view(), name='delete_proyectofase'),

    path('tarea/nueva/', views.Proyecto_TareaFormView.as_view(), name='create_proyectotarea'),
    path('tarea/actualizar/<uuid:pk>', views.Proyecto_TareaUpdateView.as_view(), name='update_proyectotarea'),
    path('tarea/eliminar/<uuid:pk>', views.Proyecto_TareaDeleteView.as_view(), name='delete_proyectotarea'),

]


    




    
    