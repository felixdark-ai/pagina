from django.db import models

from apps.core.models import SingletonModel


class SobreDEAU(SingletonModel):
    definicion = models.TextField(
        default=(
            "La Dirección de Evaluación y Acreditación Universitaria (DEAU) es un "
            "organismo que depende de Rectorado."
        )
    )
    funcion_basica = models.TextField(
        default=(
            "Planificar, asesorar, coordinar y controlar los procesos de Autoevaluación, "
            "Acreditación y Renovación de Acreditación de las Unidades Académicas. "
            "Asimismo, evaluar el grado de eficacia y eficiencia en el alcance de los "
            "objetivos del POA y realizar los seguimientos al Desempeño Docente para "
            "alcanzar la gestión de calidad en función al Plan Estratégico Institucional, "
            "los Planes Operativos Anuales y el Estatuto de la Universidad."
        )
    )
    mision = models.TextField(
        default=(
            "Coordinar y asesorar los procesos de Autoevaluación de las unidades "
            "académicas hacia la Acreditación Universitaria ante el CEUB e instancias "
            "internacionales (ARCU-SUR, MERCOSUR), para lograr la calidad y excelencia "
            "académica en la Gestión Universitaria."
        )
    )
    vision = models.TextField(
        default=(
            "Lograr el desarrollo de la excelencia y la pertinencia de las actividades "
            "académico-administrativas de la institución, gestionando la calidad en "
            "función del Plan Estratégico Institucional y promoviendo el desarrollo de "
            "una cultura de evaluación y acreditación, precautelando las ventajas "
            "competitivas del desempeño institucional."
        )
    )
    estructura_organica = models.TextField(
        default="1 Director\n2 Técnicos\n1 Asistente Administrativo",
        help_text="Un cargo por línea.",
    )
    foto_equipo = models.ImageField(upload_to="deau/", blank=True, null=True)

    def __str__(self):
        return "Sobre la DEAU"

    class Meta:
        verbose_name = "Sobre la DEAU"
        verbose_name_plural = "Sobre la DEAU"


class MiembroEquipo(models.Model):
    CARGOS = [
        ("director", "Director/a"),
        ("tecnico", "Técnico/a"),
        ("administrativo", "Asistente Administrativo/a"),
    ]

    nombre = models.CharField(max_length=150)
    cargo = models.CharField(max_length=20, choices=CARGOS)
    foto = models.ImageField(upload_to="equipo/", blank=True, null=True)
    correo = models.EmailField(blank=True)
    telefono = models.CharField(max_length=30, blank=True)
    orden = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["orden", "nombre"]
        verbose_name = "Miembro del equipo"
        verbose_name_plural = "Equipo técnico"

    def __str__(self):
        return f"{self.nombre} ({self.get_cargo_display()})"


class ValorInstitucional(models.Model):
    titulo = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    icono = models.CharField(max_length=50, blank=True, help_text="Nombre de ícono lineal (ej. 'shield', 'check').")
    orden = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["orden"]

    def __str__(self):
        return self.titulo
