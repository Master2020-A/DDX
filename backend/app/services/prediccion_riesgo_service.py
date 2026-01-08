"""
Servicio de Predicción de Riesgos Médicos
"""

from typing import Dict, Any, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from datetime import datetime, timedelta
import json
from app.models.paciente import Paciente
from app.models.laboratorio import PruebaLaboratorio
from app.models.expediente import ExpedienteClinico
from app.models.consulta import Consulta
from app.services.openai_client import chat_completion


class PrediccionRiesgoService:
    """Servicio para predicción de riesgos médicos"""

    def __init__(self):
        pass

    async def predecir_riesgo_cardiovascular(
        self, paciente_id: UUID, db: AsyncSession
    ) -> Dict[str, Any]:
        """
        Calcular riesgo cardiovascular usando algoritmo de Framingham
        y análisis con IA
        """
        # Obtener datos del paciente
        datos = await self._obtener_datos_paciente(paciente_id, db)

        # Calcular score de Framingham
        score_framingham = self._calcular_framingham(datos)

        # Análisis con IA para contexto adicional
        analisis_ia = await self._analizar_riesgo_con_ia(
            "cardiovascular", datos, score_framingham
        )

        return {
            "tipo_riesgo": "cardiovascular",
            "porcentaje_riesgo": score_framingham["riesgo_10_anos"],
            "nivel_riesgo": score_framingham["categoria"],
            "factores_riesgo": analisis_ia["factores_riesgo"],
            "factores_protectores": analisis_ia["factores_protectores"],
            "recomendaciones": analisis_ia["recomendaciones"],
            "estudios_sugeridos": analisis_ia["estudios_sugeridos"],
            "algoritmo": "Framingham + IA",
            "datos_utilizados": datos,
        }

    async def predecir_riesgo_diabetes(
        self, paciente_id: UUID, db: AsyncSession
    ) -> Dict[str, Any]:
        """Predecir riesgo de desarrollar diabetes tipo 2"""

        datos = await self._obtener_datos_paciente(paciente_id, db)

        # Calcular score de riesgo
        score = self._calcular_riesgo_diabetes(datos)

        # Análisis con IA
        analisis_ia = await self._analizar_riesgo_con_ia(
            "diabetes", datos, {"score": score}
        )

        return {
            "tipo_riesgo": "diabetes_tipo2",
            "porcentaje_riesgo": score["porcentaje"],
            "nivel_riesgo": score["categoria"],
            "factores_riesgo": analisis_ia["factores_riesgo"],
            "factores_protectores": analisis_ia["factores_protectores"],
            "recomendaciones": analisis_ia["recomendaciones"],
            "estudios_sugeridos": [
                "Glucosa en ayunas",
                "HbA1c",
                "Curva de tolerancia a la glucosa",
            ],
            "algoritmo": "ADA Risk Score + IA",
            "datos_utilizados": datos,
        }

    async def predecir_riesgo_general(
        self, paciente_id: UUID, tipo_riesgo: str, db: AsyncSession
    ) -> Dict[str, Any]:
        """Predicción de riesgo general usando IA"""

        datos = await self._obtener_datos_paciente(paciente_id, db)

        prompt = f"""Analiza el riesgo de {tipo_riesgo} para este paciente:

DATOS DEL PACIENTE:
{self._formatear_datos(datos)}

Proporciona un análisis estructurado con:
1. Nivel de riesgo (bajo/moderado/alto/muy_alto)
2. Porcentaje estimado de riesgo (0-100)
3. Factores de riesgo identificados
4. Factores protectores
5. Recomendaciones específicas
6. Estudios sugeridos para evaluación

Formato de respuesta en JSON:
{{
    "nivel_riesgo": "...",
    "porcentaje_riesgo": 0-100,
    "factores_riesgo": ["factor1", "factor2"],
    "factores_protectores": ["factor1", "factor2"],
    "recomendaciones": ["rec1", "rec2"],
    "estudios_sugeridos": ["estudio1", "estudio2"],
    "justificacion": "..."
}}"""

        response = await chat_completion(
            messages=[
                {
                    "role": "system",
                    "content": "Eres un médico experto en medicina preventiva y evaluación de riesgos.",
                },
                {"role": "user", "content": prompt},
            ],
            model="gpt-4o",
            temperature=0.3,
            response_format={"type": "json_object"},
        )

        analisis = json.loads(response.choices[0].message.content)

        return {
            "tipo_riesgo": tipo_riesgo,
            **analisis,
            "algoritmo": "IA (GPT-4)",
            "datos_utilizados": datos,
        }

    def _calcular_framingham(self, datos: Dict[str, Any]) -> Dict[str, Any]:
        """Calcular score de Framingham para riesgo cardiovascular"""

        edad = datos.get("edad", 50)
        sexo = datos.get("sexo", "M")
        colesterol_total = datos.get("colesterol_total", 200)
        hdl = datos.get("hdl", 50)
        presion_sistolica = datos.get("presion_sistolica", 120)
        fuma = datos.get("fuma", False)
        diabetes = datos.get("diabetes", False)

        # Simplificación del algoritmo de Framingham
        puntos = 0

        # Edad
        if sexo == "M":
            if edad >= 70:
                puntos += 11
            elif edad >= 60:
                puntos += 8
            elif edad >= 50:
                puntos += 5
            elif edad >= 40:
                puntos += 2
        else:
            if edad >= 70:
                puntos += 12
            elif edad >= 60:
                puntos += 9
            elif edad >= 50:
                puntos += 6
            elif edad >= 40:
                puntos += 3

        # Colesterol
        if colesterol_total >= 280:
            puntos += 3
        elif colesterol_total >= 240:
            puntos += 2
        elif colesterol_total >= 200:
            puntos += 1

        # HDL
        if hdl < 35:
            puntos += 2
        elif hdl < 45:
            puntos += 1
        elif hdl >= 60:
            puntos -= 1

        # Presión arterial
        if presion_sistolica >= 160:
            puntos += 2
        elif presion_sistolica >= 140:
            puntos += 1

        # Factores adicionales
        if fuma:
            puntos += 2
        if diabetes:
            puntos += 2

        # Convertir puntos a porcentaje de riesgo (simplificado)
        riesgo = min(max(puntos * 2, 1), 40)

        if riesgo < 10:
            categoria = "bajo"
        elif riesgo < 20:
            categoria = "moderado"
        elif riesgo < 30:
            categoria = "alto"
        else:
            categoria = "muy_alto"

        return {"puntos": puntos, "riesgo_10_anos": riesgo, "categoria": categoria}

    def _calcular_riesgo_diabetes(self, datos: Dict[str, Any]) -> Dict[str, Any]:
        """Calcular riesgo de diabetes tipo 2"""

        puntos = 0

        edad = datos.get("edad", 50)
        imc = datos.get("imc", 25)
        circunferencia_cintura = datos.get("circunferencia_cintura", 80)
        actividad_fisica = datos.get("actividad_fisica", "moderada")
        antecedentes_familiares = datos.get("antecedentes_familiares_diabetes", False)
        hipertension = datos.get("hipertension", False)
        glucosa_alterada = datos.get("glucosa_alterada_previa", False)

        # Edad
        if edad >= 65:
            puntos += 4
        elif edad >= 55:
            puntos += 3
        elif edad >= 45:
            puntos += 2

        # IMC
        if imc >= 35:
            puntos += 3
        elif imc >= 30:
            puntos += 2
        elif imc >= 25:
            puntos += 1

        # Circunferencia de cintura
        if circunferencia_cintura > 102:
            puntos += 3
        elif circunferencia_cintura > 94:
            puntos += 2

        # Actividad física
        if actividad_fisica == "sedentario":
            puntos += 2

        # Antecedentes familiares
        if antecedentes_familiares:
            puntos += 5

        # Hipertensión
        if hipertension:
            puntos += 2

        # Glucosa alterada previa
        if glucosa_alterada:
            puntos += 5

        # Convertir a porcentaje
        porcentaje = min(puntos * 3, 80)

        if porcentaje < 15:
            categoria = "bajo"
        elif porcentaje < 30:
            categoria = "moderado"
        elif porcentaje < 50:
            categoria = "alto"
        else:
            categoria = "muy_alto"

        return {"puntos": puntos, "porcentaje": porcentaje, "categoria": categoria}

    async def _obtener_datos_paciente(
        self, paciente_id: UUID, db: AsyncSession
    ) -> Dict[str, Any]:
        """Obtener datos relevantes del paciente para cálculo de riesgos"""

        # Datos básicos del paciente
        result = await db.execute(select(Paciente).where(Paciente.id == paciente_id))
        paciente = result.scalar_one_or_none()

        if not paciente:
            return {}

        datos = {
            "edad": paciente.edad if hasattr(paciente, "edad") else None,
            "sexo": paciente.genero if hasattr(paciente, "genero") else None,
            "alergias": paciente.alergias or [],
            "antecedentes": [],  # Se obtendrán de las consultas
        }

        # Último expediente con signos vitales
        result = await db.execute(
            select(ExpedienteClinico)
            .where(ExpedienteClinico.paciente_id == paciente_id)
            .order_by(desc(ExpedienteClinico.created_at))
            .limit(1)
        )
        ultimo_expediente = result.scalar_one_or_none()

        if ultimo_expediente and ultimo_expediente.signos_vitales:
            sv = ultimo_expediente.signos_vitales
            # Intentar obtener presión arterial de diferentes formatos
            if "presion_arterial_sistolica" in sv:
                datos["presion_sistolica"] = sv.get("presion_arterial_sistolica")
            if "presion_arterial_diastolica" in sv:
                datos["presion_diastolica"] = sv.get("presion_arterial_diastolica")
            # Formato alternativo: "presion_arterial": "120/80"
            if "presion_arterial" in sv and isinstance(sv["presion_arterial"], str):
                try:
                    sistolica, diastolica = sv["presion_arterial"].split("/")
                    datos["presion_sistolica"] = float(sistolica)
                    datos["presion_diastolica"] = float(diastolica)
                except:
                    pass

            datos["peso"] = sv.get("peso")
            datos["talla"] = sv.get("talla") or sv.get("estatura")

            if datos.get("peso") and datos.get("talla"):
                talla_m = datos["talla"] / 100
                datos["imc"] = datos["peso"] / (talla_m**2)

        # Laboratorios recientes
        result = await db.execute(
            select(PruebaLaboratorio)
            .where(PruebaLaboratorio.paciente_id == paciente_id)
            .where(
                PruebaLaboratorio.fecha_resultado
                >= datetime.utcnow() - timedelta(days=180)
            )
            .order_by(desc(PruebaLaboratorio.fecha_resultado))
        )
        labs = result.scalars().all()

        for lab in labs:
            if lab.resultados:
                for param, valor in lab.resultados.items():
                    # Manejar tanto dict como float/int directo
                    valor_numerico = (
                        valor.get("valor") if isinstance(valor, dict) else valor
                    )

                    if "colesterol" in param.lower():
                        datos["colesterol_total"] = valor_numerico
                    elif "hdl" in param.lower():
                        datos["hdl"] = valor_numerico
                    elif "ldl" in param.lower():
                        datos["ldl"] = valor_numerico
                    elif "glucosa" in param.lower():
                        datos["glucosa"] = valor_numerico
                    elif "hba1c" in param.lower():
                        datos["hba1c"] = valor_numerico

        # Extraer condiciones de antecedentes
        antecedentes_lower = [a.lower() for a in datos.get("antecedentes", [])]
        datos["diabetes"] = any("diabetes" in a for a in antecedentes_lower)
        datos["hipertension"] = any(
            "hipertension" in a or "hipertensión" in a for a in antecedentes_lower
        )
        datos["fuma"] = any(
            "fumador" in a or "tabaquismo" in a for a in antecedentes_lower
        )

        return datos

    async def _analizar_riesgo_con_ia(
        self, tipo_riesgo: str, datos: Dict[str, Any], score: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Análisis complementario con IA"""
        from fastapi import HTTPException
        import logging

        logger = logging.getLogger(__name__)

        prompt = f"""Analiza el riesgo {tipo_riesgo} de este paciente:

DATOS:
{self._formatear_datos(datos)}

SCORE CALCULADO:
{score}

Proporciona:
1. Factores de riesgo identificados (con su impacto)
2. Factores protectores
3. Recomendaciones específicas y personalizadas
4. Estudios adicionales sugeridos

IMPORTANTE: Responde SOLO con JSON válido, sin texto adicional.

Formato JSON:
{{
    "factores_riesgo": [
        {{"nombre": "...", "impacto": "alto/medio/bajo", "modificable": true/false}}
    ],
    "factores_protectores": ["..."],
    "recomendaciones": ["..."],
    "estudios_sugeridos": ["..."]
}}"""

        response = await chat_completion(
            messages=[
                {
                    "role": "system",
                    "content": "Eres un médico experto en medicina preventiva. IMPORTANTE: Responde SOLO con JSON válido, sin texto adicional antes o después.",
                },
                {"role": "user", "content": prompt},
            ],
            model="gpt-4o",
            temperature=0.3,
            response_format={"type": "json_object"},
        )

        # Obtener contenido de la respuesta
        raw_content = response.choices[0].message.content

        # Validar que no esté vacío
        if not raw_content or not raw_content.strip():
            logger.error("La IA devolvió una respuesta vacía para predicción de riesgo")
            raise HTTPException(
                status_code=502,
                detail="La IA devolvió una respuesta vacía. Por favor, intenta de nuevo.",
            )

        # Intentar parsear JSON
        try:
            analisis_ia = json.loads(raw_content)
            return analisis_ia
        except json.JSONDecodeError as e:
            logger.error(f"Respuesta inválida del modelo de IA: {raw_content[:500]}")
            logger.error(f"Error de JSON: {str(e)}")

            # Intentar extraer JSON si está envuelto en texto
            if "```json" in raw_content:
                try:
                    content = raw_content.split("```json")[1].split("```")[0].strip()
                    analisis_ia = json.loads(content)
                    return analisis_ia
                except:
                    pass
            elif "```" in raw_content:
                try:
                    content = raw_content.split("```")[1].split("```")[0].strip()
                    analisis_ia = json.loads(content)
                    return analisis_ia
                except:
                    pass

            # Si todo falla, devolver estructura básica
            logger.warning("Devolviendo estructura básica de fallback")
            return {
                "factores_riesgo": [
                    {
                        "nombre": "Evaluación manual requerida",
                        "impacto": "medio",
                        "modificable": False,
                    }
                ],
                "factores_protectores": ["Consultar con especialista"],
                "recomendaciones": ["Revisión manual del caso por médico especialista"],
                "estudios_sugeridos": ["Evaluación clínica completa"],
            }

    def _formatear_datos(self, datos: Dict[str, Any]) -> str:
        """Formatear datos para prompt"""
        lines = []
        for key, value in datos.items():
            if value is not None:
                lines.append(f"- {key}: {value}")
        return "\n".join(lines)
