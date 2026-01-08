"""
Servicio de Transcripción de Voz a Texto usando OpenAI Whisper
"""

import os
import tempfile
from typing import Dict, Any, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import logging

from app.models.pln import TranscripcionVoz
from app.models.paciente import Paciente
from openai import AsyncOpenAI

logger = logging.getLogger(__name__)


class TranscripcionVozService:
    """Servicio para transcribir audio a texto usando Whisper"""

    def __init__(self):
        # Configurar cliente OpenAI
        api_key = os.getenv("OPENAI_API_KEY")
        groq_key = os.getenv("GROQ_API_KEY")

        # Groq también soporta Whisper
        if groq_key:
            self.client = AsyncOpenAI(
                api_key=groq_key, base_url="https://api.groq.com/openai/v1"
            )
            self.modelo = "whisper-large-v3"
        elif api_key:
            self.client = AsyncOpenAI(api_key=api_key)
            self.modelo = "whisper-1"
        else:
            self.client = None
            self.modelo = "demo"

    async def transcribir_audio(
        self,
        archivo_audio: bytes,
        nombre_archivo: str,
        paciente_id: Optional[UUID],
        medico_id: UUID,
        consulta_id: Optional[UUID],
        idioma: Optional[str] = None,
        db: AsyncSession = None,
    ) -> Dict[str, Any]:
        """
        Transcribir archivo de audio a texto

        Args:
            archivo_audio: Bytes del archivo de audio
            nombre_archivo: Nombre del archivo
            paciente_id: ID del paciente (opcional)
            medico_id: ID del médico
            consulta_id: ID de la consulta (opcional)
            idioma: Código de idioma (es, en, etc.) - opcional
            db: Sesión de base de datos

        Returns:
            Dict con transcripción y metadatos
        """

        if not self.client:
            return self._transcripcion_demo()

        try:
            # Guardar temporalmente el archivo
            with tempfile.NamedTemporaryFile(
                delete=False, suffix=os.path.splitext(nombre_archivo)[1]
            ) as temp_file:
                temp_file.write(archivo_audio)
                temp_path = temp_file.name

            # Transcribir con Whisper
            with open(temp_path, "rb") as audio_file:
                transcription = await self.client.audio.transcriptions.create(
                    model=self.modelo,
                    file=audio_file,
                    language=idioma,
                    response_format="verbose_json",
                )

            # Limpiar archivo temporal
            os.unlink(temp_path)

            # Extraer información
            texto_transcrito = transcription.text
            idioma_detectado = getattr(transcription, "language", idioma or "es")
            duracion = getattr(transcription, "duration", 0)

            # Guardar en base de datos si se proporciona sesión
            if db:
                transcripcion_db = TranscripcionVoz(
                    paciente_id=paciente_id,
                    medico_id=medico_id,
                    consulta_id=consulta_id,
                    archivo_audio=nombre_archivo,
                    duracion_segundos=duracion,
                    formato_audio=os.path.splitext(nombre_archivo)[1].replace(".", ""),
                    texto_transcrito=texto_transcrito,
                    idioma_detectado=idioma_detectado,
                    confianza=0.95,  # Whisper no proporciona confianza directa
                    modelo_utilizado=self.modelo,
                )

                db.add(transcripcion_db)
                await db.commit()
                await db.refresh(transcripcion_db)

                return {
                    "id": str(transcripcion_db.id),
                    "texto": texto_transcrito,
                    "idioma": idioma_detectado,
                    "duracion_segundos": duracion,
                    "modelo": self.modelo,
                    "confianza": 0.95,
                }

            return {
                "texto": texto_transcrito,
                "idioma": idioma_detectado,
                "duracion_segundos": duracion,
                "modelo": self.modelo,
                "confianza": 0.95,
            }

        except Exception as e:
            logger.error(f"Error en transcripción: {str(e)}")
            raise Exception(f"Error al transcribir audio: {str(e)}")

    async def transcribir_y_extraer(
        self,
        archivo_audio: bytes,
        nombre_archivo: str,
        paciente_id: Optional[UUID],
        medico_id: UUID,
        consulta_id: Optional[UUID],
        db: AsyncSession,
    ) -> Dict[str, Any]:
        """
        Transcribir audio y extraer información médica automáticamente

        Returns:
            Dict con transcripción e información extraída
        """

        # Transcribir
        resultado = await self.transcribir_audio(
            archivo_audio, nombre_archivo, paciente_id, medico_id, consulta_id, db=db
        )

        # Extraer información médica del texto
        from app.services.extraccion_informacion_service import (
            ExtraccionInformacionService,
        )

        extractor = ExtraccionInformacionService()
        informacion = await extractor.extraer_informacion(
            texto=resultado["texto"],
            tipo_documento="transcripcion_audio",
            paciente_id=paciente_id,
            medico_id=medico_id,
            consulta_id=consulta_id,
            db=db,
        )

        resultado["informacion_extraida"] = informacion

        return resultado

    def _transcripcion_demo(self) -> Dict[str, Any]:
        """Transcripción de demostración cuando no hay API key"""
        return {
            "texto": "[DEMO] Paciente refiere cefalea intensa de 3 días de evolución, acompañada de náuseas y fotofobia. Niega fiebre. Antecedentes de migraña. Presión arterial 120/80 mmHg, frecuencia cardíaca 72 lpm.",
            "idioma": "es",
            "duracion_segundos": 45.0,
            "modelo": "demo",
            "confianza": 1.0,
        }

    async def obtener_transcripciones_paciente(
        self, paciente_id: UUID, db: AsyncSession, limite: int = 10
    ) -> list:
        """Obtener transcripciones de un paciente"""

        result = await db.execute(
            select(TranscripcionVoz)
            .where(TranscripcionVoz.paciente_id == paciente_id)
            .order_by(TranscripcionVoz.created_at.desc())
            .limit(limite)
        )

        transcripciones = result.scalars().all()

        return [
            {
                "id": str(t.id),
                "texto": t.texto_transcrito,
                "idioma": t.idioma_detectado,
                "duracion_segundos": t.duracion_segundos,
                "fecha": t.created_at.isoformat(),
                "consulta_id": str(t.consulta_id) if t.consulta_id else None,
            }
            for t in transcripciones
        ]
