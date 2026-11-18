from django.contrib import admin
from .models import Maquina, Documento, Manutencao
@admin.register(Maquina)
class MaquinaAdmin(admin.ModelAdmin):
    list_display = ("modelo", "numero_serie", "cliente", "ativo")
    search_fields = ("modelo", "numero_serie", "cliente")
@admin.register(Documento)
class DocumentoAdmin(admin.ModelAdmin):
    list_display = ("titulo", "maquina", "categoria", "criado_em")
@admin.register(Manutencao)
class ManutencaoAdmin(admin.ModelAdmin):
    list_display = ("maquina", "data_manutencao", "usuario")
