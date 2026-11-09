from django.urls import path

from . import views

app_name = "acreditacion"

urlpatterns = [
    path("<slug:slug>/", views.detalle, name="detalle"),
]
