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
]