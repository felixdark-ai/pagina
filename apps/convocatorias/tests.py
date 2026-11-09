from datetime import date

from apps.core.testing import BaseTest


class ConvocatoriasTests(BaseTest):
    def test_convocatoria_sigue_guardandose_normalmente(self):
        from apps.convocatorias.models import Convocatoria

        c = Convocatoria.objects.create(
            titulo="Conv", descripcion="d", fecha_apertura=date(2026, 1, 1), fecha_cierre=date(2026, 2, 1), estado="abierta"
        )
        self.assertTrue(c.slug)
