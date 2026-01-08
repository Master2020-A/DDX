"""
Servicio de Traducción de Terminología Médica
"""

from typing import Dict, Any, Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
import json
import logging

from app.models.pln import TraduccionMedica, DiccionarioMedico
from app.services.openai_client import chat_completion

logger = logging.getLogger(__name__)


class TraduccionMedicaService:
    """Servicio para traducir terminología médica entre idiomas"""

    # Idiomas soportados
    IDIOMAS_SOPORTADOS = {
        "es": "Español",
        "en": "Inglés",
        "fr": "Francés",
        "pt": "Portugués",
        "de": "Alemán",
        "it": "Italiano",
        "la": "Latín",
    }

    async def traducir(
        self,
        texto: str,
        idioma_origen: str,
        idioma_destino: str,
        tipo_contenido: str = "texto_libre",
        especialidad: Optional[str] = None,
        medico_id: Optional[UUID] = None,
        db: AsyncSession = None,
    ) -> Dict[str, Any]:
        """
        Traducir texto médico

        Args:
            texto: Texto a traducir
            idioma_origen: Código de idioma origen (es, en, etc.)
            idioma_destino: Código de idioma destino
            tipo_contenido: Tipo (termino_medico, diagnostico, procedimiento, medicamento, texto_libre)
            especialidad: Especialidad médica (opcional)
            medico_id: ID del médico (opcional)
            db: Sesión de base de datos

        Returns:
            Dict con traducción y metadatos
        """

        # Validar idiomas
        if idioma_origen not in self.IDIOMAS_SOPORTADOS:
            raise ValueError(f"Idioma origen '{idioma_origen}' no soportado")
        if idioma_destino not in self.IDIOMAS_SOPORTADOS:
            raise ValueError(f"Idioma destino '{idioma_destino}' no soportado")

        # Buscar en diccionario primero
        if tipo_contenido == "termino_medico" and db:
            traduccion_diccionario = await self._buscar_en_diccionario(
                texto, idioma_origen, idioma_destino, db
            )
            if traduccion_diccionario:
                return traduccion_diccionario

        # Traducir con IA
        traduccion = await self._traducir_con_ia(
            texto, idioma_origen, idioma_destino, tipo_contenido, especialidad
        )

        # Guardar en base de datos
        if db:
            traduccion_db = TraduccionMedica(
                medico_id=medico_id,
                texto_original=texto,
                idioma_origen=idioma_origen,
                texto_traducido=traduccion["texto_traducido"],
                idioma_destino=idioma_destino,
                tipo_contenido=tipo_contenido,
                especialidad=especialidad,
                terminos_medicos_origen=traduccion.get("terminos_origen", []),
                terminos_medicos_destino=traduccion.get("terminos_destino", []),
                traducciones_alternativas=traduccion.get("alternativas", []),
                sinonimos=traduccion.get("sinonimos", {}),
                definicion=traduccion.get("definicion"),
                notas_clinicas=traduccion.get("notas_clinicas"),
                modelo_utilizado="gpt-4o",
                confianza=traduccion.get("confianza", 0.9),
            )

            db.add(traduccion_db)
            await db.commit()
            await db.refresh(traduccion_db)

            traduccion["id"] = str(traduccion_db.id)

        return traduccion

    async def _buscar_en_diccionario(
        self, termino: str, idioma_origen: str, idioma_destino: str, db: AsyncSession
    ) -> Optional[Dict[str, Any]]:
        """Buscar término en diccionario médico"""

        termino_lower = termino.lower().strip()

        # Construir query según idioma origen
        if idioma_origen == "es":
            query = select(DiccionarioMedico).where(
                DiccionarioMedico.termino_es.ilike(f"%{termino_lower}%")
            )
        elif idioma_origen == "en":
            query = select(DiccionarioMedico).where(
                DiccionarioMedico.termino_en.ilike(f"%{termino_lower}%")
            )
        else:
            return None

        result = await db.execute(query.limit(1))
        entrada = result.scalar_one_or_none()

        if not entrada:
            return None

        # Obtener traducción según idioma destino
        texto_traducido = None
        definicion = None

        if idioma_destino == "es":
            texto_traducido = entrada.termino_es
            definicion = entrada.definicion_es
        elif idioma_destino == "en":
            texto_traducido = entrada.termino_en
            definicion = entrada.definicion_en
        elif idioma_destino == "la":
            texto_traducido = entrada.termino_la

        if not texto_traducido:
            return None

        return {
            "texto_traducido": texto_traducido,
            "fuente": "diccionario",
            "definicion": definicion,
            "codigo_cie10": entrada.codigo_cie10,
            "codigo_snomed": entrada.codigo_snomed,
            "categoria": entrada.categoria,
            "especialidad": entrada.especialidad,
            "confianza": 1.0,
        }

    async def _traducir_con_ia(
        self,
        texto: str,
        idioma_origen: str,
        idioma_destino: str,
        tipo_contenido: str,
        especialidad: Optional[str],
    ) -> Dict[str, Any]:
        """Traducir usando IA"""

        nombre_idioma_origen = self.IDIOMAS_SOPORTADOS[idioma_origen]
        nombre_idioma_destino = self.IDIOMAS_SOPORTADOS[idioma_destino]

        contexto_especialidad = (
            f"\nESPECIALIDAD: {especialidad}" if especialidad else ""
        )

        prompt = f"""Traduce el siguiente texto médico de {nombre_idioma_origen} a {nombre_idioma_destino}:

TIPO DE CONTENIDO: {tipo_contenido}{contexto_especialidad}

TEXTO ORIGINAL ({idioma_origen.upper()}):
{texto}

Proporciona:
1. **TRADUCCIÓN PRINCIPAL**: Traducción precisa y contextualizada
2. **TÉRMINOS MÉDICOS**: Identifica términos médicos en ambos idiomas
3. **TRADUCCIONES ALTERNATIVAS**: Otras formas válidas de traducir
4. **SINÓNIMOS**: Sinónimos en el idioma destino
5. **DEFINICIÓN**: Definición médica del término (si aplica)
6. **NOTAS CLÍNICAS**: Notas sobre el uso clínico apropiado

IMPORTANTE: 
- Mantén la precisión médica
- Usa terminología estándar
- Considera el contexto clínico
- Responde SOLO con JSON válido

Formato JSON:
{{
    "texto_traducido": "...",
    "terminos_origen": ["término1", "término2"],
    "terminos_destino": ["term1", "term2"],
    "alternativas": ["alternativa1", "alternativa2"],
    "sinonimos": {{
        "termino1": ["sinonimo1", "sinonimo2"]
    }},
    "definicion": "Definición médica...",
    "notas_clinicas": "Notas sobre uso clínico...",
    "confianza": 0.95
}}"""

        try:
            response = await chat_completion(
                messages=[
                    {
                        "role": "system",
                        "content": f"""Eres un traductor médico experto especializado en terminología clínica.
Traduces de {nombre_idioma_origen} a {nombre_idioma_destino} con precisión médica.
Conoces nomenclatura internacional (ICD-10, SNOMED CT).
Mantienes consistencia terminológica.
IMPORTANTE: Responde SOLO con JSON válido.""",
                    },
                    {"role": "user", "content": prompt},
                ],
                model="gpt-4o",
                temperature=0.2,
                response_format={"type": "json_object"},
            )

            raw_content = response.choices[0].message.content

            try:
                resultado = json.loads(raw_content)
                return resultado
            except json.JSONDecodeError:
                logger.error(f"Error parseando JSON: {raw_content[:500]}")
                return {
                    "texto_traducido": f"[Error de traducción: {texto}]",
                    "terminos_origen": [],
                    "terminos_destino": [],
                    "alternativas": [],
                    "sinonimos": {},
                    "confianza": 0.0,
                }

        except Exception as e:
            logger.error(f"Error en traducción: {str(e)}")
            return {
                "texto_traducido": f"[Error: {texto}]",
                "terminos_origen": [],
                "terminos_destino": [],
                "alternativas": [],
                "sinonimos": {},
                "confianza": 0.0,
            }

    async def traducir_documento(
        self,
        texto: str,
        idioma_origen: str,
        idioma_destino: str,
        db: AsyncSession = None,
    ) -> Dict[str, Any]:
        """
        Traducir documento médico completo manteniendo formato

        Returns:
            Dict con documento traducido
        """

        prompt = f"""Traduce el siguiente documento médico completo de {self.IDIOMAS_SOPORTADOS[idioma_origen]} a {self.IDIOMAS_SOPORTADOS[idioma_destino]}:

DOCUMENTO ORIGINAL:
{texto}

Instrucciones:
- Traduce TODO el contenido
- Mantén el formato y estructura
- Usa terminología médica estándar
- Preserva números, fechas y valores
- Mantén abreviaturas médicas reconocidas internacionalmente

IMPORTANTE: Responde SOLO con JSON válido.

Formato JSON:
{{
    "documento_traducido": "Texto completo traducido...",
    "terminos_clave": ["término1", "término2"],
    "notas_traduccion": ["nota1", "nota2"]
}}"""

        try:
            response = await chat_completion(
                messages=[
                    {
                        "role": "system",
                        "content": "Eres un traductor médico experto. Traduces documentos completos manteniendo precisión y formato. Responde SOLO con JSON válido.",
                    },
                    {"role": "user", "content": prompt},
                ],
                model="gpt-4o",
                temperature=0.2,
                response_format={"type": "json_object"},
            )

            return json.loads(response.choices[0].message.content)

        except Exception as e:
            logger.error(f"Error traduciendo documento: {str(e)}")
            return {
                "documento_traducido": texto,
                "terminos_clave": [],
                "notas_traduccion": ["Error en traducción automática"],
            }

    async def agregar_termino_diccionario(
        self,
        termino_es: str,
        termino_en: str,
        categoria: str,
        definicion_es: Optional[str] = None,
        definicion_en: Optional[str] = None,
        termino_la: Optional[str] = None,
        especialidad: Optional[str] = None,
        codigo_cie10: Optional[str] = None,
        codigo_snomed: Optional[str] = None,
        db: AsyncSession = None,
    ) -> Dict[str, Any]:
        """Agregar término al diccionario médico"""

        if not db:
            raise ValueError("Se requiere sesión de base de datos")

        termino_db = DiccionarioMedico(
            termino_es=termino_es,
            termino_en=termino_en,
            termino_la=termino_la,
            categoria=categoria,
            especialidad=especialidad,
            definicion_es=definicion_es,
            definicion_en=definicion_en,
            codigo_cie10=codigo_cie10,
            codigo_snomed=codigo_snomed,
            verificado=False,
        )

        db.add(termino_db)
        await db.commit()
        await db.refresh(termino_db)

        return {
            "id": str(termino_db.id),
            "termino_es": termino_es,
            "termino_en": termino_en,
            "categoria": categoria,
            "mensaje": "Término agregado al diccionario",
        }

    async def buscar_terminos_diccionario(
        self,
        busqueda: str,
        idioma: str = "es",
        categoria: Optional[str] = None,
        db: AsyncSession = None,
        limite: int = 10,
    ) -> List[Dict[str, Any]]:
        """Buscar términos en el diccionario"""

        if not db:
            return []

        busqueda_lower = busqueda.lower()

        # Construir query
        if idioma == "es":
            query = select(DiccionarioMedico).where(
                or_(
                    DiccionarioMedico.termino_es.ilike(f"%{busqueda_lower}%"),
                    DiccionarioMedico.definicion_es.ilike(f"%{busqueda_lower}%"),
                )
            )
        elif idioma == "en":
            query = select(DiccionarioMedico).where(
                or_(
                    DiccionarioMedico.termino_en.ilike(f"%{busqueda_lower}%"),
                    DiccionarioMedico.definicion_en.ilike(f"%{busqueda_lower}%"),
                )
            )
        else:
            return []

        if categoria:
            query = query.where(DiccionarioMedico.categoria == categoria)

        query = query.limit(limite)

        result = await db.execute(query)
        terminos = result.scalars().all()

        return [
            {
                "id": str(t.id),
                "termino_es": t.termino_es,
                "termino_en": t.termino_en,
                "termino_la": t.termino_la,
                "categoria": t.categoria,
                "especialidad": t.especialidad,
                "definicion_es": t.definicion_es,
                "definicion_en": t.definicion_en,
                "codigo_cie10": t.codigo_cie10,
                "codigo_snomed": t.codigo_snomed,
            }
            for t in terminos
        ]
