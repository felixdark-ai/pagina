from django.urls import path

from . import views

app_name = "institucional"

urlpatterns = [
    path("", views.deau, name="deau"),
    path("equipo/", views.equipo, name="equipo"),
]
