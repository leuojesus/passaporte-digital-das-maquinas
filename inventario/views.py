from io import BytesIO
from pathlib import Path
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.http import FileResponse, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_http_methods
import qrcode
from .forms import DocumentoForm, MaquinaForm, ManutencaoForm
from .models import Maquina, Documento

@login_required
def inicio(request):
    return render(request, "inventario/inicio.html", {
        "total_maquinas": Maquina.objects.filter(ativo=True).count(),
        "total_documentos": Documento.objects.count(),
    })

@login_required
@permission_required("inventario.view_maquina", raise_exception=True)
def maquinas(request):
    from django.db.models import Q
    q = request.GET.get("q", "").strip()[:100]
    itens = Maquina.objects.filter(ativo=True)
    if q:
        itens = itens.filter(Q(modelo__icontains=q) | Q(numero_serie__icontains=q))
    return render(request, "inventario/maquinas.html", {"maquinas": itens[:100], "q": q})

@login_required
@permission_required("inventario.gerenciar_maquinas", raise_exception=True)
@require_http_methods(["GET", "POST"])
def maquina_nova(request):
    form = MaquinaForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        maquina = form.save()
        messages.success(request, "Máquina salva com sucesso.")
        return redirect("maquina_editar", pk=maquina.pk)
    return render(request, "inventario/maquina_nova.html", {"form": form})

@login_required
@permission_required("inventario.gerenciar_maquinas", raise_exception=True)
@require_http_methods(["GET", "POST"])
def maquina_editar(request, pk):
    maquina = get_object_or_404(Maquina, pk=pk, ativo=True)
    acao = request.POST.get("acao") if request.method == "POST" else ""
    mf = MaquinaForm(request.POST if acao == "salvar_maquina" else None, instance=maquina, prefix="maquina")
    df = DocumentoForm(request.POST if acao == "adicionar_documento" else None,
                       request.FILES if acao == "adicionar_documento" else None, prefix="documento")
    if acao == "salvar_maquina" and mf.is_valid():
        mf.save()
        messages.success(request, "Máquina salva com sucesso.")
        return redirect("maquina_editar", pk=maquina.pk)
    if acao == "adicionar_documento" and df.is_valid():
        doc = df.save(commit=False)
        doc.maquina = maquina
        doc.criado_por = request.user
        doc.save()
        messages.success(request, "Documento adicionado com sucesso.")
        return redirect("maquina_editar", pk=maquina.pk)
    return render(request, "inventario/maquina_editar.html", {
        "maquina": maquina, "maquina_form": mf, "documento_form": df,
    })

@login_required
@permission_required("inventario.view_maquina", raise_exception=True)
@require_GET
def maquina_detalhe(request, pk):
    maquina = get_object_or_404(Maquina.objects.prefetch_related("documentos", "manutencoes"), pk=pk, ativo=True)
    return render(request, "inventario/maquina_detalhe.html", {"maquina": maquina})

@login_required
@permission_required("inventario.view_maquina", raise_exception=True)
@permission_required("inventario.view_documento", raise_exception=True)
@require_GET
def documento_abrir(request, pk):
    documento = get_object_or_404(Documento.objects.select_related("maquina"), pk=pk, maquina__ativo=True)
    try:
        arquivo = documento.arquivo.open("rb")
    except (OSError, FileNotFoundError, ValueError):
        messages.warning(request, "Arquivo não encontrado. Tente novamente ou contate o administrador.")
        return redirect("maquina_detalhe", pk=documento.maquina_id)
    tipo = {".pdf": "application/pdf", ".png": "image/png", ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg", ".webp": "image/webp"}.get(Path(documento.arquivo.name).suffix.lower(), "application/octet-stream")
    resposta = FileResponse(arquivo, content_type=tipo)
    resposta["Cache-Control"] = "private, no-store"
    resposta["Content-Security-Policy"] = "default-src 'none'; sandbox"
    return resposta

@login_required
@permission_required("inventario.view_maquina", raise_exception=True)
@require_GET
def maquina_qr(request, pk):
    maquina = get_object_or_404(Maquina, pk=pk, ativo=True)
    imagem = qrcode.make(request.build_absolute_uri(maquina.get_absolute_url()), box_size=8, border=3)
    memoria = BytesIO()
    imagem.save(memoria, format="PNG")
    resposta = HttpResponse(memoria.getvalue(), content_type="image/png")
    resposta["Cache-Control"] = "private, no-store"
    return resposta

@login_required
@permission_required("inventario.add_manutencao", raise_exception=True)
@require_http_methods(["GET", "POST"])
def manutencao_nova(request, pk):
    maquina = get_object_or_404(Maquina, pk=pk, ativo=True)
    form = ManutencaoForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        registro = form.save(commit=False)
        registro.maquina = maquina
        registro.usuario = request.user
        registro.save()
        messages.success(request, "Manutenção registrada com sucesso.")
        return redirect("maquina_detalhe", pk=maquina.pk)
    return render(request, "inventario/manutencao_nova.html", {"form": form, "maquina": maquina})
