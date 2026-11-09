from django.core.management.base import BaseCommand

from apps.contacto.models import InformacionContacto
from apps.documentos.models import CategoriaDocumento
from apps.inicio.models import HeroInicio, Indicador
from apps.institucional.models import SobreDEAU, ValorInstitucional
from apps.procesos.models import Proceso


class Command(BaseCommand):
    help = "Carga el contenido institucional inicial oficial de la DEAU."

    def handle(self, *args, **options):
        hero = HeroInicio.cargar()
        hero.titulo = "Dirección de Evaluación y Acreditación Universitaria"
        hero.subtitulo = (
            "Coordinamos los procesos de autoevaluación y acreditación para lograr "
            "la calidad y excelencia académica de nuestra universidad."
        )
        hero.save()

        sobre = SobreDEAU.cargar()
        sobre.save()  # ya trae los valores por defecto definidos en el modelo

        InformacionContacto.cargar()

        procesos_data = [
            {
                "titulo": "Autoevaluación",
                "descripcion_corta": "Diagnóstico interno de las unidades académicas frente a los estándares de calidad.",
                "icono": "🔍",
                "tipo": Proceso.TIPO_INTERNO,
                "objetivo": "Identificar fortalezas y debilidades de la unidad académica para diseñar un plan de mejora continua.",
                "etapas": "Sensibilización\nConformación del comité de autoevaluación\nRecolección y análisis de información\nInforme de autoevaluación\nPlan de mejoras",
                "orden": 1,
            },
            {
                "titulo": "Acreditación",
                "descripcion_corta": "Reconocimiento externo de la calidad académica ante el CEUB y organismos internacionales.",
                "icono": "🏅",
                "tipo": Proceso.TIPO_INTERNO,
                "objetivo": "Obtener el reconocimiento oficial de la calidad académica de la carrera o programa evaluado.",
                "etapas": "Solicitud de acreditación\nEvaluación externa (pares evaluadores)\nInforme de evaluación externa\nResolución de acreditación",
                "orden": 2,
            },
            {
                "titulo": "Renovación de Acreditación",
                "descripcion_corta": "Seguimiento y renovación del reconocimiento de calidad previamente obtenido.",
                "icono": "🔄",
                "tipo": Proceso.TIPO_INTERNO,
                "objetivo": "Garantizar la vigencia y sostenibilidad de la calidad académica certificada.",
                "etapas": "Autoevaluación de seguimiento\nInforme de cumplimiento del plan de mejoras\nEvaluación externa de renovación\nResolución de renovación",
                "orden": 3,
            },
            {
                "titulo": "Seguimiento al POA",
                "descripcion_corta": "Evaluación de la eficacia y eficiencia en el cumplimiento del Plan Operativo Anual.",
                "icono": "📈",
                "tipo": Proceso.TIPO_EXTERNO,
                "objetivo": "Realizar el seguimiento institucional al avance de los Planes Operativos Anuales de cada unidad.",
                "url_externa_nombre": "Seguimiento al POA",
                "orden": 4,
            },
            {
                "titulo": "Evaluación al Desempeño Docente",
                "descripcion_corta": "Seguimiento al desempeño docente en el marco de la gestión de calidad institucional.",
                "icono": "🎓",
                "tipo": Proceso.TIPO_EXTERNO,
                "objetivo": "Evaluar el desempeño docente como parte de la gestión de calidad institucional.",
                "url_externa_nombre": "Evaluación al Desempeño Docente",
                "orden": 5,
            },
        ]
        for datos in procesos_data:
            Proceso.objects.update_or_create(titulo=datos["titulo"], defaults=datos)

        categorias = ["Guías", "Formatos", "Normativa", "Calendario", "Informes"]
        for i, nombre in enumerate(categorias):
            CategoriaDocumento.objects.get_or_create(nombre=nombre, defaults={"orden": i})

        valores = [
            ("Transparencia", "Actuamos con claridad y apertura en cada proceso institucional."),
            ("Compromiso", "Trabajamos junto a las unidades académicas hacia la excelencia."),
            ("Mejora continua", "Promovemos una cultura permanente de evaluación y calidad."),
        ]
        for i, (titulo, descripcion) in enumerate(valores):
            ValorInstitucional.objects.get_or_create(titulo=titulo, defaults={"descripcion": descripcion, "orden": i})

        indicadores = [
            ("Unidades académicas acompañadas", "0"),
            ("Acreditaciones vigentes", "0"),
            ("Renovaciones en proceso", "0"),
        ]
        for i, (etiqueta, valor) in enumerate(indicadores):
            Indicador.objects.get_or_create(etiqueta=etiqueta, defaults={"valor": valor, "orden": i})

        self.stdout.write(self.style.SUCCESS("Contenido inicial de la DEAU cargado correctamente."))
