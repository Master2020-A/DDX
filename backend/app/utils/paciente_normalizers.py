from typing import Optional, Union
from app.schemas.paciente import TelefonoMX, DireccionMX


def normalizar_telefono(v: Optional[Union[str, TelefonoMX]]) -> Optional[str]:
    """
    Devuelve string normalizado.
    Recomendación: guardar en formato E.164: +52XXXXXXXXXX
    """
    if v is None:
        return None

    if isinstance(v, TelefonoMX):
        return v.e164()

    if isinstance(v, str):
        s = v.strip()
        return s or None

    # Si por alguna razón llega dict (dependiendo de dónde lo llames)
    try:
        t = TelefonoMX(**v)  # type: ignore
        return t.e164()
    except Exception:
        return str(v)


def normalizar_direccion(v: Optional[Union[str, DireccionMX]]) -> Optional[str]:
    """
    Devuelve un string consistente para dirección.
    """
    if v is None:
        return None

    if isinstance(v, str):
        s = v.strip()
        return s or None

    if not isinstance(v, DireccionMX):
        try:
            v = DireccionMX(**v)  # type: ignore
        except Exception:
            return str(v)

    partes = [
        v.calle,
        f"No. {v.numero_exterior}" if v.numero_exterior else None,
        f"Int. {v.numero_interior}" if v.numero_interior else None,
        v.colonia,
        v.ciudad or v.municipio,
        v.municipio,
        v.estado,
        f"CP {v.codigo_postal}",
        v.pais,
    ]
    return ", ".join([p for p in partes if p])
