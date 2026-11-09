from django.urls import reverse

from apps.core.testing import BaseTest, imagen

from .models import HeroImagen, HeroInicio


class HeroTests(BaseTest):
    def test_sin_imagenes_no_hay_carrusel(self):
        r = self.client.get(reverse("inicio:inicio"))
        self.assertEqual(r.status_code, 200)
        self.assertNotContains(r, "data-hero-carrusel")

    def test_una_imagen_es_estatica(self):
        hero = HeroInicio.cargar()
        hero.imagen = imagen("a.png")
        hero.save()
        r = self.client.get(reverse("inicio:inicio"))
        self.assertContains(r, "hero__slide")
        self.assertNotContains(r, "data-hero-carrusel")
        self.assertNotContains(r, "data-hero-punto")

    def test_dos_o_mas_imagenes_forman_carrusel_de_5s(self):
        hero = HeroInicio.cargar()
        hero.imagen = imagen("a.png")
        hero.save()
        HeroImagen.objects.create(hero=hero, imagen=imagen("b.png"))
        HeroImagen.objects.create(hero=hero, imagen=imagen("c.png"))
        HeroImagen.objects.create(hero=hero, imagen=imagen("d.png"), activo=False)  # inactiva: no cuenta
        r = self.client.get(reverse("inicio:inicio"))
        self.assertContains(r, "data-hero-carrusel")
        self.assertContains(r, 'data-intervalo="5000"')
        self.assertContains(r, "data-hero-punto", count=3)

    def test_solo_imagenes_adicionales_tambien_cuentan(self):
        hero = HeroInicio.cargar()
        HeroImagen.objects.create(hero=hero, imagen=imagen("b.png"))
        HeroImagen.objects.create(hero=hero, imagen=imagen("c.png"))
        self.assertEqual(len(hero.slides()), 2)
