from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import Cita, Promocion, Directo
from django.views.decorators.http import require_POST
from datetime import timedelta, datetime, date
from .models import Producto
from django.urls import reverse

User = get_user_model()

def home_view(request: HttpRequest) -> HttpResponse:
    hoy = timezone.now().date()
    
    # Recuperar promociones activas
    promociones_activas = Promocion.objects.filter(
        activa=True,
        fecha_inicio__lte=hoy,
        fecha_fin__gte=hoy
    )

    # Recuperar el directo activo (si existe)
    current_directo = Directo.objects.filter(is_active=True).first()

    return render(request, 'home/index.html', {
        'promociones_activas': promociones_activas,
        'current_directo': current_directo,})


def services_view(request: HttpRequest) -> HttpResponse:
    # Renderiza la plantilla servicios de la página de inicio.
    return render(request, 'services.html', get_directo_context())



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
    
    return render(request, 'home/index.html', get_directo_context())


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

    context = {
        'citas_programadas': citas_programadas,
        'citas_pasadas': citas_pasadas
    }
    
    # Fusionar con el contexto de promoción
    context.update(get_directo_context())
    
    return render(request, 'home/perfil.html', context)

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

    context.update(get_directo_context())
    
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
                return redirect(reverse('admin_gestion_citas') + '?tab=gestion-citas')
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
    # Añadir promociones al contexto
    promociones = Promocion.objects.all().order_by('-id')
    # Añadir mensaje directo activo al contexto
    current_directo = Directo.objects.filter(is_active=True).first()
    
    return {
        'citas': citas,
        'proxima_cita': proxima_cita,
        'total_citas': total_citas_futuras,
        'citas_hoy_count': citas_hoy_count,
        'citas_semana_count': citas_semana_count,
        'promociones': promociones,
        'current_directo': current_directo,
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
    
    return redirect(reverse('admin_gestion_citas') + '?tab=gestion-citas')

def lista_productos(request):
    productos = Producto.objects.all()  # Todos los productos
    context = {"productos": productos}
    context.update(get_directo_context())
    return render(request, "home/productos.html", context)

# Vista para listar (Igual que antes)
def lista_promociones(request):
    promociones = Promocion.objects.all().order_by('-id')
    return render(request, 'promociones/lista.html', {'promociones': promociones})

# Vista para crear nueva promoción
def crear_promocion(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        fecha_inicio = request.POST.get('fecha_inicio')
        fecha_fin = request.POST.get('fecha_fin')
        activa = request.POST.get('activa') == 'on'

        try:
            if fecha_inicio and fecha_fin:
                if fecha_fin < fecha_inicio:
                    raise ValueError("La fecha de fin no puede ser anterior a la de inicio")

            promo = Promocion.objects.create(
                nombre=nombre,
                descripcion=descripcion,
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
                activa=activa
            )
            
            # CRÍTICO: Si la petición viene del JavaScript (Modal), devolvemos JSON
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'status': 'ok', 'id': promo.id})
                
        except Exception as e:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error', 'errors': str(e)}, status=400)

        # Si no es AJAX, redirigimos al panel administrativo pestaña anuncios
        return redirect(reverse('admin_gestion_citas') + '?tab=anuncios') 
    
    # Si es GET, redirigimos al panel
    return redirect(reverse('admin_gestion_citas') + '?tab=anuncios')

# API para el interruptor (Toggle ON/OFF)
@require_POST
def toggle_promocion(request, pk):
    promocion = get_object_or_404(Promocion, pk=pk)
    promocion.activa = not promocion.activa
    promocion.save()
    return JsonResponse({'status': 'ok', 'activa': promocion.activa})

@login_required
def eliminar_promocion(request, pk):
    if not request.user.is_superuser:
        return redirect('home')
        
    promocion = get_object_or_404(Promocion, pk=pk)
    promocion.delete()
    
    # Redirigimos de vuelta al panel, pestaña anuncios
    return redirect(reverse('admin_gestion_citas') + '?tab=anuncios')


@csrf_protect
def update_Directo(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        # Nota: Aquí usarías request.POST.get() si el frontend usa un formulario tradicional
        # o request.body/json.loads() si sigue usando AJAX pero la quieres redirigir.
        
        # Asumiendo que has ajustado el frontend para enviar como formulario POST tradicional:
        text = request.POST.get('message_text', '').strip()
        url = request.POST.get('message_url', '').strip() 

        if not text:
            messages.error(request, 'El mensaje de cabecera no puede estar vacío.')
            return redirect('home')
        
        if not url:
            messages.error(request, 'La url no puede estar vacío.')
            return redirect('home')
        
        try:
            # Lógica para desactivar y crear/actualizar el mensaje (igual que antes)
            Directo.objects.filter(is_active=True).update(is_active=False)
            Directo.objects.create(text=text, url=url, is_active=True)
            
            messages.success(request, 'Mensaje de cabecera actualizado correctamente.')
            
        except Exception as e:
            messages.error(request, f'Error al guardar el mensaje: {str(e)}')
            
        return redirect('home') # Forzar recarga completa de la página de inicio
    
    # Si alguien intenta acceder con GET, redirigir al inicio
    return redirect('home')


@csrf_protect
def delete_Directo(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        try:
            message = Directo.objects.filter(is_active=True).first()
            
            if message:
                message.is_active = False
                message.save()
                messages.success(request, 'Mensaje de cabecera eliminado correctamente.')
            else:
                messages.info(request, 'No había ningún mensaje activo que eliminar.')
                
        except Exception as e:
            messages.error(request, f'Error al eliminar el mensaje: {str(e)}')
            
        return redirect('home') # Forzar recarga completa de la página de inicio

    return redirect('home')


# --- FUNCIÓN DE AYUDA PARA EL CONTEXTO DIRECTO (HELPER) ---
def get_directo_context():
    """Busca el mensaje de directo activo para pasarlo al contexto."""
    try:
        current_directo = Directo.objects.filter(is_active=True).first()
    except Exception:
        current_directo = None
        
    return {'current_directo': current_directo}