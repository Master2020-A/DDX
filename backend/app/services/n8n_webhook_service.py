"""
Servicio de Webhooks para N8N
Emisión de eventos a N8N para automatización
"""

from typing import Dict, Any, Optional, List
import httpx
import asyncio
from datetime import datetime
import os
import logging

logger = logging.getLogger(__name__)


class N8NWebhookService:
    """Servicio para emitir eventos a N8N"""

    def __init__(self):
        self.n8n_base_url = os.getenv("N8N_WEBHOOK_URL", "http://localhost:5678/webhook")
        self.enabled = os.getenv("N8N_WEBHOOKS_ENABLED", "true").lower() == "true"
        self.timeout = int(os.getenv("N8N_WEBHOOK_TIMEOUT", "5"))
        
    async def emit(self, event_type: str, data: Dict[str, Any], priority: str = "normal"):
        """
        Emitir evento a N8N
        
        Args:
            event_type: Tipo de evento (ej: "paciente.creado")
            data: Datos del evento
            priority: Prioridad del evento (low, normal, high, critical)
        """
        if not self.enabled:
            logger.debug(f"Webhooks N8N deshabilitados. Evento {event_type} no enviado.")
            return
        
        payload = {
            "event": event_type,
            "data": data,
            "timestamp": datetime.utcnow().isoformat(),
            "source": "DDX",
            "priority": priority
        }
        
        # Convertir event_type a URL-friendly (paciente.creado -> paciente-creado)
        event_path = event_type.replace('.', '-')
        webhook_url = f"{self.n8n_base_url}/{event_path}"
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(webhook_url, json=payload)
                response.raise_for_status()
                logger.info(f"Evento {event_type} enviado a N8N exitosamente")
        except httpx.TimeoutException:
            logger.warning(f"Timeout enviando evento {event_type} a N8N")
        except httpx.HTTPError as e:
            logger.error(f"Error HTTP enviando evento {event_type} a N8N: {e}")
        except Exception as e:
            logger.error(f"Error enviando evento {event_type} a N8N: {e}")
    
    # ========== EVENTOS DE PACIENTES ==========
    
    async def emit_paciente_creado(self, paciente_id: str, paciente_data: dict):
        """Emitir evento cuando se crea un paciente"""
        await self.emit("paciente.creado", {
            "paciente_id": paciente_id,
            **paciente_data
        })
    
    async def emit_paciente_actualizado(self, paciente_id: str, cambios: dict):
        """Emitir evento cuando se actualiza un paciente"""
        await self.emit("paciente.actualizado", {
            "paciente_id": paciente_id,
            "cambios": cambios
        })
    
    # ========== EVENTOS DE LABORATORIO ==========
    
    async def emit_laboratorio_resultado_critico(
        self, 
        resultado_id: str, 
        paciente_id: str,
        paciente_nombre: str,
        parametro: str, 
        valor: float,
        rango_normal: str,
        nivel: str
    ):
        """Emitir evento cuando hay un resultado de laboratorio crítico"""
        await self.emit("laboratorio.resultado_critico", {
            "resultado_id": resultado_id,
            "paciente_id": paciente_id,
            "paciente_nombre": paciente_nombre,
            "parametro": parametro,
            "valor": valor,
            "rango_normal": rango_normal,
            "nivel": nivel
        }, priority="critical")
    
    async def emit_laboratorio_completado(
        self,
        resultado_id: str,
        paciente_id: str,
        tipo_prueba: str,
        area: str
    ):
        """Emitir evento cuando se completa un resultado de laboratorio"""
        await self.emit("laboratorio.completado", {
            "resultado_id": resultado_id,
            "paciente_id": paciente_id,
            "tipo_prueba": tipo_prueba,
            "area": area
        })
    
    # ========== EVENTOS DE CITAS ==========
    
    async def emit_cita_agendada(
        self,
        cita_id: str,
        paciente_id: str,
        paciente_nombre: str,
        paciente_email: str,
        paciente_telefono: str,
        medico_id: str,
        medico_nombre: str,
        fecha: str,
        hora: str,
        tipo: str
    ):
        """Emitir evento cuando se agenda una cita"""
        await self.emit("cita.agendada", {
            "cita_id": cita_id,
            "paciente_id": paciente_id,
            "paciente_nombre": paciente_nombre,
            "paciente_email": paciente_email,
            "paciente_telefono": paciente_telefono,
            "medico_id": medico_id,
            "medico_nombre": medico_nombre,
            "fecha": fecha,
            "hora": hora,
            "tipo": tipo
        })
    
    async def emit_cita_cancelada(
        self,
        cita_id: str,
        paciente_id: str,
        motivo: str
    ):
        """Emitir evento cuando se cancela una cita"""
        await self.emit("cita.cancelada", {
            "cita_id": cita_id,
            "paciente_id": paciente_id,
            "motivo": motivo
        })
    
    async def emit_cita_completada(
        self,
        cita_id: str,
        paciente_id: str,
        medico_id: str,
        duracion_minutos: int
    ):
        """Emitir evento cuando se completa una cita"""
        await self.emit("cita.completada", {
            "cita_id": cita_id,
            "paciente_id": paciente_id,
            "medico_id": medico_id,
            "duracion_minutos": duracion_minutos
        })
    
    # ========== EVENTOS DE IMÁGENES MÉDICAS ==========
    
    async def emit_imagen_subida(
        self,
        imagen_id: str,
        paciente_id: str,
        tipo: str,
        formato: str,
        tamano_mb: float
    ):
        """Emitir evento cuando se sube una imagen médica"""
        await self.emit("imagen.subida", {
            "imagen_id": imagen_id,
            "paciente_id": paciente_id,
            "tipo": tipo,
            "formato": formato,
            "tamano_mb": tamano_mb
        })
    
    async def emit_imagen_analisis_completado(
        self,
        imagen_id: str,
        paciente_id: str,
        tipo_analisis: str,
        hallazgos: dict
    ):
        """Emitir evento cuando se completa el análisis de una imagen"""
        await self.emit("imagen.analisis_completado", {
            "imagen_id": imagen_id,
            "paciente_id": paciente_id,
            "tipo_analisis": tipo_analisis,
            "hallazgos": hallazgos
        })
    
    # ========== EVENTOS DE ESTUDIOS ESPECIALES ==========
    
    async def emit_estudio_completado(
        self,
        estudio_id: str,
        paciente_id: str,
        tipo_estudio: str,
        categoria: str
    ):
        """Emitir evento cuando se completa un estudio especial"""
        await self.emit("estudio.completado", {
            "estudio_id": estudio_id,
            "paciente_id": paciente_id,
            "tipo_estudio": tipo_estudio,
            "categoria": categoria
        })
    
    async def emit_estudio_interpretacion_ia(
        self,
        estudio_id: str,
        paciente_id: str,
        tipo_estudio: str,
        interpretacion: str,
        confianza: float
    ):
        """Emitir evento cuando se genera interpretación IA de un estudio"""
        await self.emit("estudio.interpretacion_ia", {
            "estudio_id": estudio_id,
            "paciente_id": paciente_id,
            "tipo_estudio": tipo_estudio,
            "interpretacion": interpretacion,
            "confianza": confianza
        })
    
    # ========== EVENTOS DE RECETAS ==========
    
    async def emit_receta_emitida(
        self,
        receta_id: str,
        paciente_id: str,
        paciente_nombre: str,
        medico_id: str,
        medicamentos: List[dict],
        farmacia_preferida: Optional[str] = None
    ):
        """Emitir evento cuando se emite una receta"""
        await self.emit("receta.emitida", {
            "receta_id": receta_id,
            "paciente_id": paciente_id,
            "paciente_nombre": paciente_nombre,
            "medico_id": medico_id,
            "medicamentos": medicamentos,
            "farmacia_preferida": farmacia_preferida
        })
    
    # ========== EVENTOS DE TELEMEDICINA ==========
    
    async def emit_consulta_iniciada(
        self,
        consulta_id: str,
        paciente_id: str,
        medico_id: str,
        tipo: str
    ):
        """Emitir evento cuando se inicia una consulta de telemedicina"""
        await self.emit("telemedicina.consulta_iniciada", {
            "consulta_id": consulta_id,
            "paciente_id": paciente_id,
            "medico_id": medico_id,
            "tipo": tipo
        })
    
    async def emit_consulta_finalizada(
        self,
        consulta_id: str,
        paciente_id: str,
        medico_id: str,
        duracion_minutos: int,
        grabacion_url: Optional[str] = None
    ):
        """Emitir evento cuando finaliza una consulta de telemedicina"""
        await self.emit("telemedicina.consulta_finalizada", {
            "consulta_id": consulta_id,
            "paciente_id": paciente_id,
            "medico_id": medico_id,
            "duracion_minutos": duracion_minutos,
            "grabacion_url": grabacion_url
        })
    
    # ========== EVENTOS DE DIAGNÓSTICO ==========
    
    async def emit_diagnostico_generado(
        self,
        diagnostico_id: str,
        paciente_id: str,
        diagnostico_principal: str,
        diferenciales: List[str],
        confianza: float
    ):
        """Emitir evento cuando se genera un diagnóstico con IA"""
        await self.emit("diagnostico.generado", {
            "diagnostico_id": diagnostico_id,
            "paciente_id": paciente_id,
            "diagnostico_principal": diagnostico_principal,
            "diferenciales": diferenciales,
            "confianza": confianza
        }, priority="high")
    
    # ========== EVENTOS DE FHIR ==========
    
    async def emit_recurso_fhir_sincronizado(
        self,
        recurso_tipo: str,
        recurso_id: str,
        servidor_destino: str,
        exitoso: bool
    ):
        """Emitir evento cuando se sincroniza un recurso FHIR"""
        await self.emit("fhir.recurso_sincronizado", {
            "recurso_tipo": recurso_tipo,
            "recurso_id": recurso_id,
            "servidor_destino": servidor_destino,
            "exitoso": exitoso
        })
    
    # ========== EVENTOS DE SISTEMA ==========
    
    async def emit_backup_completado(
        self,
        backup_id: str,
        tamano_mb: float,
        duracion_segundos: int,
        ubicacion: str
    ):
        """Emitir evento cuando se completa un backup"""
        await self.emit("sistema.backup_completado", {
            "backup_id": backup_id,
            "tamano_mb": tamano_mb,
            "duracion_segundos": duracion_segundos,
            "ubicacion": ubicacion
        })
    
    async def emit_alerta_sistema(
        self,
        tipo_alerta: str,
        severidad: str,
        mensaje: str,
        detalles: dict
    ):
        """Emitir evento de alerta del sistema"""
        priority_map = {
            "info": "low",
            "warning": "normal",
            "error": "high",
            "critical": "critical"
        }
        await self.emit("sistema.alerta", {
            "tipo_alerta": tipo_alerta,
            "severidad": severidad,
            "mensaje": mensaje,
            "detalles": detalles
        }, priority=priority_map.get(severidad, "normal"))


# Singleton global
n8n_webhook_service = N8NWebhookService()
