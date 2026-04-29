from django.db import models
import uuid


class Role(models.Model):
    """Modelo para roles del sistema"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True, null=False)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'roles'
        verbose_name = 'Rol'
        verbose_name_plural = 'Roles'


class Office(models.Model):
    """Modelo para oficinas"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=50, unique=True, null=False)
    name = models.CharField(max_length=200, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.code} - {self.name}'

    class Meta:
        db_table = 'offices'
        verbose_name = 'Oficina'
        verbose_name_plural = 'Oficinas'
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['name']),
        ]


class BankAccount(models.Model):
    """Modelo para cuentas bancarias"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=50, unique=True, null=False)
    name = models.CharField(max_length=200, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.code} - {self.name}'

    class Meta:
        db_table = 'bank_accounts'
        verbose_name = 'Cuenta Bancaria'
        verbose_name_plural = 'Cuentas Bancarias'
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['name']),
        ]


class Operation(models.Model):
    """Modelo para tipos de operaciones"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=50, unique=True, null=False)
    name = models.CharField(max_length=200, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.code} - {self.name}'

    class Meta:
        db_table = 'operations'
        verbose_name = 'Tipo de Operación'
        verbose_name_plural = 'Tipos de Operaciones'
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['name']),
        ]


class BankStatement(models.Model):
    """Modelo para estados de cuenta bancarios"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    bank_account = models.ForeignKey(BankAccount, on_delete=models.CASCADE, related_name='statements')
    file_name = models.CharField(max_length=255, blank=True, null=True)
    file_extension = models.CharField(max_length=10, blank=True, null=True)
    file_size = models.DecimalField(max_digits=20, decimal_places=4, blank=True, null=True)
    statement_date = models.DateField(blank=True, null=True)
    starting_balance = models.DecimalField(max_digits=20, decimal_places=4, blank=True, null=True)
    ending_balance = models.DecimalField(max_digits=20, decimal_places=4, blank=True, null=True)
    overdraft_balance = models.DecimalField(max_digits=20, decimal_places=4, blank=True, null=True)
    reserved_balance = models.DecimalField(max_digits=20, decimal_places=4, blank=True, null=True)
    available_balance = models.DecimalField(max_digits=20, decimal_places=4, blank=True, null=True)
    entry_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    uploaded_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, related_name='uploaded_statements')

    def __str__(self):
        return f'{self.bank_account.name} - {self.statement_date}'

    class Meta:
        db_table = 'bank_statements'
        verbose_name = 'Estado de Cuenta'
        verbose_name_plural = 'Estados de Cuenta'
        indexes = [
            models.Index(fields=['bank_account', 'statement_date']),
            models.Index(fields=['created_at']),
        ]


class BankStatementTransaction(models.Model):
    """Modelo para transacciones de estados de cuenta"""
    RECONCILIATION_STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('reconciled', 'Conciliado'),
        ('discrepancy', 'Discrepancia'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    bank_statement = models.ForeignKey(BankStatement, on_delete=models.CASCADE, related_name='transactions')
    current_reference = models.CharField(max_length=255, blank=True, null=True)
    original_reference = models.CharField(max_length=255, blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    bank_account = models.ForeignKey(BankAccount, on_delete=models.CASCADE, related_name='transactions')
    office_code = models.CharField(max_length=50, blank=True, null=True)
    entry_type = models.CharField(max_length=50, blank=True, null=True)
    bank_fee = models.DecimalField(max_digits=20, decimal_places=4, default=0)
    amount = models.DecimalField(max_digits=20, decimal_places=4)
    currency = models.CharField(max_length=3, default='USD')
    reconciliation_status = models.CharField(max_length=20, choices=RECONCILIATION_STATUS_CHOICES, default='pending')
    reconciled_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='reconciled_transactions')
    reconciled_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.current_reference or "N/A"} - {self.amount}'

    class Meta:
        db_table = 'bank_statement_transactions'
        verbose_name = 'Transacción de Estado de Cuenta'
        verbose_name_plural = 'Transacciones de Estados de Cuenta'
        indexes = [
            models.Index(fields=['bank_statement', 'created_at']),
            models.Index(fields=['office_code']),
            models.Index(fields=['currency']),
            models.Index(fields=['reconciliation_status']),
            models.Index(fields=['entry_type']),
        ]


class Notification(models.Model):
    """Modelo para notificaciones del sistema"""
    NOTIFICATION_TYPE_CHOICES = [
        ('info', 'Información'),
        ('warning', 'Advertencia'),
        ('error', 'Error'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='notifications')
    type = models.CharField(max_length=10, choices=NOTIFICATION_TYPE_CHOICES)
    content = models.TextField()
    read_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.type} - {self.user.username}'

    class Meta:
        db_table = 'notifications'
        verbose_name = 'Notificación'
        verbose_name_plural = 'Notificaciones'
        indexes = [
            models.Index(fields=['user', 'read_at']),
            models.Index(fields=['type']),
            models.Index(fields=['created_at']),
        ]


class AuditLog(models.Model):
    """Modelo para registro de auditoría"""
    ACTION_CHOICES = [
        ('CREATE', 'Crear'),
        ('UPDATE', 'Actualizar'),
        ('DELETE', 'Eliminar'),
        ('UPLOAD', 'Subir'),
        ('RECONCILE', 'Conciliar'),
        ('LOGIN', 'Iniciar sesión'),
        ('LOGOUT', 'Cerrar sesión'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, related_name='audit_logs')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    model_name = models.CharField(max_length=100)
    object_id = models.UUIDField(blank=True, null=True)
    description = models.TextField()
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.action} - {self.model_name} - {self.user.username if self.user else "Anonymous"}'

    class Meta:
        db_table = 'audit_logs'
        verbose_name = 'Registro de Auditoría'
        verbose_name_plural = 'Registros de Auditoría'
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['action']),
            models.Index(fields=['model_name']),
        ]


class TransactionChangeHistory(models.Model):
    """Modelo para historial de cambios en transacciones"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    transaction = models.ForeignKey(BankStatementTransaction, on_delete=models.CASCADE, related_name='change_history')
    user = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True)
    field_changed = models.CharField(max_length=100)
    old_value = models.TextField(blank=True, null=True)
    new_value = models.TextField(blank=True, null=True)
    changed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.transaction.id} - {self.field_changed} - {self.changed_at}'

    class Meta:
        db_table = 'transaction_change_history'
        verbose_name = 'Historial de Cambios de Transacción'
        verbose_name_plural = 'Historiales de Cambios de Transacciones'
        indexes = [
            models.Index(fields=['transaction', 'changed_at']),
            models.Index(fields=['user', 'changed_at']),
        ]
