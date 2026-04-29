#!/usr/bin/env python
"""
Script para inicializar los roles del sistema usando Django Groups.
Ejecutar con: python manage.py shell < core/scripts/init_roles.py
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bank_reconciliation.settings')
django.setup()

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from core.models import Role

def init_roles():
    """Crear los 4 roles principales del sistema"""
    
    # Lista de roles según especificaciones
    roles = [
        'Administrador',
        'Analista Financiero',
        'Analista Económico',
        'Analista Comercial'
    ]
    
    print("Inicializando roles del sistema...")
    
    # Crear grupos para cada rol
    for role_name in roles:
        group, created = Group.objects.get_or_create(name=role_name)
        if created:
            print(f"✓ Grupo '{role_name}' creado exitosamente.")
        else:
            print(f"- Grupo '{role_name}' ya existe.")
    
    # Crear entradas en la tabla Role (modelo personalizado)
    for role_name in roles:
        role, created = Role.objects.get_or_create(
            name=role_name,
            defaults={'name': role_name}
        )
        if created:
            print(f"✓ Rol '{role_name}' en modelo Role creado exitosamente.")
        else:
            print(f"- Rol '{role_name}' en modelo Role ya existe.")
    
    print("\n✅ Inicialización de roles completada.")
    print("\nRoles disponibles:")
    for group in Group.objects.all():
        print(f"  - {group.name}")

if __name__ == '__main__':
    init_roles()
