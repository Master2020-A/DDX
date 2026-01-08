from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Literal, Any, Dict, Optional, Tuple
import httpx
import os

router = APIRouter(prefix="/cp", tags=["Catálogos CP (Legacy)"])


class CodigoPostalResponse(BaseModel):
    codigo_postal: str = Field(..., min_length=5, max_length=5)
    pais: str = "México"
    estado: str
    municipio: str
    ciudad: str
    colonia: str
    colonias: List[str]
    fuente: Literal["dipomex"]


def _digits5(cp: str) -> str:
    return "".join(ch for ch in (cp or "") if ch.isdigit())[:5]


def _clean(v: Any) -> str:
    return str(v).strip() if v is not None else ""


def _titleish(v: Any) -> str:
    # Si quieres conservar MAYÚSCULAS como vienen, cambia por: return _clean(v)
    s = _clean(v)
    return s.title() if s else ""


def _parse_dipomex(data: Any, cp_fallback: str) -> Optional[CodigoPostalResponse]:
    # Espera el formato que compartiste
    if not isinstance(data, dict):
        return None

    # Si DIPOMEX reporta error, no parseamos
    if data.get("error") is not False:
        return None

    cp_node = data.get("codigo_postal")
    if not isinstance(cp_node, dict):
        return None

    cp = _digits5(_clean(cp_node.get("codigo_postal")) or cp_fallback)
    estado = _titleish(cp_node.get("estado"))
    municipio = _titleish(cp_node.get("municipio"))
    ciudad = _titleish(cp_node.get("ciudad")) or municipio

    colonias_node = cp_node.get("colonias") or []
    colonias: List[str] = []
    if isinstance(colonias_node, list):
        for item in colonias_node:
            if isinstance(item, dict):
                c = _clean(item.get("colonia"))
                if c:
                    colonias.append(c)
            else:
                c = _clean(item)
                if c:
                    colonias.append(c)

    colonia = colonias[0] if colonias else ""

    if not (cp and estado and municipio):
        return None

    return CodigoPostalResponse(
        codigo_postal=cp,
        pais="México",
        estado=estado,
        municipio=municipio,
        ciudad=ciudad,
        colonia=colonia,
        colonias=colonias,
        fuente="dipomex",
    )


async def _get_json(
    client: httpx.AsyncClient, url: str, params: Dict[str, Any], headers: Dict[str, str]
) -> Tuple[int, Any, str]:
    r = await client.get(url, params=params, headers=headers)
    raw = r.text
    try:
        data = r.json()
    except Exception:
        data = None
    return r.status_code, data, raw


async def _fetch_dipomex_tau(cp: str) -> CodigoPostalResponse:
    endpoint = (
        os.getenv("DIPOMEX_ENDPOINT", "https://api.tau.com.mx/dipomex/v1/codigo_postal")
        .strip()
        .rstrip("/")
    )  # sin slash final

    from app.core.settings import settings

    apikey = settings.DIPOMEX_APIKEY
    endpoint = settings.DIPOMEX_ENDPOINT.rstrip("/")
    print("DIPOMEX_APIKEY present?", bool(apikey), "len=", len(apikey))
    if not apikey:
        raise HTTPException(
            status_code=500, detail="Falta configurar DIPOMEX_APIKEY en el backend"
        )

    headers: Dict[str, str] = {
        "Accept": "application/json",
        "User-Agent": "mi-sistema/1.0 (FastAPI)",
        # Enviamos el APIKEY en varias cabeceras comunes
        "APIKEY": apikey,
        "X-API-KEY": apikey,
        "x-api-key": apikey,
        "apikey": apikey,
        # Algunas APIs usan Authorization
        "Authorization": f"ApiKey {apikey}",
    }

    # TAU confirmó que funciona por query param "codigo_postal"
    params = {"codigo_postal": cp}

    timeout = httpx.Timeout(12.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        status, data, raw = await _get_json(
            client, endpoint, params=params, headers=headers
        )

        # Si DIPOMEX contesta con JSON de error, lo propagamos claro
        if isinstance(data, dict) and data.get("error") is True:
            msg = data.get("message") or "Error en DIPOMEX"
            raise HTTPException(status_code=502, detail=f"DIPOMEX: {msg}")

        if status != 200:
            snippet = (raw or "")[:300].replace("\n", " ").replace("\r", " ")
            raise HTTPException(
                status_code=502, detail=f"DIPOMEX HTTP {status}: {snippet}"
            )

        parsed = _parse_dipomex(data, cp)
        if not parsed:
            raise HTTPException(
                status_code=502,
                detail="Respuesta DIPOMEX no coincide con el formato esperado",
            )

        return parsed


@router.get("/{cp}", response_model=CodigoPostalResponse)
async def obtener_info_cp(cp: str):
    cp = _digits5(cp)
    if len(cp) != 5:
        raise HTTPException(
            status_code=400, detail="CP inválido (debe tener 5 dígitos)"
        )

    return await _fetch_dipomex_tau(cp)
