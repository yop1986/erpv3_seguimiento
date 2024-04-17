from django.urls import path, include

from . import views

app_name = 'seguimiento'

urlpatterns = [
    path('', views.IndexTemplateView.as_view(), name='index'),

    path('estado/', views.EstadoListView.as_view(), name='list_estado'),
    path('estado/nuevo/', views.EstadoCreateView.as_view(), name='create_estado'),
    path('estado/ver/<uuid:pk>', views.EstadoDetailView.as_view(), name='detail_estado'),
    path('estado/actualizar/<uuid:pk>', views.EstadoUpdateView.as_view(), name='update_estado'),
    path('estado/eliminar/<uuid:pk>', views.EstadoDeleteView.as_view(), name='delete_estado'),

    path('tipo/', views.Tipo_ProyectoListView.as_view(), name='list_tipo_proyecto'),
    path('tipo/nuevo/', views.Tipo_ProyectoCreateView.as_view(), name='create_tipo_proyecto'),
    path('tipo/ver/<uuid:pk>', views.Tipo_ProyectoDetailView.as_view(), name='detail_tipo_proyecto'),
    path('tipo/actualizar/<uuid:pk>', views.Tipo_ProyectoUpdateView.as_view(), name='update_tipo_proyecto'),
    path('tipo/eliminar/<uuid:pk>', views.Tipo_ProyectoDeleteView.as_view(), name='delete_tipo_proyecto'),

    path('origen/', views.Origen_ProyectoListView.as_view(), name='list_origen_proyecto'),
    path('origen/nuevo/', views.Origen_ProyectoCreateView.as_view(), name='create_origen_proyecto'),
    path('origen/ver/<uuid:pk>', views.Origen_ProyectoDetailView.as_view(), name='detail_origen_proyecto'),
    path('origen/actualizar/<uuid:pk>', views.Origen_ProyectoUpdateView.as_view(), name='update_origen_proyecto'),
    path('origen/eliminar/<uuid:pk>', views.Origen_ProyectoDeleteView.as_view(), name='delete_origen_proyecto'),

    path('pm/', views.PM_ProyectoListView.as_view(), name='list_pm_proyecto'),
    path('pm/nuevo/', views.PM_ProyectoCreateView.as_view(), name='create_pm_proyecto'),
    path('pm/ver/<uuid:pk>', views.PM_ProyectoDetailView.as_view(), name='detail_pm_proyecto'),
    path('pm/actualizar/<uuid:pk>', views.PM_ProyectoUpdateView.as_view(), name='update_pm_proyecto'),
    path('pm/eliminar/<uuid:pk>', views.PM_ProyectoDeleteView.as_view(), name='delete_pm_proyecto'),

    path('proyecto/', views.ProyectoListView.as_view(), name='list_proyecto'),
    path('proyecto/nuevo/', views.ProyectoCreateView.as_view(), name='create_proyecto'),
    path('proyecto/ver/<uuid:pk>', views.ProyectoDetailView.as_view(), name='detail_proyecto'),
    path('proyecto/ver/<uuid:pk>/<uuid:faseactiva>', views.ProyectoDetailView.as_view(), name='detail_proyecto'),
    path('proyecto/ver/<uuid:pk>/<str:opcion>', views.ProyectoDetailView.as_view(), name='detail_proyecto'),
    path('proyecto/actualizar/<uuid:pk>', views.ProyectoUpdateView.as_view(), name='update_proyecto'),
    path('proyecto/eliminar/<uuid:pk>', views.ProyectoDeleteView.as_view(), name='delete_proyecto'),

    path('usuario/nuevo/', views.Proyecto_UsuarioFormView.as_view(), name='create_proyectousuario'),
    path('usuario/eliminar/<uuid:pk>', views.Proyecto_UsuarioDeleteView.as_view(), name='delete_proyectousuario'),

    path('objetivo/nuevo/', views.Proyecto_ObjetivoFormView.as_view(), name='create_proyectoobjetivo'),
    path('objetivo/actualizar/<uuid:pk>', views.Proyecto_ObjetivoUpdateView.as_view(), name='update_proyectoobjetivo'),
    path('objetivo/eliminar/<uuid:pk>', views.Proyecto_ObjetivoDeleteView.as_view(), name='delete_proyectoobjetivo'),

    path('meta/nueva/', views.Proyecto_MetaFormView.as_view(), name='create_proyectometa'),
    path('meta/actualizar/<uuid:pk>', views.Proyecto_MetaUpdateView.as_view(), name='update_proyectometa'),
    path('meta/eliminar/<uuid:pk>', views.Proyecto_MetaDeleteView.as_view(), name='delete_proyectometa'),

    path('fase/nueva/', views.Proyecto_FaseFormView.as_view(), name='create_proyectofase'),
    path('fase/actualizar/<uuid:pk>', views.Proyecto_FaseUpdateView.as_view(), name='update_proyectofase'),
    path('fase/eliminar/<uuid:pk>', views.Proyecto_FaseDeleteView.as_view(), name='delete_proyectofase'),

    path('tarea/', views.Proyecto_TareaListView.as_view(), name='list_proyectotarea'),
    path('tarea/nueva/', views.Proyecto_TareaFormView.as_view(), name='create_proyectotarea'),
    path('tarea/actualizar/<uuid:pk>', views.Proyecto_TareaUpdateView.as_view(), name='update_proyectotarea'),
    path('tarea/eliminar/<uuid:pk>', views.Proyecto_TareaDeleteView.as_view(), name='delete_proyectotarea'),

    path('actividad/nueva/', views.Proyecto_ActividadFormView.as_view(), name='create_proyectoactividad'),
    path('actividad/actualizar/<uuid:pk>', views.Proyecto_ActividadUpdateView.as_view(), name='update_proyectoactividad'),
    path('actividad/eliminar/<uuid:pk>', views.Proyecto_ActividadDeleteView.as_view(), name='delete_proyectoactividad'),
    path('fase/tarea/', views.combo_fase_tarea, name='combo_fasetarea'),
    path('accordion/tarea/actividad/', views.accordion_tarea_actividad, name='accordion_tareaactividad'),

    path('pendiente/nueva/', views.Proyecto_PendienteFormView.as_view(), name='create_proyectopendiente'),
    path('pendiente/actualizar/<uuid:pk>', views.Proyecto_PendienteUpdateView.as_view(), name='update_proyectopendiente'),
    path('pendiente/eliminar/<uuid:pk>', views.Proyecto_PendienteDeleteView.as_view(), name='delete_proyectopendiente'),
    path('pendiente/pendiente/', views.tabla_pendiente, name='tabla_pendiente'),

    path('comentario/nuevo/', views.Comentario_FormView.as_view(), name='create_comentario'),
    path('comentario/<uuid:pk>', views.ComentarioListView.as_view(), name='list_comentario'),
]


    




    
    