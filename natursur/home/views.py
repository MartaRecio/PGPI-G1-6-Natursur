from django.shortcuts import render
from django.http import HttpRequest, HttpResponse

# Create your views here.

def home_view(request: HttpRequest) -> HttpResponse:
    """
    Renderiza la plantilla base de la página de inicio.
    """
    # Busca la plantilla en 'home/templates/home/index.html'
    return render(request, 'home/index.html', {})

def services_view(request: HttpRequest) -> HttpResponse:
    """
    Renderiza la plantilla servicios de la página de inicio.
    """
    # Busca la plantilla en 'home/templates/services.html'
    return render(request, 'services.html', {})