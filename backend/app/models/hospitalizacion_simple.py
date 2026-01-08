"""
Modelo "simple" de Hospitalización: re-usa la Table del modelo principal.
"""

from __future__ import annotations

from app.core.database import Base
from app.models.hospitalizacion import Hospitalizacion as _Hospitalizacion


class HospitalizacionSimple(Base):
    __table__ = _Hospitalizacion.__table__
