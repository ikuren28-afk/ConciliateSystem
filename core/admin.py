from django.contrib import admin
from django.contrib.auth.models import User, Group
from .models import Role, Office, BankAccount, Operation, BankStatement, BankStatementTransaction, Notification, AuditLog, TransactionChangeHistory


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['name']
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
    list_display = ['bank_account', 'statement_date', 'file_name', 'entry_count', 'uploaded_by', 'created_at']
    search_fields = ['bank_account__code', 'file_name']
    list_filter = ['statement_date', 'bank_account', 'uploaded_by']
    readonly_fields = ['uploaded_by', 'created_at', 'updated_at']
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.uploaded_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(BankStatementTransaction)
class BankStatementTransactionAdmin(admin.ModelAdmin):
    list_display = ['current_reference', 'bank_account', 'office_code', 'amount', 'currency', 'reconciliation_status', 'reconciled_by', 'created_at']
    search_fields = ['current_reference', 'original_reference', 'name']
    list_filter = ['reconciliation_status', 'currency', 'office_code', 'bank_account']
    readonly_fields = ['reconciled_by', 'reconciled_at', 'created_at', 'updated_at']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'type', 'is_read', 'created_at']
    search_fields = ['user__username', 'content']
    list_filter = ['type', 'is_read']


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['action', 'model_name', 'user', 'timestamp']
    search_fields = ['action', 'model_name', 'user__username']
    list_filter = ['action', 'model_name', 'timestamp']
    readonly_fields = ['timestamp']


@admin.register(TransactionChangeHistory)
class TransactionChangeHistoryAdmin(admin.ModelAdmin):
    list_display = ['transaction', 'field_changed', 'user', 'changed_at']
    search_fields = ['transaction__id', 'field_changed', 'user__username']
    list_filter = ['changed_at']
    readonly_fields = ['changed_at']


# Configuración personalizada del admin
admin.site.site_header = 'Sistema de Conciliación Bancaria'
admin.site.site_title = 'Conciliación Bancaria - Admin'
admin.site.index_title = 'Panel de Administración'
