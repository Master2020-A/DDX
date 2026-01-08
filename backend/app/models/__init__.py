"""
app.models

- Importa modelos para registrar mappers y resolver relationship("NombreClase").
- Importa primero módulos clave (portal_paciente incluido) para evitar KeyError
  de relaciones por nombre (ej. "CitaPaciente").
- Tolera módulos legacy que redeclaran tablas.
"""

from __future__ import annotations

import logging
from importlib import import_module
from pkgutil import iter_modules

from sqlalchemy.exc import InvalidRequestError

logger = logging.getLogger(__name__)

SKIP_MODULES = {
    "hospitalizacion_simple",  # legacy que redeclara tablas
}

# 1) módulos clave: si fallan, queremos enterarnos (no los “silenciamos”)
KEY_MODULES = (
    "app.models.security",
    "app.models.institucion",
    "app.models.metricas_uso",
    "app.models.configuracion_portal",  # <-- ANTES de portal_paciente
    "app.models.portal_paciente",
    "app.models.usuario",
)

for _mod in KEY_MODULES:
    import_module(_mod)

# 2) resto de módulos: tolerantes
for m in iter_modules(__path__):
    if m.name.startswith("_") or m.name in SKIP_MODULES:
        if m.name in SKIP_MODULES:
            logger.warning("🟡 Saltando import de modelo '%s' por exclusión", m.name)
        continue

    try:
        import_module(f"{__name__}.{m.name}")
    except InvalidRequestError as e:
        msg = str(e)
        if "is already defined for this MetaData instance" in msg:
            logger.warning("🟡 Saltando '%s' por tabla duplicada: %s", m.name, msg)
            continue
        raise
