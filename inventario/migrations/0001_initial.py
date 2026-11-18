import uuid
import django.db.models.deletion
import inventario.models
from django.conf import settings
from django.db import migrations, models
class Migration(migrations.Migration):
    initial = True
    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [
        migrations.CreateModel(name="Maquina", fields=[
            ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
            ("numero_serie", models.CharField(max_length=80, unique=True, verbose_name="Número de série")),
            ("modelo", models.CharField(max_length=150)),
            ("cliente", models.CharField(max_length=160)),
            ("descricao_tecnica", models.TextField(blank=True, verbose_name="Descrição técnica")),
            ("criado_em", models.DateTimeField(auto_now_add=True)),
            ("ativo", models.BooleanField(default=True)),
        ], options={"ordering": ["modelo", "numero_serie"], "permissions": [("gerenciar_maquinas", "Pode gerenciar máquinas e documentos")]}),
        migrations.CreateModel(name="Documento", fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("titulo", models.CharField(max_length=150)),
            ("categoria", models.CharField(choices=[
                ("manual", "Manual"), ("esquema", "Esquema elétrico"),
                ("componentes", "Lista de componentes"), ("configuracao", "Configuração"),
            ], max_length=20)),
            ("arquivo", models.FileField(upload_to=inventario.models.caminho_documento)),
            ("criado_em", models.DateTimeField(auto_now_add=True)),
            ("criado_por", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ("maquina", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="documentos", to="inventario.maquina")),
        ], options={"ordering": ["categoria", "titulo"]}),
        migrations.CreateModel(name="Manutencao", fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("data_manutencao", models.DateField()),
            ("problema", models.TextField()),
            ("solucao", models.TextField(verbose_name="Solução aplicada")),
            ("criado_em", models.DateTimeField(auto_now_add=True)),
            ("maquina", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="manutencoes", to="inventario.maquina")),
            ("usuario", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
        ], options={"ordering": ["-data_manutencao", "-criado_em"]}),
    ]
