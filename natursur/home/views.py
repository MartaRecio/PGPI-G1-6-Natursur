from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import Cita
from datetime import timedelta, datetime, date
from .models import Producto

User = get_user_model()

def home_view(request: HttpRequest) -> HttpResponse:
    # Renderiza la plantilla base de la página de inicio.
    return render(request, 'home/index.html', {})


def services_view(request: HttpRequest) -> HttpResponse:
    # Renderiza la plantilla servicios de la página de inicio.
    return render(request, 'services.html', {})



# VISTAS DE AUTENTICACIÓN:

@csrf_protect
def registro_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        
        if not all([username, email, password1]):
            messages.error(request, 'Usuario, email y contraseña son obligatorios.')
        elif len(password1) < 3:
            messages.error(request, 'La contraseña debe tener al menos 3 caracteres.')
        elif password1 != password2:
            messages.error(request, 'Las contraseñas no coinciden.')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Este usuario ya existe.')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'Este email ya está registrado.')
        else:
            try:
                user = User.objects.create_user(username=username, email=email, password=password1)
                user = authenticate(username=username, password=password1)
                if user:
                    login(request, user)
                    messages.success(request, '¡Registro exitoso! Bienvenido/a.')
                    return redirect('home')
            except Exception as e:
                messages.error(request, f'Error creando usuario: {str(e)}')
    
    return render(request, 'home/index.html')


@csrf_protect
def login_view(request):
    if request.method == 'POST':
        username_or_email = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(username=username_or_email, password=password)
        
        if user is None:
            try:
                user_by_email = User.objects.get(email=username_or_email)
                user = authenticate(username=user_by_email.username, password=password)
            except User.DoesNotExist:
                user = None

        if user:
            login(request, user)
            messages.success(request, f'¡Bienvenido/a de nuevo, {user.username}!')
            return redirect('home')
        else:
            messages.error(request, 'Usuario/email o contraseña incorrectos.')
    
    return redirect('home')


def logout_view(request):
    logout(request)
    messages.success(request, 'Has cerrado sesión correctamente.')
    return redirect('home')

@login_required
def perfil_usuario(request):
    if request.method == 'POST':
        cambios_realizados = False
        nuevo_username = request.POST.get('username')
        telefono = request.POST.get('telefono')
        fecha_nacimiento = request.POST.get('fecha_nacimiento')
        
        if nuevo_username and nuevo_username != request.user.username:
            request.user.username = nuevo_username
            cambios_realizados = True
        
        telefono_vacio = telefono if telefono else None
        if telefono != request.user.telefono:
            request.user.telefono = telefono_vacio
            cambios_realizados = True
        
        nueva_fecha_nacimiento = fecha_nacimiento if fecha_nacimiento else None
        if nueva_fecha_nacimiento != request.user.fecha_nacimiento:
            request.user.fecha_nacimiento = nueva_fecha_nacimiento
            cambios_realizados = True

        if cambios_realizados:
            request.user.save()
            messages.success(request, 'Datos actualizados correctamente')
    
    ahora = timezone.now()
    
    citas_programadas = Cita.objects.filter(
        user=request.user,
        fecha__gte=ahora
    ).order_by('fecha')
    
    for cita in citas_programadas:
        cita.puede_cancelar = (cita.fecha - ahora) > timedelta(hours=24)
    
    citas_pasadas = Cita.objects.filter(
        user=request.user,
        fecha__lt=ahora
    ).order_by('-fecha')[:10]
    
    return render(request, 'home/perfil.html', {
        'citas_programadas': citas_programadas,
        'citas_pasadas': citas_pasadas
    })

@login_required
def cambiar_password(request):
    """
    Vista para cambiar la contraseña del usuario
    """
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        if request.user.check_password(current_password):
            if new_password == confirm_password:
                request.user.set_password(new_password)
                request.user.save()
                update_session_auth_hash(request, request.user)
                messages.success(request, 'Contraseña cambiada correctamente')
            else:
                messages.error(request, 'Las contraseñas no coinciden')
        else:
            messages.error(request, 'Contraseña actual incorrecta')
    
    return redirect('perfil')

@login_required
def cancelar_cita(request, cita_id):
    try:
        cita = Cita.objects.get(id=cita_id, user=request.user)
        if (cita.fecha - timezone.now()) > timedelta(hours=24):
            cita.delete()
            messages.success(request, 'Cita cancelada correctamente')
        else:
            messages.error(request, 'No se puede cancelar con menos de 24 horas de antelación')
    except Cita.DoesNotExist:
        messages.error(request, 'Cita no encontrada')
    
    return redirect('perfil')


@login_required
def calendario_mensual(request):
    año = int(request.GET.get('año', timezone.now().year))
    mes = int(request.GET.get('mes', timezone.now().month))

    primer_dia = date(año, mes, 1)
    if mes == 12:
        ultimo_dia = date(año + 1, 1, 1) - timedelta(days=1)
    else:
        ultimo_dia = date(año, mes + 1, 1) - timedelta(days=1)
    
    hoy = timezone.now().date()
    max_fecha = hoy + timedelta(days=60)
    
    mes_anterior = date(año, mes, 1) - timedelta(days=1)
    mes_siguiente = date(año, mes, 1) + timedelta(days=32)
    mes_siguiente = date(mes_siguiente.year, mes_siguiente.month, 1)
    
    if mes_siguiente > max_fecha:
        mes_siguiente = None
    
    meses_espanol = {
        1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril', 5: 'Mayo', 6: 'Junio',
        7: 'Julio', 8: 'Agosto', 9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
    }
    
    dias = []
    primer_dia_semana = primer_dia.weekday()
    
    for i in range(primer_dia_semana):
        dias.append({'vacio': True})
    
    dia_actual = primer_dia
    while dia_actual <= ultimo_dia:
        es_fin_de_semana = dia_actual.weekday() in [5, 6]
        
        if hoy <= dia_actual <= max_fecha and not es_fin_de_semana:
            dias.append({
                'fecha': dia_actual,
                'es_hoy': dia_actual == hoy,
                'es_pasado': False,
                'es_fin_de_semana': False,
                'vacio': False
            })
        else:
            dias.append({
                'fecha': dia_actual,
                'es_hoy': False,
                'es_pasado': True,
                'es_fin_de_semana': es_fin_de_semana,
                'vacio': False
            })
        dia_actual += timedelta(days=1)
    
    context = {
        'dias': dias,
        'año': año,
        'mes': mes,
        'mes_anterior': mes_anterior if mes_anterior >= hoy.replace(day=1) else None,
        'mes_siguiente': mes_siguiente,
        'nombre_mes_espanol': meses_espanol[mes],
        'hoy': hoy,
    }
    
    return render(request, 'home/calendario.html', context)


@login_required
def horas_ocupadas(request):
    fecha_str = request.GET.get('fecha')
    if not fecha_str:
        return JsonResponse([], safe=False)
    
    try:
        fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
        citas_existentes = Cita.objects.filter(fecha__date=fecha).values_list('fecha__time', flat=True)
        horas_ocupadas = [cita.strftime('%H:%M') for cita in citas_existentes]
        return JsonResponse(horas_ocupadas, safe=False)
    except ValueError:
        return JsonResponse([], safe=False)

    

def crear_cita_final(request):
    if request.method == 'POST':
        fecha_str = request.POST.get('fecha')
        hora_str = request.POST.get('hora')
        tipo = request.POST.get('tipo')
        
        try:
            fecha_hora = datetime.strptime(f"{fecha_str} {hora_str}", "%Y-%m-%d %H:%M")
            
            if Cita.objects.filter(fecha=fecha_hora).exists():
                messages.error(request, 'Ya existe una cita en ese horario')
                return redirect('calendario')
            
            cita = Cita.objects.create(user=request.user, fecha=fecha_hora, tipo=tipo)
            tipo_display = dict(Cita.TIPOS_CITA).get(tipo, tipo)
            messages.success(request, f'Cita de {tipo_display} creada para el {fecha_str} a las {hora_str}')
            
            if request.user.is_superuser:
                return redirect('admin_gestion_citas')
            else:
                return redirect('perfil')
            
        except Exception as e:
            messages.error(request, f'Error creando cita: {str(e)}')
    
    return redirect('calendario')


# =============================================
# VISTAS DE ADMINISTRACIÓN FERNANDO
# =============================================

def obtener_datos_citas_admin():
    ahora = timezone.now()
    
    citas_futuras = Cita.objects.filter(fecha__gte=ahora).select_related('user').order_by('fecha')
    citas_pasadas = Cita.objects.filter(fecha__lt=ahora).select_related('user').order_by('-fecha')
    
    citas = list(citas_futuras) + list(citas_pasadas)
    
    for cita in citas:
        cita.es_futura = cita.fecha >= ahora
    
    proxima_cita = citas_futuras.first()
    
    if proxima_cita:
        hoy = ahora.date()
        dias_restantes = (proxima_cita.fecha.date() - hoy).days
        if dias_restantes == 0:
            proxima_cita.dias_restantes = "Hoy"
        elif dias_restantes == 1:
            proxima_cita.dias_restantes = "Mañana"
        else:
            proxima_cita.dias_restantes = f"En {dias_restantes} días"
    
    hoy = ahora.date()
    semana_siguiente = hoy + timedelta(days=7)
    
    citas_hoy_count = citas_futuras.filter(fecha__date=hoy).count()
    citas_semana_count = citas_futuras.filter(fecha__date__range=[hoy, semana_siguiente]).count()
    total_citas_futuras = citas_futuras.count()
    
    return {
        'citas': citas,
        'proxima_cita': proxima_cita,
        'total_citas': total_citas_futuras,
        'citas_hoy_count': citas_hoy_count,
        'citas_semana_count': citas_semana_count,
    }

@login_required
def admin_editar_perfil(request):
    if not request.user.is_superuser:
        return redirect('home')
    
    if request.method == 'POST':
        cambios_realizados = False
        nuevo_username = request.POST.get('username')
        nuevo_email = request.POST.get('email')
        telefono = request.POST.get('telefono')
        
        if nuevo_username and nuevo_username != request.user.username:
            request.user.username = nuevo_username
            cambios_realizados = True
        
        if nuevo_email and nuevo_email != request.user.email:
            request.user.email = nuevo_email
            cambios_realizados = True
        
        telefono_vacio = telefono if telefono else None
        if telefono != request.user.telefono:
            request.user.telefono = telefono_vacio
            cambios_realizados = True

        if cambios_realizados:
            request.user.save()
            messages.success(request, 'Datos actualizados correctamente')
        else:
            messages.info(request, 'No se realizaron cambios')
    
    context = obtener_datos_citas_admin()
    context['seccion_activa'] = 'mi-perfil'
    
    return render(request, 'home/admin.html', context)

@login_required
def admin_cambiar_password(request):
    if not request.user.is_superuser:
        return redirect('home')
    
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        if request.user.check_password(current_password):
            if new_password == confirm_password:
                if len(new_password) < 3:
                    messages.error(request, 'La contraseña debe tener al menos 3 caracteres')
                else:
                    request.user.set_password(new_password)
                    request.user.save()
                    update_session_auth_hash(request, request.user)
                    messages.success(request, 'Contraseña cambiada correctamente')
            else:
                messages.error(request, 'Las contraseñas no coinciden')
        else:
            messages.error(request, 'Contraseña actual incorrecta')
    
    context = obtener_datos_citas_admin()
    context['seccion_activa'] = 'mi-perfil'
    
    return render(request, 'home/admin.html', context)

@login_required
def admin_gestion_citas(request):
    if not request.user.is_superuser:
        return redirect('home')
    
    context = obtener_datos_citas_admin()
    context['seccion_activa'] = 'gestion-citas'
    
    return render(request, 'home/admin.html', context)

@login_required
def admin_cancelar_cita(request, cita_id):
    if not request.user.is_superuser:
        messages.error(request, 'Sin permisos')
        return redirect('perfil')
    
    try:
        cita = Cita.objects.get(id=cita_id)
        cita.delete()
        messages.success(request, 'Cita cancelada')
    except Cita.DoesNotExist:
        messages.error(request, 'Cita no encontrada')
    
    return redirect('admin_gestion_citas')

def lista_productos(request):
    productos = Producto.objects.all()  # Todos los productos
    return render(request, "home/productos.html", {"productos": productos})