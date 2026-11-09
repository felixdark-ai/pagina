"""Validadores de archivos subidos desde el panel."""
from pathlib import Path

from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible

_OLE = b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"   # .doc .xls .ppt (formato binario antiguo de Office)
_ZIP = b"PK\x03\x04"                         # .docx .xlsx .pptx .odt .ods .odp (paquetes ZIP)

# extensión -> firma que debe tener el contenido real del archivo
FIRMAS = {
    "pdf": None,                              # se revisa aparte (cabecera %PDF-)
    "doc": _OLE, "xls": _OLE, "ppt": _OLE,
    "docx": _ZIP, "xlsx": _ZIP, "pptx": _ZIP,
    "odt": _ZIP, "ods": _ZIP, "odp": _ZIP,
    "csv": None,                              # texto: se revisa que no sea binario
}
EXTENSIONES_DOCUMENTO = sorted(FIRMAS)
FORMATOS_TEXTO = "PDF, Word, Excel, PowerPoint, OpenDocument (ODT/ODS/ODP) y CSV"


@deconstructible
class ValidarDocumento:
    """
    Acepta solo documentos de oficina. Comprueba la extensión Y que el contenido
    corresponda a ella, para que no se pueda subir un ejecutable o una página web
    simplemente renombrándolo a «.pdf».
    """

    def __call__(self, archivo):
        nombre = getattr(archivo, "name", "") or ""
        ext = Path(nombre).suffix.lower().lstrip(".")
        if ext not in FIRMAS:
            raise ValidationError(
                "Tipo de archivo no permitido (.%(ext)s). Formatos aceptados: %(formatos)s.",
                code="extension_no_permitida",
                params={"ext": ext or "sin extensión", "formatos": FORMATOS_TEXTO},
            )
        try:
            archivo.seek(0)
            cabecera = archivo.read(1024)
            archivo.seek(0)
        except (OSError, ValueError):
            return  # archivo ya guardado que no se puede releer: no se vuelve a validar
        if ext == "pdf":
            valido = b"%PDF-" in cabecera
        elif ext == "csv":
            valido = b"\x00" not in cabecera
        else:
            valido = cabecera.startswith(FIRMAS[ext])
        if not valido:
            raise ValidationError(
                "El contenido del archivo no corresponde a su extensión (.%(ext)s). "
                "Verifique que sea un documento válido.",
                code="contenido_invalido",
                params={"ext": ext},
            )

    def __eq__(self, otro):
        return isinstance(otro, ValidarDocumento)


validar_documento = ValidarDocumento()
