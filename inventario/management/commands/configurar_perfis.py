from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
class Command(BaseCommand):
    help = "Configura os grupos de acesso do MVP."
    def handle(self, *args, **kwargs):
        admin, _ = Group.objects.get_or_create(name="Administrador")
        tecnico, _ = Group.objects.get_or_create(name="Tecnico")
        admin.permissions.set(Permission.objects.filter(content_type__app_label="inventario"))
        tecnico.permissions.set(Permission.objects.filter(
            content_type__app_label="inventario",
            codename__in=["view_maquina", "view_documento", "view_manutencao", "add_manutencao"],
        ))
        self.stdout.write(self.style.SUCCESS("Grupos configurados. Atribua usuários no Django Admin."))
