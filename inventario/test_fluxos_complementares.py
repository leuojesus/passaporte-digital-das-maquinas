"""Testes complementares dos fluxos administrativos e documentos do MVP."""
from io import BytesIO
from tempfile import TemporaryDirectory
from django.contrib.auth.models import Group, User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse
from PIL import Image

from .forms import DocumentoForm
from .models import Documento, Maquina, Manutencao


class TestesFluxoAdministrativo(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            "admin_fluxo", "admin-fluxo@exemplo.invalid", "SenhaSegura123!Teste"
        )
        self.maquina = Maquina.objects.create(
            modelo="Serra Industrial", numero_serie="FLUXO-001", cliente="Empresa Fictícia"
        )
        self.client.force_login(self.admin)

    def test_inicio_mostra_acoes_e_catalogo_vazio_sem_filtro(self):
        resposta = self.client.get(reverse("inicio"))
        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, "Cadastrar máquina")
        resposta_lista = self.client.get(reverse("maquinas"))
        self.assertContains(resposta_lista, "FLUXO-001")

    def test_alterar_maquina_com_formulario_prefixado(self):
        url = reverse("maquina_editar", args=[self.maquina.pk])
        self.assertEqual(self.client.get(url).status_code, 200)
        resposta = self.client.post(url, {
            "acao": "salvar_maquina",
            "maquina-modelo": "Serra Atualizada",
            "maquina-numero_serie": "FLUXO-001",
            "maquina-cliente": "Empresa Fictícia",
            "maquina-descricao_tecnica": "Configuração atualizada",
        })
        self.assertEqual(resposta.status_code, 302)
        self.maquina.refresh_from_db()
        self.assertEqual(self.maquina.modelo, "Serra Atualizada")

    def test_anexar_e_abrir_pdf_privado(self):
        url = reverse("maquina_editar", args=[self.maquina.pk])
        with TemporaryDirectory() as pasta:
            with self.settings(MEDIA_ROOT=pasta):
                resposta = self.client.post(url, {
                    "acao": "adicionar_documento",
                    "documento-titulo": "Manual",
                    "documento-categoria": "manual",
                    "documento-arquivo": SimpleUploadedFile(
                        "manual.pdf", b"%PDF-1.4\nexemplo de teste\n",
                        content_type="application/pdf",
                    ),
                })
                self.assertEqual(resposta.status_code, 302)
                documento = Documento.objects.get(maquina=self.maquina)
                resposta_arquivo = self.client.get(
                    reverse("documento_abrir", args=[documento.pk])
                )
                self.assertEqual(resposta_arquivo.status_code, 200)
                self.assertEqual(resposta_arquivo["Content-Type"], "application/pdf")
                resposta_arquivo.close()

    def test_arquivo_ausente_exibe_alerta_e_redireciona(self):
        documento = Documento.objects.create(
            maquina=self.maquina, criado_por=self.admin, titulo="Esquema",
            categoria="esquema", arquivo="documentos/ausente.pdf",
        )
        resposta = self.client.get(
            reverse("documento_abrir", args=[documento.pk]), follow=True
        )
        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, "Arquivo não encontrado")

    def test_registrar_manutencao_e_consultar_historico(self):
        url = reverse("manutencao_nova", args=[self.maquina.pk])
        self.assertEqual(self.client.get(url).status_code, 200)
        resposta = self.client.post(url, {
            "data_manutencao": "2026-11-18",
            "problema": "Sensor desalinhado",
            "solucao": "Sensor ajustado e testado",
        })
        self.assertEqual(resposta.status_code, 302)
        self.assertEqual(Manutencao.objects.filter(maquina=self.maquina).count(), 1)
        ficha = self.client.get(self.maquina.get_absolute_url())
        self.assertContains(ficha, "Sensor desalinhado")

    def test_endereco_e_descricao_dos_modelos(self):
        self.assertIn("FLUXO-001", str(self.maquina))
        self.assertIn(str(self.maquina.pk), self.maquina.get_absolute_url())
        doc = Documento.objects.create(
            maquina=self.maquina, criado_por=self.admin, titulo="Manual",
            categoria="manual", arquivo="documentos/exemplo.pdf",
        )
        self.assertIn("Manual", str(doc))
        self.assertIn("FLUXO-001", str(doc))


class TestesValidacaoArquivos(TestCase):
    def criar_formulario(self, nome, conteudo):
        return DocumentoForm(
            data={"titulo": "Manual", "categoria": "manual"},
            files={"arquivo": SimpleUploadedFile(nome, conteudo)},
        )

    def test_pdf_valido_e_aceito(self):
        self.assertTrue(self.criar_formulario("manual.pdf", b"%PDF-1.4\nconteudo").is_valid())

    def test_extensao_executavel_rejeitada(self):
        form = self.criar_formulario("programa.exe", b"arquivo de teste")
        self.assertFalse(form.is_valid())
        self.assertIn("arquivo", form.errors)

    def test_imagem_png_valida_e_aceita(self):
        imagem = Image.new("RGB", (4, 4), "white")
        buffer = BytesIO()
        imagem.save(buffer, format="PNG")
        self.assertTrue(self.criar_formulario("esquema.png", buffer.getvalue()).is_valid())

    def test_imagem_com_extensao_incorreta_rejeitada(self):
        imagem = Image.new("RGB", (4, 4), "white")
        buffer = BytesIO()
        imagem.save(buffer, format="JPEG")
        self.assertFalse(self.criar_formulario("esquema.png", buffer.getvalue()).is_valid())

    def test_imagem_corrompida_rejeitada(self):
        self.assertFalse(self.criar_formulario("esquema.png", b"imagem corrompida").is_valid())


class TestesConfiguracaoPerfis(TestCase):
    def test_comando_cria_grupos_e_permissoes(self):
        call_command("configurar_perfis")
        administrador = Group.objects.get(name="Administrador")
        tecnico = Group.objects.get(name="Tecnico")
        self.assertTrue(administrador.permissions.filter(codename="gerenciar_maquinas").exists())
        self.assertTrue(tecnico.permissions.filter(codename="view_maquina").exists())
        self.assertFalse(tecnico.permissions.filter(codename="gerenciar_maquinas").exists())
