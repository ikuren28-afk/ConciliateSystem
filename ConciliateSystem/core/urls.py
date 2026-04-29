from django.urls import path
from . import views

urlpatterns = [
    # Autenticación
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    
    # Notificaciones
    path('notification/<uuid:notification_id>/read/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/read-all/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
    
    # Gestión de usuarios (Solo administradores)
    path('users/register/', views.register_user_view, name='register_user'),
    path('users/', views.user_list_view, name='user_list'),
    path('users/<uuid:user_id>/edit/', views.edit_user_view, name='edit_user'),
    path('users/<uuid:user_id>/delete/', views.delete_user_view, name='delete_user'),
    
    # Gestión de oficinas (Solo administradores)
    path('offices/', views.office_list_view, name='office_list'),
    path('offices/create/', views.office_create_view, name='office_create'),
    path('offices/<uuid:office_id>/edit/', views.office_edit_view, name='office_edit'),
    path('offices/<uuid:office_id>/delete/', views.office_delete_view, name='office_delete'),
    
    # Gestión de cuentas bancarias (Solo administradores)
    path('bank-accounts/', views.bank_account_list_view, name='bank_account_list'),
    path('bank-accounts/create/', views.bank_account_create_view, name='bank_account_create'),
    path('bank-accounts/<uuid:account_id>/edit/', views.bank_account_edit_view, name='bank_account_edit'),
    path('bank-accounts/<uuid:account_id>/delete/', views.bank_account_delete_view, name='bank_account_delete'),
    
    # Gestión de tipos de operaciones (Solo administradores)
    path('operations/', views.operation_list_view, name='operation_list'),
    path('operations/create/', views.operation_create_view, name='operation_create'),
    path('operations/<uuid:operation_id>/edit/', views.operation_edit_view, name='operation_edit'),
    path('operations/<uuid:operation_id>/delete/', views.operation_delete_view, name='operation_delete'),
]
