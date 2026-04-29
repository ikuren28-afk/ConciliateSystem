from django.db import models
import uuid


class Role(models.Model):
    """Modelo para los roles del sistema"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, unique=True)
    
    class Meta:
        db_table = 'roles'
        verbose_name = 'Rol'
        verbose_name_plural = 'Roles'
    
    def __str__(self):
        return self.name


class Office(models.Model):
    """Modelo para las oficinas"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'offices'
        verbose_name = 'Oficina'
        verbose_name_plural = 'Oficinas'
        indexes = [
            models.Index(fields=['code']),
        ]
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class BankAccount(models.Model):
    """Modelo para las cuentas bancarias"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'bank_accounts'
        verbose_name = 'Cuenta Bancaria'
        verbose_name_plural = 'Cuentas Bancarias'
        indexes = [
            models.Index(fields=['code']),
        ]
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class Operation(models.Model):
    """Modelo para los tipos de operaciones"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'operations'
        verbose_name = 'Tipo de Operación'
        verbose_name_plural = 'Tipos de Operaciones'
        indexes = [
            models.Index(fields=['code']),
        ]
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class BankStatement(models.Model):
    """Modelo para los estados de cuenta bancarios"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    bank_account = models.ForeignKey(
        BankAccount, 
        on_delete=models.CASCADE, 
        related_name='bank_statements',
        db_column='bank_account_id'
    )
    file_name = models.CharField(max_length=255)
    file_extension = models.CharField(max_length=10)
    file_size = models.DecimalField(max_digits=20, decimal_places=4)
    statement_date = models.DateField()
    starting_balance = models.DecimalField(max_digits=20, decimal_places=4)
    ending_balance = models.DecimalField(max_digits=20, decimal_places=4)
    overdraft_balance = models.DecimalField(max_digits=20, decimal_places=4, null=True, blank=True)
    reserved_balance = models.DecimalField(max_digits=20, decimal_places=4, null=True, blank=True)
    available_balance = models.DecimalField(max_digits=20, decimal_places=4, null=True, blank=True)
    entry_count = models.IntegerField()
    uploaded_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='uploaded_statements'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'bank_statements'
        verbose_name = 'Estado de Cuenta'
        verbose_name_plural = 'Estados de Cuenta'
        indexes = [
            models.Index(fields=['statement_date']),
            models.Index(fields=['bank_account']),
        ]
    
    def __str__(self):
        return f"{self.bank_account.code} - {self.statement_date}"


class BankStatementTransaction(models.Model):
    """Modelo para las transacciones de los estados de cuenta"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    bank_statement = models.ForeignKey(
        BankStatement,
        on_delete=models.CASCADE,
        related_name='transactions',
        db_column='bank_statement_id'
    )
    bank_account = models.ForeignKey(
        BankAccount,
        on_delete=models.CASCADE,
        related_name='transactions',
        db_column='bank_account_id'
    )
    current_reference = models.CharField(max_length=100, null=True, blank=True)
    original_reference = models.CharField(max_length=100, null=True, blank=True)
    name = models.CharField(max_length=255)
    office_code = models.CharField(max_length=20)
    entry_type = models.CharField(max_length=50)
    bank_fee = models.DecimalField(max_digits=20, decimal_places=4, default=0)
    amount = models.DecimalField(max_digits=20, decimal_places=4)
    currency = models.CharField(max_length=3)
    reconciliation_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pendiente'),
            ('reconciled', 'Conciliado'),
            ('discrepancy', 'Discrepancia'),
        ],
        default='pending'
    )
    reconciled_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reconciled_transactions'
    )
    reconciled_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'bank_statement_transactions'
        verbose_name = 'Transacción'
        verbose_name_plural = 'Transacciones'
        indexes = [
            models.Index(fields=['office_code']),
            models.Index(fields=['currency']),
            models.Index(fields=['reconciliation_status']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.current_reference or self.original_reference} - {self.amount} {self.currency}"


class Notification(models.Model):
    """Modelo para notificaciones del sistema"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE,
        related_name='notifications',
        db_column='user_id'
    )
    type = models.CharField(
        max_length=10,
        choices=[
            ('info', 'Información'),
            ('warning', 'Advertencia'),
            ('error', 'Error'),
        ]
    )
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'notifications'
        verbose_name = 'Notificación'
        verbose_name_plural = 'Notificaciones'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.type} - {self.user.username}"


class AuditLog(models.Model):
    """Modelo para registro de auditoría"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='audit_logs'
    )
    action = models.CharField(max_length=50)
    model_name = models.CharField(max_length=100)
    object_id = models.UUIDField(null=True, blank=True)
    changes = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'audit_logs'
        verbose_name = 'Registro de Auditoría'
        verbose_name_plural = 'Registros de Auditoría'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['user']),
            models.Index(fields=['model_name']),
        ]
    
    def __str__(self):
        return f"{self.action} - {self.model_name} - {self.timestamp}"


class TransactionChangeHistory(models.Model):
    """Modelo para historial de cambios en transacciones"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    transaction = models.ForeignKey(
        BankStatementTransaction,
        on_delete=models.CASCADE,
        related_name='change_history'
    )
    user = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True
    )
    field_changed = models.CharField(max_length=100)
    old_value = models.TextField(null=True, blank=True)
    new_value = models.TextField(null=True, blank=True)
    changed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'transaction_change_history'
        verbose_name = 'Historial de Cambios'
        verbose_name_plural = 'Historial de Cambios'
        ordering = ['-changed_at']
    
    def __str__(self):
        return f"{self.transaction.id} - {self.field_changed} - {self.changed_at}"
