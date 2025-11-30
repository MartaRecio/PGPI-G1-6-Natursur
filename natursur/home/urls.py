from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('services/', views.services_view, name='services'),

    # Autenticación
    path('registro/', views.registro_view, name='registro'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Perfil y gestión de citas
    path('perfil/', views.perfil_usuario, name='perfil'),
    path('cambiar-password/', views.cambiar_password, name='cambiar_password'),
    path('cancelar-cita/<int:cita_id>/', views.cancelar_cita, name='cancelar_cita'),

    # Calendario y citas
    path('calendario/', views.calendario_mensual, name='calendario'),
    path('calendario/horas-ocupadas/', views.horas_ocupadas, name='horas_ocupadas'),
    path('crear-cita-final/', views.crear_cita_final, name='crear_cita_final'),

    # Perfil administrador
    path('admin/cancelar-cita/<int:cita_id>/', views.admin_cancelar_cita, name='admin_cancelar_cita'),
    path('admin/editar-perfil/', views.admin_editar_perfil, name='admin_editar_perfil'),
    path('admin/cambiar-password/', views.admin_cambiar_password, name='admin_cambiar_password'),
    path('admin/gestion-citas/', views.admin_gestion_citas, name='admin_gestion_citas'),

    # Productos Herbalife
    path("productos/", views.lista_productos, name="lista_productos"),

    # Promociones
    path('promociones/nueva/', views.crear_promocion, name='crear_promocion'),
    path('promociones/toggle/<int:pk>/', views.toggle_promocion, name='toggle_promocion'),
    path('promociones/eliminar/<int:pk>/', views.eliminar_promocion, name='eliminar_promocion'),

    # Administración de mensajes en la cabecera
    path('directo/update/', views.update_Directo, name='update_Directo'),
    path('directo/delete/', views.delete_Directo, name='delete_Directo'),
]