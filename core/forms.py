from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Office, BankAccount, Operation, BankStatement


class LoginForm(AuthenticationForm):
    """Formulario personalizado para login"""
    
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nombre de usuario',
            'autofocus': True
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Contraseña'
        })
    )


class CustomUserCreationForm(UserCreationForm):
    """Formulario personalizado para registro de usuarios"""
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Correo electrónico'
        })
    )
    first_name = forms.CharField(
        required=True,
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nombre'
        })
    )
    last_name = forms.CharField(
        required=True,
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Apellido'
        })
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Nombre de usuario'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Contraseña'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirmar contraseña'
        })


class OfficeForm(forms.ModelForm):
    """Formulario para gestionar oficinas"""
    
    class Meta:
        model = Office
        fields = ['code', 'name']
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Código'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre'})
        }


class BankAccountForm(forms.ModelForm):
    """Formulario para gestionar cuentas bancarias"""
    
    class Meta:
        model = BankAccount
        fields = ['code', 'name']
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Código'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre'})
        }


class OperationForm(forms.ModelForm):
    """Formulario para gestionar tipos de operaciones"""
    
    class Meta:
        model = Operation
        fields = ['code', 'name']
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Código'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre'})
        }


class BankStatementForm(forms.ModelForm):
    """Formulario para cargar estados de cuenta bancario"""
    
    file = forms.FileField(
        label='Archivo del estado de cuenta',
        required=True,
        help_text='Solo se permiten archivos .xml o .txt (máximo 5 MB)'
    )
    
    class Meta:
        model = BankStatement
        fields = ['bank_account_id', 'statement_date', 'starting_balance', 'ending_balance', 
                  'overdraft_balance', 'reserved_balance', 'available_balance', 'file']
        widgets = {
            'bank_account_id': forms.Select(attrs={'class': 'form-control'}),
            'statement_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'starting_balance': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'ending_balance': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'overdraft_balance': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'reserved_balance': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'available_balance': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'file': forms.FileInput(attrs={'class': 'form-control'})
        }
    
    def clean_file(self):
        """Validar extensión y tamaño del archivo"""
        file = self.cleaned_data.get('file')
        if file:
            # Validar extensión
            allowed_extensions = ['.xml', '.txt']
            file_extension = file.name.lower().split('.')[-1]
            if f'.{file_extension}' not in allowed_extensions:
                raise ValidationError('Solo se permiten archivos con extensión .xml o .txt')
            
            # Validar tamaño (5 MB = 5 * 1024 * 1024 bytes)
            max_size = 5 * 1024 * 1024
            if file.size > max_size:
                raise ValidationError('El tamaño del archivo no puede superar los 5 MB')
            
            return file
        return None
