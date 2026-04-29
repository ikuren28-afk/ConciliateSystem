from django.contrib import admin
from django.contrib.auth.models import User, Group
from .models import Role, Office, BankAccount, Operation, BankStatement, BankStatementTransaction, Notification, AuditLog, TransactionChangeHistory

# Personalización del admin
admin.site.site_header = 'Administración de Conciliación Bancaria'
admin.site.site_title = 'ConciliateSystem Admin'
admin.site.index_title = 'Panel de Administración'


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['name', 'id']
    search_fields = ['name']


@admin.register(Office)
class OfficeAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'created_at', 'updated_at']
    search_fields = ['code', 'name']
    list_filter = ['created_at']


@admin.register(BankAccount)
class BankAccountAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'created_at', 'updated_at']
    search_fields = ['code', 'name']
    list_filter = ['created_at']


@admin.register(Operation)
class OperationAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'created_at', 'updated_at']
    search_fields = ['code', 'name']
    list_filter = ['created_at']


@admin.register(BankStatement)
class BankStatementAdmin(admin.ModelAdmin):
    list_display = ['bank_account', 'statement_date', 'entry_count', 'uploaded_by', 'created_at']
    search_fields = ['bank_account__name', 'file_name']
    list_filter = ['bank_account', 'statement_date', 'created_at']
    readonly_fields = ['uploaded_by', 'created_at', 'updated_at']


@admin.register(BankStatementTransaction)
class BankStatementTransactionAdmin(admin.ModelAdmin):
    list_display = ['current_reference', 'bank_statement', 'amount', 'currency', 'reconciliation_status', 'created_at']
    search_fields = ['current_reference', 'original_reference', 'name']
    list_filter = ['reconciliation_status', 'currency', 'entry_type', 'created_at']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'type', 'read_at', 'created_at']
    search_fields = ['user__username', 'content']
    list_filter = ['type', 'read_at', 'created_at']


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['action', 'model_name', 'user', 'ip_address', 'created_at']
    search_fields = ['user__username', 'model_name', 'description']
    list_filter = ['action', 'model_name', 'created_at']
    readonly_fields = ['created_at']


@admin.register(TransactionChangeHistory)
class TransactionChangeHistoryAdmin(admin.ModelAdmin):
    list_display = ['transaction', 'field_changed', 'user', 'changed_at']
    search_fields = ['transaction__id', 'field_changed', 'user__username']
    list_filter = ['changed_at']
    readonly_fields = ['changed_at']


# Registrar User y Group de Django Auth
admin.site.unregister(User)
admin.site.unregister(Group)

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_active', 'date_joined']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    list_filter = ['is_active', 'is_staff', 'is_superuser', 'groups']
    filter_horizontal = ['groups', 'user_permissions']

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ['name']
    filter_horizontal = ['permissions']
