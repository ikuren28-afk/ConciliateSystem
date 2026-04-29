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


# ==================== Vistas para Oficinas ====================

@login_required
@user_passes_test(is_admin, login_url='dashboard')
def office_list_view(request):
    """Listado de oficinas (solo administradores)"""
    offices = Office.objects.all().order_by('code')
    return render(request, 'core/office_list.html', {'offices': offices})


@login_required
@user_passes_test(is_admin, login_url='dashboard')
def office_create_view(request):
    """Crear oficina (solo administradores)"""
    if request.method == 'POST':
        form = OfficeForm(request.POST)
        if form.is_valid():
            office = form.save()
            AuditLog.objects.create(
                user=request.user,
                action='CREATE',
                model_name='Office',
                object_id=office.id,
                changes=f'Oficina {office.code} creada por {request.user.username}'
            )
            messages.success(request, f'Oficina {office.name} creada exitosamente.')
            return redirect('office_list')
        else:
            messages.error(request, 'Error al crear la oficina. Verifique los datos.')
    else:
        form = OfficeForm()
    
    return render(request, 'core/office_form.html', {'form': form, 'action': 'Crear'})


@login_required
@user_passes_test(is_admin, login_url='dashboard')
def office_edit_view(request, office_id):
    """Editar oficina (solo administradores)"""
    office = get_object_or_404(Office, pk=office_id)
    
    if request.method == 'POST':
        form = OfficeForm(request.POST, instance=office)
        if form.is_valid():
            office = form.save()
            AuditLog.objects.create(
                user=request.user,
                action='UPDATE',
                model_name='Office',
                object_id=office.id,
                changes=f'Oficina {office.code} editada por {request.user.username}'
            )
            messages.success(request, f'Oficina {office.name} actualizada exitosamente.')
            return redirect('office_list')
        else:
            messages.error(request, 'Error al editar la oficina. Verifique los datos.')
    else:
        form = OfficeForm(instance=office)
    
    return render(request, 'core/office_form.html', {'form': form, 'action': 'Editar', 'office': office})


@login_required
@user_passes_test(is_admin, login_url='dashboard')
def office_delete_view(request, office_id):
    """Eliminar oficina (solo administradores)"""
    office = get_object_or_404(Office, pk=office_id)
    
    if request.method == 'POST':
        office_code = office.code
        office_name = office.name
        office.delete()
        AuditLog.objects.create(
            user=request.user,
            action='DELETE',
            model_name='Office',
            changes=f'Oficina {office_code} ({office_name}) eliminada por {request.user.username}'
        )
        messages.success(request, f'Oficina {office_name} eliminada exitosamente.')
        return redirect('office_list')
    
    return render(request, 'core/office_delete.html', {'office': office})


# ==================== Vistas para Cuentas Bancarias ====================

@login_required
@user_passes_test(is_admin, login_url='dashboard')
def bank_account_list_view(request):
    """Listado de cuentas bancarias (solo administradores)"""
    accounts = BankAccount.objects.all().order_by('code')
    return render(request, 'core/bank_account_list.html', {'accounts': accounts})


@login_required
@user_passes_test(is_admin, login_url='dashboard')
def bank_account_create_view(request):
    """Crear cuenta bancaria (solo administradores)"""
    if request.method == 'POST':
        form = BankAccountForm(request.POST)
        if form.is_valid():
            account = form.save()
            AuditLog.objects.create(
                user=request.user,
                action='CREATE',
                model_name='BankAccount',
                object_id=account.id,
                changes=f'Cuenta bancaria {account.code} creada por {request.user.username}'
            )
            messages.success(request, f'Cuenta bancaria {account.name} creada exitosamente.')
            return redirect('bank_account_list')
        else:
            messages.error(request, 'Error al crear la cuenta bancaria. Verifique los datos.')
    else:
        form = BankAccountForm()
    
    return render(request, 'core/bank_account_form.html', {'form': form, 'action': 'Crear'})


@login_required
@user_passes_test(is_admin, login_url='dashboard')
def bank_account_edit_view(request, account_id):
    """Editar cuenta bancaria (solo administradores)"""
    account = get_object_or_404(BankAccount, pk=account_id)
    
    if request.method == 'POST':
        form = BankAccountForm(request.POST, instance=account)
        if form.is_valid():
            account = form.save()
            AuditLog.objects.create(
                user=request.user,
                action='UPDATE',
                model_name='BankAccount',
                object_id=account.id,
                changes=f'Cuenta bancaria {account.code} editada por {request.user.username}'
            )
            messages.success(request, f'Cuenta bancaria {account.name} actualizada exitosamente.')
            return redirect('bank_account_list')
        else:
            messages.error(request, 'Error al editar la cuenta bancaria. Verifique los datos.')
    else:
        form = BankAccountForm(instance=account)
    
    return render(request, 'core/bank_account_form.html', {'form': form, 'action': 'Editar', 'account': account})


@login_required
@user_passes_test(is_admin, login_url='dashboard')
def bank_account_delete_view(request, account_id):
    """Eliminar cuenta bancaria (solo administradores)"""
    account = get_object_or_404(BankAccount, pk=account_id)
    
    if request.method == 'POST':
        account_code = account.code
        account_name = account.name
        account.delete()
        AuditLog.objects.create(
            user=request.user,
            action='DELETE',
            model_name='BankAccount',
            changes=f'Cuenta bancaria {account_code} ({account_name}) eliminada por {request.user.username}'
        )
        messages.success(request, f'Cuenta bancaria {account_name} eliminada exitosamente.')
        return redirect('bank_account_list')
    
    return render(request, 'core/bank_account_delete.html', {'account': account})


# ==================== Vistas para Tipos de Operaciones ====================

@login_required
@user_passes_test(is_admin, login_url='dashboard')
def operation_list_view(request):
    """Listado de tipos de operaciones (solo administradores)"""
    operations = Operation.objects.all().order_by('code')
    return render(request, 'core/operation_list.html', {'operations': operations})


@login_required
@user_passes_test(is_admin, login_url='dashboard')
def operation_create_view(request):
    """Crear tipo de operación (solo administradores)"""
    if request.method == 'POST':
        form = OperationForm(request.POST)
        if form.is_valid():
            operation = form.save()
            AuditLog.objects.create(
                user=request.user,
                action='CREATE',
                model_name='Operation',
                object_id=operation.id,
                changes=f'Tipo de operación {operation.code} creado por {request.user.username}'
            )
            messages.success(request, f'Tipo de operación {operation.name} creado exitosamente.')
            return redirect('operation_list')
        else:
            messages.error(request, 'Error al crear el tipo de operación. Verifique los datos.')
    else:
        form = OperationForm()
    
    return render(request, 'core/operation_form.html', {'form': form, 'action': 'Crear'})


@login_required
@user_passes_test(is_admin, login_url='dashboard')
def operation_edit_view(request, operation_id):
    """Editar tipo de operación (solo administradores)"""
    operation = get_object_or_404(Operation, pk=operation_id)
    
    if request.method == 'POST':
        form = OperationForm(request.POST, instance=operation)
        if form.is_valid():
            operation = form.save()
            AuditLog.objects.create(
                user=request.user,
                action='UPDATE',
                model_name='Operation',
                object_id=operation.id,
                changes=f'Tipo de operación {operation.code} editado por {request.user.username}'
            )
            messages.success(request, f'Tipo de operación {operation.name} actualizado exitosamente.')
            return redirect('operation_list')
        else:
            messages.error(request, 'Error al editar el tipo de operación. Verifique los datos.')
    else:
        form = OperationForm(instance=operation)
    
    return render(request, 'core/operation_form.html', {'form': form, 'action': 'Editar', 'operation': operation})


@login_required
@user_passes_test(is_admin, login_url='dashboard')
def operation_delete_view(request, operation_id):
    """Eliminar tipo de operación (solo administradores)"""
    operation = get_object_or_404(Operation, pk=operation_id)
    
    if request.method == 'POST':
        operation_code = operation.code
        operation_name = operation.name
        operation.delete()
        AuditLog.objects.create(
            user=request.user,
            action='DELETE',
            model_name='Operation',
            changes=f'Tipo de operación {operation_code} ({operation_name}) eliminado por {request.user.username}'
        )
        messages.success(request, f'Tipo de operación {operation_name} eliminado exitosamente.')
        return redirect('operation_list')
    
    return render(request, 'core/operation_delete.html', {'operation': operation})
