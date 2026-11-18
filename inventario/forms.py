from pathlib import Path
from PIL import Image, UnidentifiedImageError
from django import forms
from django.core.exceptions import ValidationError
from .models import Maquina, Documento, Manutencao

class FormBase:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for campo in self.fields.values():
            campo.widget.attrs["class"] = "form-control"
            if campo.required:
                campo.widget.attrs["aria-required"] = "true"

class MaquinaForm(FormBase, forms.ModelForm):
    class Meta:
        model = Maquina
        fields = ["modelo", "numero_serie", "cliente", "descricao_tecnica"]
        widgets = {"descricao_tecnica": forms.Textarea(attrs={"rows": 3})}

class DocumentoForm(FormBase, forms.ModelForm):
    class Meta:
        model = Documento
        fields = ["titulo", "categoria", "arquivo"]
    def clean_arquivo(self):
        arquivo = self.cleaned_data["arquivo"]
        if arquivo.size > 10 * 1024 * 1024:
            raise ValidationError("O arquivo deve ter no máximo 10 MB.")
        ext = Path(arquivo.name).suffix.lower()
        if ext not in (".pdf", ".png", ".jpg", ".jpeg", ".webp"):
            raise ValidationError("Aceitos apenas PDF e imagens.")
        inicio = arquivo.read(16)
        arquivo.seek(0)
        if ext == ".pdf":
            if not inicio.startswith(b"%PDF-"):
                raise ValidationError("Conteúdo PDF inválido.")
        else:
            try:
                imagem = Image.open(arquivo)
                imagem.verify()
                tipos = {".png": "PNG", ".jpg": "JPEG", ".jpeg": "JPEG", ".webp": "WEBP"}
                if imagem.format != tipos[ext]:
                    raise ValidationError("O formato do arquivo não corresponde à extensão.")
            except (UnidentifiedImageError, OSError, ValueError) as exc:
                raise ValidationError("Imagem inválida.") from exc
            finally:
                arquivo.seek(0)
        return arquivo

class ManutencaoForm(FormBase, forms.ModelForm):
    class Meta:
        model = Manutencao
        fields = ["data_manutencao", "problema", "solucao"]
        widgets = {"data_manutencao": forms.DateInput(attrs={"type": "date"})}
