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
#
#    path('area_tipolicencia/nueva/', views.Area_TipoLicenciaFormView.as_view(), name='create_areatipo'),
#    path('area_tipolicencia/actualizar/<uuid:pk>', views.Area_TipoLicenciaUpdateView.as_view(), name='update_areatipo'),
#    path('area_tipolicencia/eliminar/<uuid:pk>', views.Area_TipoLicenciaDeleteView.as_view(), name='delete_areatipo'),
#
#    path('usuario/', views.UsuarioListView.as_view(), name='list_usuario'),
#    path('usuario/nuevo/', views.UsuarioCreateView.as_view(), name='create_usuario'),
#    path('usuario/actualizar/<uuid:pk>', views.UsuarioUpdateView.as_view(), name='update_usuario'),
#    path('usuario/eliminar/<uuid:pk>', views.UsuarioDeleteView.as_view(), name='delete_usuario'),
#
#    path('stream/', views.StreamListView.as_view(), name='list_stream'),
#    path('stream/ver/<uuid:pk>', views.StreamDetailView.as_view(), name='detail_stream'),
#    path('qlikapi/recargar/', views.refresh_all, name='refresh_all_data'),
#
#    path('modelo/ver/<uuid:pk>', views.ModelDetailView.as_view(), name='detail_modelo'),
]


    




    
    