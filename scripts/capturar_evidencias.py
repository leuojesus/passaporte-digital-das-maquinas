"""Gera capturas REAIS de um servidor Django aberto em navegador Chromium.

Uso em CI: python scripts/capturar_evidencias.py
As capturas usam apenas dados fictícios criados no banco temporário de testes.
"""
import os
import sys
import time
import subprocess
import urllib.request
from pathlib import Path

# Ao executar um arquivo de scripts/, incluir o diretório raiz no sys.path.
RAIZ_PROJETO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ_PROJETO))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django
django.setup()

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from inventario.models import Maquina, Documento
from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:8000"
DESTINO = Path("evidencias_reais")
DESTINO.mkdir(exist_ok=True)
USUARIO = "administrador.demo"
SENHA = "SenhaFicticiaParaTeste!2026"

User = get_user_model()
administrador, novo = User.objects.get_or_create(username=USUARIO, defaults={
    "email": "demonstracao@exemplo.invalid", "is_staff": True, "is_superuser": True,
})
administrador.set_password(SENHA)
administrador.is_staff = True
administrador.is_superuser = True
administrador.save()

maquina, _ = Maquina.objects.get_or_create(
    numero_serie="TCN-2026-001",
    defaults={"modelo": "Tecnoação Corte 2000", "cliente": "Empresa Exemplo Ltda.",
              "descricao_tecnica": "Máquina industrial de corte — dados fictícios de demonstração."}
)
if not maquina.documentos.filter(titulo="Manual Técnico.pdf").exists():
    doc = Documento(maquina=maquina, titulo="Manual Técnico.pdf",
                    categoria="manual", criado_por=administrador)
    doc.arquivo.save("manual_demonstracao.pdf",
                    ContentFile(b"%PDF-1.4\\n% Arquivo ficticio para testes\\n%%EOF\\n"), save=True)
if not maquina.documentos.filter(titulo="Esquema Elétrico.pdf").exists():
    doc = Documento(maquina=maquina, titulo="Esquema Elétrico.pdf",
                    categoria="esquema", criado_por=administrador)
    doc.arquivo.save("esquema_demonstracao.pdf",
                    ContentFile(b"%PDF-1.4\\n% Arquivo ficticio para testes\\n%%EOF\\n"), save=True)

log = open("/tmp/passaporte-django-demo.log", "w", encoding="utf-8")
server = subprocess.Popen([sys.executable, "manage.py", "runserver", "--noreload", "127.0.0.1:8000"],
                          stdout=log, stderr=subprocess.STDOUT)
try:
    for tent in range(70):
        try:
            urllib.request.urlopen(BASE + "/entrar/", timeout=2).close()
            break
        except Exception:
            if server.poll() is not None:
                raise RuntimeError("Servidor Django encerrou; consulte o log.")
            time.sleep(0.5)
    else:
        raise RuntimeError("Servidor Django não ficou disponível.")
    with sync_playwright() as playwright:
        try:
            browser = playwright.chromium.launch(channel="chrome", headless=True, args=["--no-sandbox"])
        except Exception:
            browser = playwright.chromium.launch(headless=True, args=["--no-sandbox"])
        context = browser.new_context(
            viewport={"width": 390, "height": 844}, device_scale_factor=1,
            is_mobile=True, has_touch=True, locale="pt-BR",
        )
        page = context.new_page()
        erros_js = []
        page.on("pageerror", lambda erro: erros_js.append(str(erro)))
        page.goto(BASE + "/entrar/", wait_until="domcontentloaded")
        page.locator("#id_username").fill(USUARIO)
        page.locator("#id_password").fill(SENHA)
        page.get_by_role("button", name="Entrar").click()
        page.wait_for_url(BASE + "/", timeout=20000)
        assert "Cadastrar máquina" in page.locator("body").inner_text()
        page.screenshot(path=str(DESTINO / "01_menu_inicial_real.png"), full_page=True)

        page.goto(BASE + f"/maquinas/{maquina.pk}/editar/", wait_until="domcontentloaded")
        page.get_by_text("Documentos Técnicos").first.wait_for()
        page.get_by_text("QR Code da máquina").wait_for()
        assert "Manual Técnico.pdf" in page.locator("body").inner_text()
        page.locator(".qr-panel img").wait_for(state="visible")
        page.wait_for_function("() => { const img = document.querySelector('.qr-panel img'); return img && img.complete && img.naturalWidth > 0; }")
        page.screenshot(path=str(DESTINO / "02_cadastro_documentos_real.png"), full_page=True)

        page.goto(BASE + str(maquina.get_absolute_url()), wait_until="domcontentloaded")
        page.get_by_text("Documentos disponíveis").wait_for()
        assert "Manual Técnico.pdf" in page.locator("body").inner_text()
        botao = page.locator("#alternar-contraste")
        botao.click()
        assert botao.get_attribute("aria-pressed") == "true"
        assert page.evaluate("document.documentElement.classList.contains('alto-contraste')")
        page.screenshot(path=str(DESTINO / "03_ficha_alto_contraste_real.png"), full_page=True)

        if erros_js:
            raise RuntimeError("Erro de JavaScript: " + "; ".join(erros_js))
        print("CAPTURAS_REAIS_OK")
        print("Telas geradas:", *[p.name for p in DESTINO.glob("*.png")], sep="\\n - ")
        print("Dispositivo emulado: navegador Chromium, viewport móvel 390×844.")
        print("Recurso demonstrado: botão de alto contraste ativado em execução.")
        browser.close()
finally:
    server.terminate()
    try:
        server.wait(timeout=10)
    except subprocess.TimeoutExpired:
        server.kill()
    log.close()
