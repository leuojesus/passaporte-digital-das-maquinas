from django.contrib import admin
from django.urls import include, path
from django.contrib.auth.views import LoginView, LogoutView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("entrar/", LoginView.as_view(template_name="registration/login.html"), name="login"),
    path("sair/", LogoutView.as_view(), name="logout"),
    path("", include("inventario.urls")),
]
