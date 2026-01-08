"""
Servicio para consultar códigos postales usando SEPOMEX API
"""

import httpx
from typing import Optional, Dict, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.catalogos import CodigoPostal


class CodigoPostalService:
    """Servicio para gestión de códigos postales"""

    # APIs alternativas de códigos postales (en orden de prioridad)
    # Estas son las APIs que usan los ecommerce
    CP_APIS = [
        # API 0: Zippopotam (sin autenticación, cobertura global)
        {
            "url": "https://api.zippopotam.us/MX/{cp}",
            "parser": "zippopotam",
        },
        # API 1: Copomex (requiere token, pero se intenta por si el proyecto lo provee)
        {
            "url": "https://api.copomex.com/query/info_cp/{cp}?type=simplified",
            "parser": "copomex",
        },
        # API 2: SEPOMEX original
        {
            "url": "https://api-sepomex.hckdrk.mx/query/info_cp/{cp}",
            "parser": "sepomex",
        },
        # API 3: Codigo Postal Mexico
        {
            "url": "https://api-codigos-postales.onrender.com/api/cp/{cp}",
            "parser": "cp_mexico",
        },
    ]

    def __init__(self, db: AsyncSession):
        self.db = db

    async def buscar_por_cp(self, codigo_postal: str) -> Optional[Dict]:
        """
        Buscar información de código postal
        Consulta directamente API externa (tabla BD no existe)
        """
        # Limpiar código postal
        cp_limpio = codigo_postal.strip().replace(" ", "")

        # Consultar API externa directamente
        try:
            datos_api = await self._consultar_api_sepomex(cp_limpio)

            if datos_api:
                return datos_api

        except Exception as e:
            print(f"Error consultando API SEPOMEX: {e}")

        return None

    async def _consultar_api_sepomex(self, codigo_postal: str) -> Optional[Dict]:
        """Consultar API externa de SEPOMEX - intenta múltiples APIs"""

        # Intentar con cada API en orden
        for api_config in self.CP_APIS:
            try:
                url = api_config["url"].format(cp=codigo_postal)
                parser = api_config["parser"]
                print(f"📡 Consultando API ({parser}): {url}")

                async with httpx.AsyncClient(
                    timeout=5.0
                ) as client:  # Timeout más corto
                    response = await client.get(url)

                    print(f"   Status: {response.status_code}")

                    if response.status_code == 200:
                        data = response.json()

                        # Parsear según el tipo de API
                        resultado = None
                        if parser == "copomex":
                            resultado = self._parse_copomex(data, codigo_postal)
                        elif parser == "sepomex":
                            resultado = self._parse_sepomex(data, codigo_postal)
                        elif parser == "cp_mexico":
                            resultado = self._parse_cp_mexico(data, codigo_postal)
                        elif parser == "zippopotam":
                            resultado = self._parse_zippopotam(data, codigo_postal)

                        if resultado:
                            resultado = await self._enrich_with_nominatim(
                                codigo_postal, resultado
                            )
                            print(
                                f"   ✅ Datos encontrados: {resultado.get('estado')}, {resultado.get('municipio')}"
                            )
                            return resultado
                        else:
                            print(f"   ⚠️  API respondió 200 pero sin datos")
                    elif response.status_code == 404:
                        print(f"   ❌ Código postal no encontrado en esta API")
                        continue  # Probar siguiente API
                    else:
                        print(f"   ❌ Error HTTP {response.status_code}")
                        continue

            except httpx.TimeoutException:
                print(f"   ⏱️  Timeout en {api_config['parser']}")
                continue
            except httpx.ConnectError as e:
                print(f"   🔌 Error de conexión en {api_config['parser']}: {str(e)}")
                continue
            except Exception as e:
                print(
                    f"   ❌ Error inesperado en {api_config['parser']}: {type(e).__name__}: {str(e)}"
                )
                continue

        print(f"❌ Todas las APIs fallaron para CP: {codigo_postal}")
        return None

    def _parse_copomex(self, data: Dict, codigo_postal: str) -> Optional[Dict]:
        """Parsear respuesta de API Copomex"""
        try:
            if not data or "error" in data:
                return None

            # Copomex puede retornar array o objeto
            if isinstance(data, list) and len(data) > 0:
                primer_registro = data[0]
            elif isinstance(data, dict):
                primer_registro = data
            else:
                return None

            # Obtener colonias
            colonias = []
            if isinstance(data, list):
                colonias = [
                    item.get("response", {}).get("asentamiento", "")
                    or item.get("asentamiento", "")
                    for item in data
                    if "asentamiento" in item or "response" in item
                ]

            return {
                "codigo_postal": codigo_postal,
                "pais": "México",
                "estado": primer_registro.get("response", {}).get("estado", "")
                or primer_registro.get("estado", ""),
                "municipio": primer_registro.get("response", {}).get("municipio", "")
                or primer_registro.get("municipio", ""),
                "ciudad": primer_registro.get("response", {}).get("ciudad", "")
                or primer_registro.get("ciudad", "")
                or primer_registro.get("response", {}).get("municipio", "")
                or primer_registro.get("municipio", ""),
                "colonia": (
                    colonias[0]
                    if colonias
                    else primer_registro.get("response", {}).get("asentamiento", "")
                    or primer_registro.get("asentamiento", "")
                ),
                "colonias": colonias if colonias else [],
                "fuente": "api",
            }
        except Exception as e:
            print(f"Error parseando Copomex: {e}")
            return None

    def _parse_sepomex(self, data: List, codigo_postal: str) -> Optional[Dict]:
        """Parsear respuesta de API SEPOMEX"""
        try:
            if not data or not isinstance(data, list) or len(data) == 0:
                return None

            primer_registro = data[0]

            # Obtener todas las colonias
            colonias = [item.get("asentamiento", "") for item in data]

            return {
                "codigo_postal": codigo_postal,
                "pais": "México",
                "estado": primer_registro.get("estado", ""),
                "municipio": primer_registro.get("municipio", ""),
                "ciudad": primer_registro.get("ciudad", "")
                or primer_registro.get("municipio", ""),
                "colonia": colonias[0] if colonias else "",
                "colonias": colonias,
                "fuente": "api",
            }
        except Exception as e:
            print(f"Error parseando SEPOMEX: {e}")
            return None

    def _parse_cp_mexico(self, data: Dict, codigo_postal: str) -> Optional[Dict]:
        """Parsear respuesta de API Codigo Postal Mexico"""
        try:
            if not data or "error" in data:
                return None

            # Puede tener diferentes estructuras
            if "data" in data:
                info = data["data"]
            elif "codigo_postal" in data:
                info = data
            else:
                return None

            colonias = info.get("colonias", []) or info.get("asentamientos", [])

            return {
                "codigo_postal": codigo_postal,
                "pais": "México",
                "estado": info.get("estado", ""),
                "municipio": info.get("municipio", ""),
                "ciudad": info.get("ciudad", "") or info.get("municipio", ""),
                "colonia": colonias[0] if colonias else "",
                "colonias": colonias,
                "fuente": "api",
            }
        except Exception as e:
            print(f"Error parseando CP Mexico: {e}")
            return None

    def _parse_zippopotam(self, data: Dict, codigo_postal: str) -> Optional[Dict]:
        """Parsear respuesta de la API Zippopotam"""
        try:
            if not data or "places" not in data:
                return None

            places = data.get("places", [])
            if not places:
                return None

            colonias = [
                place.get("place name", "")
                for place in places
                if place.get("place name")
            ]
            primer_lugar = places[0]

            return {
                "codigo_postal": codigo_postal,
                "pais": data.get("country", "México"),
                "estado": primer_lugar.get("state", ""),
                "municipio": primer_lugar.get("place name", ""),
                "ciudad": primer_lugar.get("place name", ""),
                "colonia": colonias[0]
                if colonias
                else primer_lugar.get("place name", ""),
                "colonias": colonias,
                "fuente": "zippopotam",
            }
        except Exception as e:
            print(f"Error parseando Zippopotam: {e}")
            return None

    async def _enrich_with_nominatim(self, codigo_postal: str, datos: Dict) -> Dict:
        """Complementar información con Nominatim (ciudad/municipio)."""
        necesita_municipio = not datos.get("municipio") or (
            datos.get("colonia")
            and datos.get("municipio", "").strip().lower()
            == datos.get("colonia", "").strip().lower()
        )
        necesita_ciudad = not datos.get("ciudad") or (
            datos.get("colonia")
            and datos.get("ciudad", "").strip().lower()
            == datos.get("colonia", "").strip().lower()
        )

        if not (necesita_municipio or necesita_ciudad):
            return datos

        try:
            async with httpx.AsyncClient(
                timeout=6.0,
                headers={"User-Agent": "DDX-Medical/1.0 (codigo-postal)"},
            ) as client:
                response = await client.get(
                    "https://nominatim.openstreetmap.org/search",
                    params={
                        "postalcode": codigo_postal,
                        "country": "Mexico",
                        "format": "json",
                        "addressdetails": 1,
                    },
                )

                if response.status_code != 200:
                    return datos

                payload = response.json()
                if not payload:
                    return datos

                address = payload[0].get("address", {})
                municipio = (
                    address.get("city")
                    or address.get("town")
                    or address.get("county")
                    or datos.get("municipio")
                )
                ciudad = municipio or datos.get("ciudad")

                if municipio:
                    datos["municipio"] = municipio
                if ciudad:
                    datos.setdefault("ciudad", ciudad)

                return datos
        except Exception as e:
            print(f"   ⚠️  Nominatim fallback error: {e}")
            return datos

    async def _guardar_en_bd(self, datos: Dict) -> None:
        """Guardar código postal con TODAS sus colonias en BD local"""
        try:
            # Guardar solo si tiene datos válidos
            if datos.get("estado") and datos.get("municipio"):
                colonias = datos.get("colonias", [])

                # Si no hay colonias en el array, usar la colonia singular
                if not colonias and datos.get("colonia"):
                    colonias = [datos["colonia"]]

                # Guardar un registro por cada colonia
                for colonia in colonias:
                    # Verificar si ya existe este CP+colonia
                    result = await self.db.execute(
                        select(CodigoPostal).where(
                            CodigoPostal.codigo_postal == datos["codigo_postal"],
                            CodigoPostal.colonia == colonia,
                        )
                    )
                    existe = result.scalar_one_or_none()

                    if not existe:
                        nuevo_cp = CodigoPostal(
                            codigo_postal=datos["codigo_postal"],
                            pais=datos.get("pais", "México"),
                            estado=datos["estado"],
                            municipio=datos["municipio"],
                            ciudad=datos.get("ciudad") or datos["municipio"],
                            colonia=colonia,
                            activo=True,
                        )
                        self.db.add(nuevo_cp)
                        print(f"  💾 Guardando: {datos['codigo_postal']} - {colonia}")

                await self.db.commit()
                print(
                    f"✅ Guardadas {len(colonias)} colonias para CP {datos['codigo_postal']}"
                )
        except Exception as e:
            print(f"❌ Error guardando CP en BD: {e}")
            await self.db.rollback()

    async def buscar_por_estado(self, estado: str) -> List[Dict]:
        """Buscar códigos postales por estado"""
        result = await self.db.execute(
            select(CodigoPostal)
            .where(
                CodigoPostal.estado.ilike(f"%{estado}%"), CodigoPostal.activo == True
            )
            .limit(50)
        )
        codigos = result.scalars().all()

        return [
            {
                "codigo_postal": cp.codigo_postal,
                "estado": cp.estado,
                "municipio": cp.municipio,
                "ciudad": cp.ciudad,
                "colonia": cp.colonia,
            }
            for cp in codigos
        ]
