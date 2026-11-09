from django.urls import path

from . import views

app_name = "convocatorias"

urlpatterns = [
    path("", views.lista, name="lista"),
]
