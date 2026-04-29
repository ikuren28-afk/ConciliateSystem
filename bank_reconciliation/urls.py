"""
URL configuration for bank_reconciliation project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.login_view, name='login'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    
    # Gestión de usuarios (solo administradores)
    path('users/register/', views.register_user_view, name='register_user'),
    path('users/', views.user_list_view, name='user_list'),
    path('users/<uuid:user_id>/edit/', views.edit_user_view, name='edit_user'),
    path('users/<uuid:user_id>/delete/', views.delete_user_view, name='delete_user'),
    
    # Notificaciones
    path('notifications/<uuid:notification_id>/read/', views.mark_notification_read_view, name='mark_notification_read'),
    path('notifications/read-all/', views.mark_all_notifications_read_view, name='mark_all_notifications_read'),
    
    # Gestión de Oficinas (solo administradores)
    path('offices/', views.office_list_view, name='office_list'),
    path('offices/create/', views.office_create_view, name='office_create'),
    path('offices/<uuid:office_id>/edit/', views.office_edit_view, name='office_edit'),
    path('offices/<uuid:office_id>/delete/', views.office_delete_view, name='office_delete'),
    
    # Gestión de Cuentas Bancarias (solo administradores)
    path('bank-accounts/', views.bank_account_list_view, name='bank_account_list'),
    path('bank-accounts/create/', views.bank_account_create_view, name='bank_account_create'),
    path('bank-accounts/<uuid:account_id>/edit/', views.bank_account_edit_view, name='bank_account_edit'),
    path('bank-accounts/<uuid:account_id>/delete/', views.bank_account_delete_view, name='bank_account_delete'),
    
    # Gestión de Tipos de Operaciones (solo administradores)
    path('operations/', views.operation_list_view, name='operation_list'),
    path('operations/create/', views.operation_create_view, name='operation_create'),
    path('operations/<uuid:operation_id>/edit/', views.operation_edit_view, name='operation_edit'),
    path('operations/<uuid:operation_id>/delete/', views.operation_delete_view, name='operation_delete'),
    
    # Gestión de Estados de Cuenta (solo administradores y analistas financieros)
    path('bank-statements/', views.bank_statement_list_view, name='bank_statement_list'),
    path('bank-statements/upload/', views.bank_statement_upload_view, name='bank_statement_upload'),
    path('bank-statements/<uuid:statement_id>/delete/', views.bank_statement_delete_view, name='bank_statement_delete'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
