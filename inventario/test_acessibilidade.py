"""Teste da interface de acessibilidade disponibilizada no Django."""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class TesteAltoContraste(TestCase):
    def setUp(self):
        self.usuario = get_user_model().objects.create_superuser(
            "admin_acessibilidade", "acessibilidade@exemplo.invalid",
            "SenhaFicticiaDeTeste!2026",
        )
        self.client.force_login(self.usuario)

    def test_menu_oferece_controle_de_alto_contraste(self):
        resposta = self.client.get(reverse("inicio"))
        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, 'id="alternar-contraste"')
        self.assertContains(resposta, 'aria-pressed="false"')
        self.assertContains(resposta, "js/acessibilidade.js")
