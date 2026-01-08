"""
Alias de compatibilidad.

Algunos servicios importan `app.models.imagenes.ImagenMedica`,
pero el modelo real vive en `app.models.imagen_medica`.
"""

from app.models.imagen_medica import ImagenMedica

__all__ = ["ImagenMedica"]
