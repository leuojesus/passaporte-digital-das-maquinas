"""Testes de regressão do fluxo central e das permissões do MVP.

Executar: python manage.py test
"""
from django.contrib.auth.models import Permission, User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from .forms import DocumentoForm
from .models import Documento, Maquina


class FluxoDeMaquinasTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            "admin_testes", "admin@exemplo.invalid", "SenhaSegura123!Teste"
        )
        self.maquina = Maquina.objects.create(
            modelo="Corte 2000", numero_serie="TCN-001",
            cliente="Empresa Exemplo Ltda."
        )

    def test_administrador_cadastra_maquina(self):
        self.client.force_login(self.admin)
        resposta = self.client.post(reverse("maquina_nova"), {
            "modelo": "Centro de usinagem",
            "numero_serie": "TCN-002",
            "cliente": "Cliente Fictício",
            "descricao_tecnica": "Exemplo de cadastro",
        })
        self.assertEqual(resposta.status_code, 302)
        self.assertTrue(Maquina.objects.filter(numero_serie="TCN-002").exists())

    def test_formulario_impede_numero_de_serie_duplicado(self):
        self.client.force_login(self.admin)
        resposta = self.client.post(reverse("maquina_nova"), {
            "modelo": "Máquina repetida", "numero_serie": "TCN-001",
            "cliente": "Cliente Fictício",
        })
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(Maquina.objects.filter(numero_serie="TCN-001").count(), 1)

    def test_catalogo_paginar_dez_por_vez(self):
        Maquina.objects.bulk_create([
            Maquina(modelo="Modelo", numero_serie=f"TCN-{n:03d}", cliente="Fictício")
            for n in range(2, 22)
        ])
        self.client.force_login(self.admin)
        resposta = self.client.get(reverse("maquinas"), {"page": "2"})
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.context["page_obj"].number, 2)
        self.assertEqual(len(resposta.context["maquinas"]), 10)
        self.assertContains(resposta, "Anterior")

    def test_qr_exige_login(self):
        resposta = self.client.get(reverse("maquina_qr", args=[self.maquina.pk]))
        self.assertEqual(resposta.status_code, 302)
        self.assertIn("/entrar/", resposta.url)


class SegurancaDocumentalTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            "admin_documentos", "doc@exemplo.invalid", "SenhaSegura123!Teste"
        )
        self.visitante = User.objects.create_user(
            "visitante", password="SenhaSegura123!Teste"
        )
        self.maquina = Maquina.objects.create(
            modelo="Corte 2000", numero_serie="DOC-001", cliente="Fictício"
        )
        # Referência fictícia: o teste de permissão ocorre antes do acesso físico.
        self.documento = Documento.objects.create(
            maquina=self.maquina, criado_por=self.admin,
            titulo="Manual", categoria="manual",
            arquivo="documentos/nao-publico/manual.pdf",
        )

    def test_anônimo_nao_acessa_arquivo(self):
        resposta = self.client.get(reverse("documento_abrir", args=[self.documento.pk]))
        self.assertEqual(resposta.status_code, 302)
        self.assertIn("/entrar/", resposta.url)

    def test_usuario_sem_permissoes_nao_acessa_documento(self):
        self.client.force_login(self.visitante)
        resposta = self.client.get(reverse("documento_abrir", args=[self.documento.pk]))
        self.assertEqual(resposta.status_code, 403)

    def test_so_permissao_de_documento_nao_basta(self):
        permissao = Permission.objects.get(
            content_type__app_label="inventario", codename="view_documento"
        )
        self.visitante.user_permissions.add(permissao)
        self.client.force_login(self.visitante)
        resposta = self.client.get(reverse("documento_abrir", args=[self.documento.pk]))
        self.assertEqual(resposta.status_code, 403)

    def test_upload_pdf_com_conteudo_invalido_e_rejeitado(self):
        arquivo = SimpleUploadedFile("manual.pdf", b"isto-nao-e-pdf")
        formulario = DocumentoForm(
            data={"titulo": "Manual", "categoria": "manual"},
            files={"arquivo": arquivo},
        )
        self.assertFalse(formulario.is_valid())
        self.assertIn("arquivo", formulario.errors)

    def test_login_tem_rotulos_e_senha_oculta(self):
        resposta = self.client.get(reverse("login"))
        self.assertContains(resposta, 'for="id_username"')
        self.assertContains(resposta, 'for="id_password"')
        self.assertContains(resposta, 'type="password"')
