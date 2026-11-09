from django.urls import path

from . import views

app_name = "procesos"

urlpatterns = [
    path("", views.lista, name="lista"),
    path("<slug:slug>/", views.detalle, name="detalle"),
    path("<slug:slug>/acceso/", views.acceso, name="acceso"),
    path("<slug:slug>/ir/", views.redirigir, name="redirigir"),
]
