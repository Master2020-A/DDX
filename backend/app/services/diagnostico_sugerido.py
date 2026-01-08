"""
Servicio para generar diagnósticos sugeridos usando IA.
Analiza toda la información disponible del paciente.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from uuid import UUID
from typing import Dict, List, Any
from datetime import datetime, timedelta
from openai import OpenAI
import os

from app.models.paciente import Paciente
from app.models.consulta import Consulta
from app.models.laboratorio import PruebaLaboratorio
from app.models.estudios_especiales import EstudioEKG, EstudioEEG, Ecografia
from app.core.config import settings


class DiagnosticoSugeridoService:
    """Servicio para generar diagnósticos sugeridos con IA"""

    def __init__(self, db: AsyncSession):
        self.db = db
        if not settings.OPENAI_API_KEY:
            raise ValueError(
                "OPENAI_API_KEY no está configurada. "
                "Por favor configura la variable de entorno OPENAI_API_KEY en el archivo .env"
            )
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)

    async def generar_diagnostico_sugerido(self, paciente_id: UUID) -> Dict[str, Any]:
        """
        Genera un diagnóstico sugerido basado en toda la información del paciente.

        Returns:
            Dict con diagnósticos sugeridos, evidencia y recomendaciones
        """
        # 1. Recopilar toda la información del paciente
        datos_paciente = await self._recopilar_datos_paciente(paciente_id)

        # 2. Generar prompt para la IA
        prompt = self._construir_prompt(datos_paciente)

        # 3. Llamar a OpenAI
        respuesta_ia = await self._analizar_con_ia(prompt)

        # 4. Estructurar la respuesta
        resultado = self._estructurar_respuesta(respuesta_ia, datos_paciente)

        return resultado

    async def _recopilar_datos_paciente(self, paciente_id: UUID) -> Dict[str, Any]:
        """Recopila toda la información relevante del paciente"""

        # Obtener paciente
        result = await self.db.execute(
            select(Paciente).where(Paciente.id == paciente_id)
        )
        paciente = result.scalar_one_or_none()

        if not paciente:
            raise ValueError("Paciente no encontrado")

        # Fecha límite para datos recientes (últimos 30 días)
        fecha_limite = datetime.utcnow() - timedelta(days=30)

        # Última consulta
        result = await self.db.execute(
            select(Consulta)
            .where(Consulta.paciente_id == paciente_id)
            .order_by(desc(Consulta.fecha_hora))
            .limit(1)
        )
        ultima_consulta = result.scalar_one_or_none()

        # Laboratorios recientes
        result = await self.db.execute(
            select(PruebaLaboratorio)
            .where(
                PruebaLaboratorio.paciente_id == paciente_id,
                PruebaLaboratorio.fecha_resultado >= fecha_limite,
            )
            .order_by(desc(PruebaLaboratorio.fecha_resultado))
        )
        laboratorios = result.scalars().all()

        # Estudios EKG recientes
        result = await self.db.execute(
            select(EstudioEKG)
            .where(
                EstudioEKG.paciente_id == paciente_id,
                EstudioEKG.fecha_estudio >= fecha_limite,
            )
            .order_by(desc(EstudioEKG.fecha_estudio))
        )
        estudios_ekg = result.scalars().all()

        # Estudios EEG recientes
        result = await self.db.execute(
            select(EstudioEEG)
            .where(
                EstudioEEG.paciente_id == paciente_id,
                EstudioEEG.fecha_estudio >= fecha_limite,
            )
            .order_by(desc(EstudioEEG.fecha_estudio))
        )
        estudios_eeg = result.scalars().all()

        # Ecografías recientes
        result = await self.db.execute(
            select(Ecografia)
            .where(
                Ecografia.paciente_id == paciente_id,
                Ecografia.fecha_estudio >= fecha_limite,
            )
            .order_by(desc(Ecografia.fecha_estudio))
        )
        ecografias = result.scalars().all()

        return {
            "paciente": paciente,
            "ultima_consulta": ultima_consulta,
            "laboratorios": laboratorios,
            "estudios_ekg": estudios_ekg,
            "estudios_eeg": estudios_eeg,
            "ecografias": ecografias,
        }

    def _construir_prompt(self, datos: Dict[str, Any]) -> str:
        """Construye el prompt para la IA"""

        paciente = datos["paciente"]
        consulta = datos["ultima_consulta"]

        alergias_str = ", ".join(paciente.alergias) if paciente.alergias else "Ninguna"

        prompt = f"""Eres un médico experto analizando la información de un paciente para generar un diagnóstico diferencial.

INFORMACIÓN DEL PACIENTE:
- Edad: {paciente.edad} años
- Sexo: {paciente.genero or 'No especificado'}
- Tipo de Sangre: {paciente.tipo_sangre or 'No especificado'}
- Alergias: {alergias_str}
"""

        # Agregar información de la última consulta
        if consulta:
            sintomas_str = (
                ", ".join(consulta.sintomas)
                if consulta.sintomas
                else "No especificados"
            )
            prompt += f"""
ÚLTIMA CONSULTA ({consulta.fecha_hora.strftime('%d/%m/%Y')}):
- Motivo: {consulta.motivo_consulta}
- Síntomas: {sintomas_str}
- Estado: {consulta.estado}
"""

        # Agregar laboratorios
        if datos["laboratorios"]:
            prompt += "\nRESULTADOS DE LABORATORIO RECIENTES:\n"
            for lab in datos["laboratorios"][:3]:  # Solo los 3 más recientes
                fecha_lab = (
                    lab.fecha_resultado.strftime("%d/%m/%Y")
                    if lab.fecha_resultado
                    else "Fecha no disponible"
                )
                prompt += f"\n{lab.tipo_prueba} ({fecha_lab}):\n"
                if lab.resultados:
                    for param, valor in lab.resultados.items():
                        estado = ""
                        if lab.valores_anormales and param in lab.valores_anormales:
                            estado = " [ANORMAL]"
                        if lab.valores_criticos and param in lab.valores_criticos:
                            estado = " [CRÍTICO]"
                        prompt += f"  - {param}: {valor}{estado}\n"

                if lab.interpretacion:
                    prompt += f"  Interpretación: {lab.interpretacion}\n"

        # Agregar estudios EKG
        if datos["estudios_ekg"]:
            prompt += "\nESTUDIOS EKG RECIENTES:\n"
            for ekg in datos["estudios_ekg"][:2]:
                prompt += f"\nEKG ({ekg.fecha_estudio.strftime('%d/%m/%Y')}):\n"
                if ekg.frecuencia_cardiaca:
                    prompt += f"  - FC: {ekg.frecuencia_cardiaca} lpm\n"
                if ekg.ritmo:
                    prompt += f"  - Ritmo: {ekg.ritmo}\n"
                if ekg.intervalo_pr:
                    prompt += f"  - Intervalo PR: {ekg.intervalo_pr} ms\n"
                if ekg.duracion_qrs:
                    prompt += f"  - QRS: {ekg.duracion_qrs} ms\n"
                if ekg.interpretacion_ia:
                    prompt += f"  Interpretación: {ekg.interpretacion_ia}\n"
                if ekg.es_critico:
                    prompt += f"  ⚠️ HALLAZGO CRÍTICO\n"

        # Agregar estudios EEG
        if datos["estudios_eeg"]:
            prompt += "\nESTUDIOS EEG RECIENTES:\n"
            for eeg in datos["estudios_eeg"][:2]:
                prompt += f"\nEEG ({eeg.fecha_estudio.strftime('%d/%m/%Y')}):\n"
                if eeg.tipo_estudio:
                    prompt += f"  - Tipo: {eeg.tipo_estudio}\n"
                if eeg.actividad_fondo:
                    prompt += f"  - Actividad de fondo: {eeg.actividad_fondo}\n"
                if eeg.simetria:
                    prompt += f"  - Simetría: {eeg.simetria}\n"
                if eeg.interpretacion_ia:
                    prompt += f"  Interpretación: {eeg.interpretacion_ia}\n"

        # Agregar ecografías
        if datos["ecografias"]:
            prompt += "\nECOGRAFÍAS RECIENTES:\n"
            for eco in datos["ecografias"][:2]:
                tipo_eco = (
                    eco.tipo_ecografia.upper() if eco.tipo_ecografia else "ECOGRAFÍA"
                )
                prompt += f"\n{tipo_eco} ({eco.fecha_estudio.strftime('%d/%m/%Y')}):\n"
                if eco.modo:
                    prompt += f"  - Modo: {eco.modo}\n"
                if eco.interpretacion_ia:
                    prompt += f"  Interpretación: {eco.interpretacion_ia}\n"

        prompt += """

TAREA:
Genera un diagnóstico diferencial con los 3-5 diagnósticos más probables basándote en TODA la información anterior.

Para cada diagnóstico, proporciona:
1. Nombre del diagnóstico
2. Probabilidad estimada (0-100%)
3. Evidencia que lo soporta (datos específicos del paciente)
4. Nivel de urgencia (bajo, moderado, alto, crítico)

Además, proporciona:
- Alertas clínicas importantes
- Recomendaciones de estudios adicionales
- Recomendaciones de tratamiento o seguimiento

Responde en formato JSON con esta estructura:
{
  "diagnosticos": [
    {
      "nombre": "Nombre del diagnóstico",
      "codigo_cie10": "Código CIE-10 si aplica",
      "probabilidad": 85,
      "evidencia": ["Evidencia 1", "Evidencia 2"],
      "urgencia": "alto"
    }
  ],
  "alertas": ["Alerta 1", "Alerta 2"],
  "recomendaciones_estudios": ["Estudio 1", "Estudio 2"],
  "recomendaciones_tratamiento": ["Recomendación 1", "Recomendación 2"],
  "resumen_clinico": "Resumen breve del caso"
}
"""

        return prompt

    async def _analizar_con_ia(self, prompt: str) -> str:
        """Llama a OpenAI para analizar los datos"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",  # Modelo de OpenAI
                messages=[
                    {
                        "role": "system",
                        "content": "Eres un médico experto en diagnóstico diferencial. Analiza la información del paciente y proporciona diagnósticos sugeridos basados en evidencia. DEBES responder ÚNICAMENTE en formato JSON válido.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,  # Más determinista para diagnósticos
                response_format={"type": "json_object"},
            )

            return response.choices[0].message.content

        except Exception as e:
            raise Exception(f"Error al analizar con IA: {str(e)}")

    def _estructurar_respuesta(
        self, respuesta_ia: str, datos: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Estructura la respuesta de la IA"""

        import json

        try:
            resultado = json.loads(respuesta_ia)

            # Agregar metadata
            resultado["fecha_analisis"] = datetime.utcnow().isoformat()
            resultado["paciente_id"] = str(datos["paciente"].id)
            resultado["datos_analizados"] = {
                "consultas": 1 if datos["ultima_consulta"] else 0,
                "laboratorios": len(datos["laboratorios"]),
                "estudios_ekg": len(datos["estudios_ekg"]),
                "estudios_eeg": len(datos["estudios_eeg"]),
                "ecografias": len(datos["ecografias"]),
            }

            # Ordenar diagnósticos por probabilidad
            if "diagnosticos" in resultado:
                resultado["diagnosticos"] = sorted(
                    resultado["diagnosticos"],
                    key=lambda x: x.get("probabilidad", 0),
                    reverse=True,
                )

            return resultado

        except json.JSONDecodeError as e:
            raise Exception(f"Error al parsear respuesta de IA: {str(e)}")
