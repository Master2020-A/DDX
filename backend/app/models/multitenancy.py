"""
Compatibilidad: este módulo NO debe declarar tablas duplicadas.

Re-exporta modelos canónicos para evitar:
InvalidRequestError: Table 'X' is already defined for this MetaData instance.
"""

from __future__ import annotations

import inspect
from typing import Any, Type

from app.models import institucion as _institucion_mod
from app.models import metricas_uso as _metricas_mod


def _find_model_by_tablename(mod: Any, tablename: str) -> Type[Any]:
    for _, obj in vars(mod).items():
        if inspect.isclass(obj) and getattr(obj, "__tablename__", None) == tablename:
            return obj
    raise ImportError(f"No se encontró en {mod.__name__} __tablename__='{tablename}'")


Institucion = _find_model_by_tablename(_institucion_mod, "instituciones")
ConfiguracionModulos = _find_model_by_tablename(
    _institucion_mod, "configuraciones_modulos"
)
FacturaInstitucion = _find_model_by_tablename(
    _institucion_mod, "facturas_instituciones"
)
MetricaUso = _find_model_by_tablename(_metricas_mod, "metricas_uso")

ConfiguracionesModulos = ConfiguracionModulos
FacturasInstituciones = FacturaInstitucion
MetricasUso = MetricaUso

__all__ = [
    "Institucion",
    "ConfiguracionModulos",
    "ConfiguracionesModulos",
    "FacturaInstitucion",
    "FacturasInstituciones",
    "MetricaUso",
    "MetricasUso",
]
