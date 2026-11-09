from django.urls import path

from . import views

app_name = "editor"

urlpatterns = [
    path("subir-imagen/", views.subir_imagen, name="subir_imagen"),
]
