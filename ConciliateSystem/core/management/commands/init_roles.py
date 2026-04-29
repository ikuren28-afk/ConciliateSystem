from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, User
from core.models import Role
import uuid

class Command(BaseCommand):
    help = 'Inicializa los roles y grupos del sistema'

    def handle(self, *args, **options):
        # Roles definidos en el sistema
        roles_data = [
            {'name': 'Administrador'},
            {'name': 'Analista financiero'},
            {'name': 'Analista económico'},
            {'name': 'Analista comercial'},
        ]

        # Crear roles en la tabla Role
        for role_data in roles_data:
            role, created = Role.objects.get_or_create(
                name=role_data['name'],
                defaults={'id': uuid.uuid4()}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Rol "{role.name}" creado exitosamente'))
            else:
                self.stdout.write(self.style.WARNING(f'Rol "{role.name}" ya existe'))

        # Crear grupos de Django (para permisos)
        groups_data = [
            {'name': 'Administrador', 'permissions': ['add', 'change', 'delete', 'view']},
            {'name': 'Analista financiero', 'permissions': ['add', 'view']},
            {'name': 'Analista económico', 'permissions': ['change', 'view']},
            {'name': 'Analista comercial', 'permissions': ['view']},
        ]

        for group_data in groups_data:
            group, created = Group.objects.get_or_create(name=group_data['name'])
            if created:
                self.stdout.write(self.style.SUCCESS(f'Grupo "{group.name}" creado exitosamente'))
            else:
                self.stdout.write(self.style.WARNING(f'Grupo "{group.name}" ya existe'))

        self.stdout.write(self.style.SUCCESS('\nInicialización de roles y grupos completada'))
        self.stdout.write(self.style.SUCCESS('\nRoles disponibles:'))
        for role in Role.objects.all():
            self.stdout.write(f'  - {role.name}')
        
        self.stdout.write(self.style.SUCCESS('\nGrupos disponibles:'))
        for group in Group.objects.all():
            self.stdout.write(f'  - {group.name}')
