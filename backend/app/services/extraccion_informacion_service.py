"""
Servicio de Extracción de Información de Notas Médicas
"""

from typing import Dict, Any, Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
import json
import logging

from app.models.pln import ExtraccionInformacion
from app.services.openai_client import chat_completion

logger = logging.getLogger(__name__)


class ExtraccionInformacionService:
    """Servicio para extraer información estructurada de notas médicas"""

    async def extraer_informacion(
        self,
        texto: str,
        tipo_documento: str,
        paciente_id: Optional[UUID],
        medico_id: UUID,
        consulta_id: Optional[UUID] = None,
        transcripcion_id: Optional[UUID] = None,
        db: AsyncSession = None,
    ) -> Dict[str, Any]:
        """
        Extraer información estructurada de texto médico

        Args:
            texto: Texto a analizar
            tipo_documento: Tipo de documento (nota_evolucion, historia_clinica, etc.)
            paciente_id: ID del paciente
            medico_id: ID del médico
            consulta_id: ID de la consulta (opcional)
            transcripcion_id: ID de transcripción (opcional)
            db: Sesión de base de datos

        Returns:
            Dict con información extraída
        """

        # Extraer con IA
        informacion = await self._extraer_con_ia(texto, tipo_documento)

        # Guardar en base de datos si se proporciona sesión
        if db:
            extraccion_db = ExtraccionInformacion(
                paciente_id=paciente_id,
                medico_id=medico_id,
                consulta_id=consulta_id,
                transcripcion_id=transcripcion_id,
                texto_original=texto,
                tipo_documento=tipo_documento,
                sintomas=informacion.get("sintomas", []),
                diagnosticos=informacion.get("diagnosticos", []),
                medicamentos=informacion.get("medicamentos", []),
                procedimientos=informacion.get("procedimientos", []),
                signos_vitales=informacion.get("signos_vitales", {}),
                antecedentes=informacion.get("antecedentes", []),
                alergias=informacion.get("alergias", []),
                entidades_medicas=informacion.get("entidades_medicas", []),
                modelo_utilizado=informacion.get("modelo", "gpt-4o"),
                confianza_promedio=informacion.get("confianza", 0.85),
            )

            db.add(extraccion_db)
            await db.commit()
            await db.refresh(extraccion_db)

            informacion["id"] = str(extraccion_db.id)

        return informacion

    async def _extraer_con_ia(self, texto: str, tipo_documento: str) -> Dict[str, Any]:
        """Extraer información usando IA"""

        prompt = f"""Analiza el siguiente texto médico y extrae información estructurada:

TIPO DE DOCUMENTO: {tipo_documento}

TEXTO:
{texto}

Extrae y estructura la siguiente información:

1. **SÍNTOMAS**: Lista de síntomas mencionados con:
   - Nombre del síntoma
   - Intensidad (leve/moderada/severa)
   - Duración
   - Características adicionales

2. **DIAGNÓSTICOS**: Diagnósticos mencionados con:
   - Nombre del diagnóstico
   - Código CIE-10 (si es identificable)
   - Tipo (presuntivo/confirmado/diferencial)

3. **MEDICAMENTOS**: Medicamentos con:
   - Nombre genérico
   - Nombre comercial (si se menciona)
   - Dosis
   - Frecuencia
   - Vía de administración
   - Duración del tratamiento

4. **PROCEDIMIENTOS**: Procedimientos realizados o sugeridos

5. **SIGNOS VITALES**: Si se mencionan:
   - Presión arterial
   - Frecuencia cardíaca
   - Temperatura
   - Frecuencia respiratoria
   - Saturación de oxígeno
   - Peso, talla, IMC

6. **ANTECEDENTES**: Antecedentes médicos mencionados

7. **ALERGIAS**: Alergias identificadas

8. **ENTIDADES MÉDICAS**: Todas las entidades médicas relevantes (órganos, sistemas, enfermedades, etc.)

IMPORTANTE: Responde SOLO con JSON válido.

Formato JSON:
{{
    "sintomas": [
        {{
            "nombre": "...",
            "intensidad": "leve/moderada/severa",
            "duracion": "...",
            "caracteristicas": "..."
        }}
    ],
    "diagnosticos": [
        {{
            "nombre": "...",
            "codigo_cie10": "...",
            "tipo": "presuntivo/confirmado/diferencial"
        }}
    ],
    "medicamentos": [
        {{
            "nombre_generico": "...",
            "nombre_comercial": "...",
            "dosis": "...",
            "frecuencia": "...",
            "via": "...",
            "duracion": "..."
        }}
    ],
    "procedimientos": ["..."],
    "signos_vitales": {{
        "presion_arterial": "...",
        "frecuencia_cardiaca": "...",
        "temperatura": "...",
        "frecuencia_respiratoria": "...",
        "saturacion_oxigeno": "...",
        "peso": "...",
        "talla": "...",
        "imc": "..."
    }},
    "antecedentes": ["..."],
    "alergias": ["..."],
    "entidades_medicas": ["..."]
}}"""

        try:
            response = await chat_completion(
                messages=[
                    {
                        "role": "system",
                        "content": """Eres un experto en procesamiento de lenguaje natural médico.
Tu tarea es extraer información estructurada de textos médicos con alta precisión.
Identifica entidades médicas, relaciones y contexto clínico.
IMPORTANTE: Responde SOLO con JSON válido, sin texto adicional.""",
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
                resultado["modelo"] = "gpt-4o"
                resultado["confianza"] = 0.85
                return resultado
            except json.JSONDecodeError:
                logger.error(f"Error parseando JSON: {raw_content[:500]}")
                return self._estructura_vacia()

        except Exception as e:
            logger.error(f"Error en extracción: {str(e)}")
            return self._estructura_vacia()

    def _estructura_vacia(self) -> Dict[str, Any]:
        """Estructura vacía de fallback"""
        return {
            "sintomas": [],
            "diagnosticos": [],
            "medicamentos": [],
            "procedimientos": [],
            "signos_vitales": {},
            "antecedentes": [],
            "alergias": [],
            "entidades_medicas": [],
            "modelo": "fallback",
            "confianza": 0.0,
        }

    async def extraer_entidades_nombradas(self, texto: str) -> Dict[str, List[str]]:
        """
        Extraer solo entidades nombradas médicas del texto

        Returns:
            Dict con categorías de entidades
        """

        prompt = f"""Identifica y clasifica todas las entidades médicas en el siguiente texto:

TEXTO:
{texto}

Clasifica las entidades en estas categorías:
- anatomia: Órganos, sistemas, partes del cuerpo
- patologia: Enfermedades, condiciones, síndromes
- farmacologia: Medicamentos, principios activos
- procedimientos: Procedimientos médicos, cirugías, estudios
- sintomas: Síntomas y signos clínicos
- valores: Valores numéricos con unidades (presión, temperatura, etc.)

Formato JSON:
{{
    "anatomia": ["..."],
    "patologia": ["..."],
    "farmacologia": ["..."],
    "procedimientos": ["..."],
    "sintomas": ["..."],
    "valores": ["..."]
}}"""

        try:
            response = await chat_completion(
                messages=[
                    {
                        "role": "system",
                        "content": "Eres un experto en reconocimiento de entidades médicas. Responde SOLO con JSON válido.",
                    },
                    {"role": "user", "content": prompt},
                ],
                model="gpt-4o",
                temperature=0.1,
                response_format={"type": "json_object"},
            )

            return json.loads(response.choices[0].message.content)

        except Exception as e:
            logger.error(f"Error extrayendo entidades: {str(e)}")
            return {
                "anatomia": [],
                "patologia": [],
                "farmacologia": [],
                "procedimientos": [],
                "sintomas": [],
                "valores": [],
            }
