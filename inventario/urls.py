from django.urls import path
from . import views
urlpatterns = [
    path("", views.inicio, name="inicio"),
    path("maquinas/", views.maquinas, name="maquinas"),
    path("maquinas/nova/", views.maquina_nova, name="maquina_nova"),
    path("maquinas/<uuid:pk>/", views.maquina_detalhe, name="maquina_detalhe"),
    path("maquinas/<uuid:pk>/editar/", views.maquina_editar, name="maquina_editar"),
    path("maquinas/<uuid:pk>/qr.png", views.maquina_qr, name="maquina_qr"),
    path("documentos/<int:pk>/abrir/", views.documento_abrir, name="documento_abrir"),
    path("maquinas/<uuid:pk>/manutencoes/nova/", views.manutencao_nova, name="manutencao_nova"),
]
