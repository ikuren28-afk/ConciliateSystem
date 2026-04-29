from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
from .forms import LoginForm, CustomUserCreationForm, OfficeForm, BankAccountForm, OperationForm
from .models import Notification, Office, BankAccount, Operation
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


def is_admin(user):
    """Verifica si el usuario es administrador"""
    return user.groups.filter(name='Administrador').exists()


def is_financial_analyst(user):
    """Verifica si el usuario es analista financiero"""
    return user.groups.filter(name='Analista financiero').exists()


def is_economic_analyst(user):
    """Verifica si el usuario es analista económico"""
    return user.groups.filter(name='Analista económico').exists()


def is_commercial_analyst(user):
    """Verifica si el usuario es analista comercial"""
    return user.groups.filter(name='Analista comercial').exists()


def login_view(request):
    """Vista para iniciar sesión"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f'Bienvenido, {user.first_name or user.username}!')
                return redirect('dashboard')
            else:
                messages.error(request, 'Usuario o contraseña incorrectos.')
    else:
        form = LoginForm()
    
    return render(request, 'core/login.html', {'form': form})


@login_required
def logout_view(request):
    """Vista para cerrar sesión"""
    logout(request)
    messages.info(request, 'Has cerrado sesión correctamente.')
    return redirect('login')


@login_required
def dashboard_view(request):
    """Vista del dashboard principal"""
    # Obtener notificaciones no leídas
    notifications = Notification.objects.filter(
        user=request.user, 
        read_at__isnull=True
    ).order_by('-created_at')[:10]
    
    # Contar notificaciones por tipo
    notification_counts = Notification.objects.filter(
        user=request.user,
        read_at__isnull=True
    ).values('type').annotate(count=Count('id'))
    
    # Preparar contexto con permisos por rol
    context = {
        'notifications': notifications,
        'is_admin_user': is_admin(request.user),
        'is_financial_analyst_user': is_financial_analyst(request.user),
        'is_economic_analyst_user': is_economic_analyst(request.user),
        'is_commercial_analyst_user': is_commercial_analyst(request.user),
        'notification_counts': {item['type']: item['count'] for item in notification_counts},
    }
    
    return render(request, 'core/dashboard.html', context)


@login_required
def mark_notification_read(request, notification_id):
    """Marcar una notificación como leída"""
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.read_at = timezone.now()
    notification.save()
    return redirect('dashboard')


@login_required
def mark_all_notifications_read(request):
    """Marcar todas las notificaciones como leídas"""
    Notification.objects.filter(user=request.user, read_at__isnull=True).update(read_at=timezone.now())
    return redirect('dashboard')


# ==================== GESTIÓN DE USUARIOS (Solo Administradores) ====================

@login_required
def register_user_view(request):
    """Registro de usuarios - Solo administradores"""
    if not is_admin(request.user):
        messages.error(request, 'No tienes permisos para realizar esta acción.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()
            
            # Asignar grupo si se seleccionó
            group_name = form.cleaned_data.get('group')
            if group_name:
                group = Group.objects.get(name=group_name)
                user.groups.add(group)
            
            messages.success(request, f'Usuario {user.username} registrado exitosamente.')
            return redirect('user_list')
        else:
            messages.error(request, 'Error en el formulario. Por favor corrige los errores.')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'core/register_user.html', {'form': form})


@login_required
def user_list_view(request):
    """Listado de usuarios - Solo administradores"""
    if not is_admin(request.user):
        messages.error(request, 'No tienes permisos para realizar esta acción.')
        return redirect('dashboard')
    
    search_query = request.GET.get('search', '')
    users = User.objects.all().select_related('profile').prefetch_related('groups')
    
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        )
    
    paginator = Paginator(users, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'core/user_list.html', {'page_obj': page_obj, 'search_query': search_query})


@login_required
def edit_user_view(request, user_id):
    """Edición de usuarios - Solo administradores"""
    if not is_admin(request.user):
        messages.error(request, 'No tienes permisos para realizar esta acción.')
        return redirect('dashboard')
    
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        # Procesar formulario de edición
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        email = request.POST.get('email', '')
        is_active = request.POST.get('is_active') == 'on'
        group_name = request.POST.get('group', '')
        
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.is_active = is_active
        user.save()
        
        # Actualizar grupo
        user.groups.clear()
        if group_name:
            group = Group.objects.get(name=group_name)
            user.groups.add(group)
        
        messages.success(request, f'Usuario {user.username} actualizado exitosamente.')
        return redirect('user_list')
    
    # Obtener grupo actual del usuario
    current_group = user.groups.first().name if user.groups.exists() else ''
    
    return render(request, 'core/edit_user.html', {
        'user_obj': user,
        'current_group': current_group
    })


@login_required
def delete_user_view(request, user_id):
    """Eliminación de usuarios - Solo administradores"""
    if not is_admin(request.user):
        messages.error(request, 'No tienes permisos para realizar esta acción.')
        return redirect('dashboard')
    
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        username = user.username
        user.delete()
        messages.success(request, f'Usuario {username} eliminado exitosamente.')
        return redirect('user_list')
    
    return render(request, 'core/delete_user.html', {'user_obj': user})


# ==================== GESTIÓN DE OFICINAS (Solo Administradores) ====================

@login_required
def office_list_view(request):
    """Listado de oficinas - Solo administradores"""
    if not is_admin(request.user):
        messages.error(request, 'No tienes permisos para realizar esta acción.')
        return redirect('dashboard')
    
    search_query = request.GET.get('search', '')
    offices = Office.objects.all()
    
    if search_query:
        offices = offices.filter(
            Q(code__icontains=search_query) |
            Q(name__icontains=search_query)
        )
    
    paginator = Paginator(offices, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'core/office_list.html', {'page_obj': page_obj, 'search_query': search_query})


@login_required
def office_create_view(request):
    """Crear oficina - Solo administradores"""
    if not is_admin(request.user):
        messages.error(request, 'No tienes permisos para realizar esta acción.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = OfficeForm(request.POST)
        if form.is_valid():
            office = form.save()
            messages.success(request, f'Oficina {office.name} creada exitosamente.')
            return redirect('office_list')
    else:
        form = OfficeForm()
    
    return render(request, 'core/office_form.html', {'form': form, 'action': 'Crear'})


@login_required
def office_edit_view(request, office_id):
    """Editar oficina - Solo administradores"""
    if not is_admin(request.user):
        messages.error(request, 'No tienes permisos para realizar esta acción.')
        return redirect('dashboard')
    
    office = get_object_or_404(Office, id=office_id)
    
    if request.method == 'POST':
        form = OfficeForm(request.POST, instance=office)
        if form.is_valid():
            form.save()
            messages.success(request, f'Oficina {office.name} actualizada exitosamente.')
            return redirect('office_list')
    else:
        form = OfficeForm(instance=office)
    
    return render(request, 'core/office_form.html', {'form': form, 'action': 'Editar', 'office': office})


@login_required
def office_delete_view(request, office_id):
    """Eliminar oficina - Solo administradores"""
    if not is_admin(request.user):
        messages.error(request, 'No tienes permisos para realizar esta acción.')
        return redirect('dashboard')
    
    office = get_object_or_404(Office, id=office_id)
    
    if request.method == 'POST':
        office_name = office.name
        office.delete()
        messages.success(request, f'Oficina {office_name} eliminada exitosamente.')
        return redirect('office_list')
    
    return render(request, 'core/office_confirm_delete.html', {'office': office})


# ==================== GESTIÓN DE CUENTAS BANCARIAS (Solo Administradores) ====================

@login_required
def bank_account_list_view(request):
    """Listado de cuentas bancarias - Solo administradores"""
    if not is_admin(request.user):
        messages.error(request, 'No tienes permisos para realizar esta acción.')
        return redirect('dashboard')
    
    search_query = request.GET.get('search', '')
    accounts = BankAccount.objects.all()
    
    if search_query:
        accounts = accounts.filter(
            Q(code__icontains=search_query) |
            Q(name__icontains=search_query)
        )
    
    paginator = Paginator(accounts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'core/bank_account_list.html', {'page_obj': page_obj, 'search_query': search_query})


@login_required
def bank_account_create_view(request):
    """Crear cuenta bancaria - Solo administradores"""
    if not is_admin(request.user):
        messages.error(request, 'No tienes permisos para realizar esta acción.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = BankAccountForm(request.POST)
        if form.is_valid():
            account = form.save()
            messages.success(request, f'Cuenta {account.name} creada exitosamente.')
            return redirect('bank_account_list')
    else:
        form = BankAccountForm()
    
    return render(request, 'core/bank_account_form.html', {'form': form, 'action': 'Crear'})


@login_required
def bank_account_edit_view(request, account_id):
    """Editar cuenta bancaria - Solo administradores"""
    if not is_admin(request.user):
        messages.error(request, 'No tienes permisos para realizar esta acción.')
        return redirect('dashboard')
    
    account = get_object_or_404(BankAccount, id=account_id)
    
    if request.method == 'POST':
        form = BankAccountForm(request.POST, instance=account)
        if form.is_valid():
            form.save()
            messages.success(request, f'Cuenta {account.name} actualizada exitosamente.')
            return redirect('bank_account_list')
    else:
        form = BankAccountForm(instance=account)
    
    return render(request, 'core/bank_account_form.html', {'form': form, 'action': 'Editar', 'account': account})


@login_required
def bank_account_delete_view(request, account_id):
    """Eliminar cuenta bancaria - Solo administradores"""
    if not is_admin(request.user):
        messages.error(request, 'No tienes permisos para realizar esta acción.')
        return redirect('dashboard')
    
    account = get_object_or_404(BankAccount, id=account_id)
    
    if request.method == 'POST':
        account_name = account.name
        account.delete()
        messages.success(request, f'Cuenta {account_name} eliminada exitosamente.')
        return redirect('bank_account_list')
    
    return render(request, 'core/bank_account_confirm_delete.html', {'account': account})


# ==================== GESTIÓN DE TIPOS DE OPERACIONES (Solo Administradores) ====================

@login_required
def operation_list_view(request):
    """Listado de tipos de operaciones - Solo administradores"""
    if not is_admin(request.user):
        messages.error(request, 'No tienes permisos para realizar esta acción.')
        return redirect('dashboard')
    
    search_query = request.GET.get('search', '')
    operations = Operation.objects.all()
    
    if search_query:
        operations = operations.filter(
            Q(code__icontains=search_query) |
            Q(name__icontains=search_query)
        )
    
    paginator = Paginator(operations, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'core/operation_list.html', {'page_obj': page_obj, 'search_query': search_query})


@login_required
def operation_create_view(request):
    """Crear tipo de operación - Solo administradores"""
    if not is_admin(request.user):
        messages.error(request, 'No tienes permisos para realizar esta acción.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = OperationForm(request.POST)
        if form.is_valid():
            operation = form.save()
            messages.success(request, f'Tipo de operación {operation.name} creado exitosamente.')
            return redirect('operation_list')
    else:
        form = OperationForm()
    
    return render(request, 'core/operation_form.html', {'form': form, 'action': 'Crear'})


@login_required
def operation_edit_view(request, operation_id):
    """Editar tipo de operación - Solo administradores"""
    if not is_admin(request.user):
        messages.error(request, 'No tienes permisos para realizar esta acción.')
        return redirect('dashboard')
    
    operation = get_object_or_404(Operation, id=operation_id)
    
    if request.method == 'POST':
        form = OperationForm(request.POST, instance=operation)
        if form.is_valid():
            form.save()
            messages.success(request, f'Tipo de operación {operation.name} actualizado exitosamente.')
            return redirect('operation_list')
    else:
        form = OperationForm(instance=operation)
    
    return render(request, 'core/operation_form.html', {'form': form, 'action': 'Editar', 'operation': operation})


@login_required
def operation_delete_view(request, operation_id):
    """Eliminar tipo de operación - Solo administradores"""
    if not is_admin(request.user):
        messages.error(request, 'No tienes permisos para realizar esta acción.')
        return redirect('dashboard')
    
    operation = get_object_or_404(Operation, id=operation_id)
    
    if request.method == 'POST':
        operation_name = operation.name
        operation.delete()
        messages.success(request, f'Tipo de operación {operation_name} eliminado exitosamente.')
        return redirect('operation_list')
    
    return render(request, 'core/operation_confirm_delete.html', {'operation': operation})
