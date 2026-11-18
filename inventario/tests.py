from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Maquina

class TestesBasicos(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser("teste_admin", "teste@exemplo.invalid", "SenhaDeTesteSegura123!")
        self.maquina = Maquina.objects.create(modelo="Corte 2000", numero_serie="TESTE-001", cliente="Cliente Fictício")
    def test_login_exigido(self):
        resposta = self.client.get(self.maquina.get_absolute_url())
        self.assertEqual(resposta.status_code, 302)
        self.assertIn("/entrar/", resposta.url)
    def test_ficha_acessivel_para_autorizado(self):
        self.client.force_login(self.admin)
        resposta = self.client.get(self.maquina.get_absolute_url())
        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, "TESTE-001")
    def test_qr_code_retorna_imagem(self):
        self.client.force_login(self.admin)
        resposta = self.client.get(reverse("maquina_qr", args=[str(self.maquina.pk)]))
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta["Content-Type"], "image/png")
    def test_serie_unica(self):
        from django.db import IntegrityError, transaction
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Maquina.objects.create(modelo="Outra", numero_serie="TESTE-001", cliente="Cliente")
