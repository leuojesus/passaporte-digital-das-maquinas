import uuid
from pathlib import Path
from django.conf import settings
from django.db import models
from django.urls import reverse

def caminho_documento(instance, filename):
    ext = Path(filename).suffix.lower()
    return f"documentos/{instance.maquina_id}/{uuid.uuid4().hex}{ext}"

class Maquina(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    numero_serie = models.CharField("Número de série", max_length=80, unique=True)
    modelo = models.CharField(max_length=150)
    cliente = models.CharField(max_length=160)
    descricao_tecnica = models.TextField("Descrição técnica", blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    ativo = models.BooleanField(default=True)
    class Meta:
        ordering = ["modelo", "numero_serie"]
        permissions = [("gerenciar_maquinas", "Pode gerenciar máquinas e documentos")]
    def __str__(self):
        return f"{self.modelo} — {self.numero_serie}"
    def get_absolute_url(self):
        return reverse("maquina_detalhe", args=[str(self.pk)])

class Documento(models.Model):
    CATEGORIAS = [
        ("manual", "Manual"), ("esquema", "Esquema elétrico"),
        ("componentes", "Lista de componentes"), ("configuracao", "Configuração"),
    ]
    maquina = models.ForeignKey(Maquina, on_delete=models.PROTECT, related_name="documentos")
    titulo = models.CharField(max_length=150)
    categoria = models.CharField(max_length=20, choices=CATEGORIAS)
    arquivo = models.FileField(upload_to=caminho_documento)
    criado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    criado_em = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ["categoria", "titulo"]
    def __str__(self):
        return f"{self.titulo} — {self.maquina.numero_serie}"

class Manutencao(models.Model):
    maquina = models.ForeignKey(Maquina, on_delete=models.PROTECT, related_name="manutencoes")
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    data_manutencao = models.DateField()
    problema = models.TextField()
    solucao = models.TextField("Solução aplicada")
    criado_em = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ["-data_manutencao", "-criado_em"]
