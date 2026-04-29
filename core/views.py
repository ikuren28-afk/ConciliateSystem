from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.models import User, Group
from .forms import LoginForm, CustomUserCreationForm
from .models import Role, Office, BankAccount, Operation, BankStatement, BankStatementTransaction, Notification, AuditLog


def login_view(request):
    """Vista para iniciar sesión"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Bienvenido {user.first_name or user.username}!')
                return redirect('dashboard')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
    else:
        form = LoginForm()
    
    return render(request, 'core/login.html', {'form': form})


def logout_view(request):
    """Vista para cerrar sesión"""
    logout(request)
    messages.info(request, 'Has cerrado sesión correctamente.')
    return redirect('login')


@login_required
def dashboard_view(request):
    """Vista del dashboard principal"""
    # Obtener notificaciones no leídas del usuario
    unread_notifications = Notification.objects.filter(user=request.user, is_read=False)[:5]
    total_unread = Notification.objects.filter(user=request.user, is_read=False).count()
    
    # Verificar permisos de rol para mostrar menú de administración
    is_admin_user = request.user.groups.filter(name='Administrador').exists() or request.user.is_superuser
    
    context = {
        'unread_notifications': unread_notifications,
        'total_unread': total_unread,
        'is_admin_user': is_admin_user,
    }
    return render(request, 'core/dashboard.html', context)


def is_admin(user):
    """Verifica si el usuario es administrador"""
    return user.groups.filter(name='Administrador').exists() or user.is_superuser


def is_financial_analyst(user):
    """Verifica si el usuario es analista financiero"""
    return user.groups.filter(name='Analista Financiero').exists() or user.is_superuser


def is_economic_analyst(user):
    """Verifica si el usuario es analista económico"""
    return user.groups.filter(name='Analista Económico').exists() or user.is_superuser


def is_commercial_analyst(user):
    """Verifica si el usuario es analista comercial"""
    return user.groups.filter(name='Analista Comercial').exists() or user.is_superuser


@login_required
@user_passes_test(is_admin, login_url='dashboard')
def register_user_view(request):
    """Vista para registrar nuevos usuarios (solo administradores)"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Asignar rol si se especifica
            role_name = request.POST.get('role')
            if role_name:
                group, created = Group.objects.get_or_create(name=role_name)
                user.groups.add(group)
            
            # Crear registro de auditoría
            AuditLog.objects.create(
                user=request.user,
                action='CREATE',
                model_name='User',
                object_id=user.id,
                changes=f'Usuario {user.username} creado por {request.user.username}'
            )
            
            messages.success(request, f'Usuario {user.username} registrado exitosamente.')
            return redirect('user_list')
        else:
            messages.error(request, 'Error al registrar el usuario. Verifique los datos.')
    else:
        form = CustomUserCreationForm()
    
    roles = ['Administrador', 'Analista Financiero', 'Analista Económico', 'Analista Comercial']
    return render(request, 'core/register_user.html', {'form': form, 'roles': roles})


@login_required
@user_passes_test(is_admin, login_url='dashboard')
def user_list_view(request):
    """Vista para listar usuarios (solo administradores)"""
    users = User.objects.all().select_related('audit_logs').prefetch_related('groups')
    return render(request, 'core/user_list.html', {'users': users})


@login_required
@user_passes_test(is_admin, login_url='dashboard')
def edit_user_view(request, user_id):
    """Vista para editar usuarios (solo administradores)"""
    user = get_object_or_404(User, pk=user_id)
    
    if request.method == 'POST':
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        user.is_active = request.POST.get('is_active') == 'on'
        
        # Actualizar grupos/roles
        user.groups.clear()
        role_name = request.POST.get('role')
        if role_name:
            group, created = Group.objects.get_or_create(name=role_name)
            user.groups.add(group)
        
        user.save()
        
        # Crear registro de auditoría
        AuditLog.objects.create(
            user=request.user,
            action='UPDATE',
            model_name='User',
            object_id=user.id,
            changes=f'Usuario {user.username} editado por {request.user.username}'
        )
        
        messages.success(request, f'Usuario {user.username} actualizado exitosamente.')
        return redirect('user_list')
    
    roles = ['Administrador', 'Analista Financiero', 'Analista Económico', 'Analista Comercial']
    current_role = user.groups.first().name if user.groups.exists() else ''
    
    return render(request, 'core/edit_user.html', {
        'user_form': user,
        'roles': roles,
        'current_role': current_role
    })


@login_required
@user_passes_test(is_admin, login_url='dashboard')
def delete_user_view(request, user_id):
    """Vista para eliminar usuarios (solo administradores)"""
    user = get_object_or_404(User, pk=user_id)
    
    if request.method == 'POST':
        username = user.username
        user.delete()
        
        # Crear registro de auditoría
        AuditLog.objects.create(
            user=request.user,
            action='DELETE',
            model_name='User',
            changes=f'Usuario {username} eliminado por {request.user.username}'
        )
        
        messages.success(request, f'Usuario {username} eliminado exitosamente.')
        return redirect('user_list')
    
    return render(request, 'core/delete_user.html', {'user': user})


@login_required
def mark_notification_read_view(request, notification_id):
    """Marcar una notificación como leída"""
    notification = get_object_or_404(Notification, pk=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    return redirect('dashboard')


@login_required
def mark_all_notifications_read_view(request):
    """Marcar todas las notificaciones como leídas"""
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return redirect('dashboard')
