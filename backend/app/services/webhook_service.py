"""
Servicio de Webhooks para Interoperabilidad
Gestión de suscripciones y envío de eventos
"""

import hmac
import hashlib
import json
import time
from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID
import asyncio
import aiohttp
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, desc

from app.models.webhook_interoperabilidad import (
    WebhookSuscripcion,
    WebhookEntrega,
    EventoWebhook,
    EstadoWebhook,
)


class WebhookService:
    """Servicio para gestionar webhooks de interoperabilidad"""

    @staticmethod
    async def crear_suscripcion(
        db: AsyncSession,
        nombre: str,
        url: str,
        eventos: List[str],
        usuario_id: UUID,
        descripcion: Optional[str] = None,
        secret_key: Optional[str] = None,
        headers_adicionales: Optional[Dict[str, str]] = None,
        timeout_segundos: int = 30,
        reintentos_max: int = 3,
        filtros: Optional[Dict[str, Any]] = None,
        institucion_id: Optional[UUID] = None,
    ) -> WebhookSuscripcion:
        """
        Crea una nueva suscripción de webhook

        Args:
            db: Sesión de base de datos
            nombre: Nombre de la suscripción
            url: URL de destino
            eventos: Lista de eventos a suscribirse
            usuario_id: ID del usuario propietario
            descripcion: Descripción opcional
            secret_key: Clave secreta para firmar payloads (se genera si no se proporciona)
            headers_adicionales: Headers HTTP adicionales
            timeout_segundos: Timeout para las peticiones
            reintentos_max: Número máximo de reintentos
            filtros: Filtros opcionales para eventos
            institucion_id: ID de institución asociada (opcional)

        Returns:
            Suscripción creada
        """
        # Generar secret_key si no se proporciona
        if not secret_key:
            import secrets

            secret_key = secrets.token_urlsafe(32)

        suscripcion = WebhookSuscripcion(
            nombre=nombre,
            descripcion=descripcion,
            url=url,
            eventos=eventos,
            secret_key=secret_key,
            headers_adicionales=headers_adicionales,
            timeout_segundos=timeout_segundos,
            reintentos_max=reintentos_max,
            filtros=filtros,
            usuario_id=usuario_id,
            institucion_id=institucion_id,
        )

        db.add(suscripcion)
        await db.commit()
        await db.refresh(suscripcion)

        return suscripcion

    @staticmethod
    async def obtener_suscripciones(
        db: AsyncSession,
        usuario_id: Optional[UUID] = None,
        activo: Optional[bool] = None,
        evento: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[WebhookSuscripcion]:
        """
        Obtiene suscripciones de webhooks

        Args:
            db: Sesión de base de datos
            usuario_id: Filtrar por usuario
            activo: Filtrar por estado activo
            evento: Filtrar por evento específico
            limit: Límite de resultados
            offset: Offset para paginación

        Returns:
            Lista de suscripciones
        """
        query = select(WebhookSuscripcion)

        conditions = []
        if usuario_id:
            conditions.append(WebhookSuscripcion.usuario_id == usuario_id)
        if activo is not None:
            conditions.append(WebhookSuscripcion.activo == activo)
        if evento:
            # Buscar en el array JSONB de eventos
            conditions.append(WebhookSuscripcion.eventos.contains([evento]))

        if conditions:
            query = query.where(and_(*conditions))

        query = query.order_by(desc(WebhookSuscripcion.created_at))
        query = query.limit(limit).offset(offset)

        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def actualizar_suscripcion(
        db: AsyncSession, suscripcion_id: UUID, usuario_id: UUID, **datos
    ) -> Optional[WebhookSuscripcion]:
        """
        Actualiza una suscripción de webhook

        Args:
            db: Sesión de base de datos
            suscripcion_id: ID de la suscripción
            usuario_id: ID del usuario (para verificar permisos)
            **datos: Datos a actualizar

        Returns:
            Suscripción actualizada o None si no se encontró
        """
        query = select(WebhookSuscripcion).where(
            and_(
                WebhookSuscripcion.id == suscripcion_id,
                WebhookSuscripcion.usuario_id == usuario_id,
            )
        )

        result = await db.execute(query)
        suscripcion = result.scalar_one_or_none()

        if suscripcion:
            for key, value in datos.items():
                if hasattr(suscripcion, key):
                    setattr(suscripcion, key, value)

            await db.commit()
            await db.refresh(suscripcion)

        return suscripcion

    @staticmethod
    async def eliminar_suscripcion(
        db: AsyncSession, suscripcion_id: UUID, usuario_id: UUID
    ) -> bool:
        """
        Elimina una suscripción de webhook

        Args:
            db: Sesión de base de datos
            suscripcion_id: ID de la suscripción
            usuario_id: ID del usuario (para verificar permisos)

        Returns:
            True si se eliminó, False si no se encontró
        """
        query = select(WebhookSuscripcion).where(
            and_(
                WebhookSuscripcion.id == suscripcion_id,
                WebhookSuscripcion.usuario_id == usuario_id,
            )
        )

        result = await db.execute(query)
        suscripcion = result.scalar_one_or_none()

        if suscripcion:
            await db.delete(suscripcion)
            await db.commit()
            return True

        return False

    @staticmethod
    def generar_firma(payload: Dict[str, Any], secret_key: str) -> str:
        """
        Genera una firma HMAC-SHA256 del payload

        Args:
            payload: Datos a firmar
            secret_key: Clave secreta

        Returns:
            Firma en formato hexadecimal
        """
        payload_json = json.dumps(payload, sort_keys=True)
        signature = hmac.new(
            secret_key.encode("utf-8"), payload_json.encode("utf-8"), hashlib.sha256
        ).hexdigest()
        return signature

    @staticmethod
    async def enviar_evento(
        db: AsyncSession,
        evento: str,
        payload: Dict[str, Any],
        filtros_evento: Optional[Dict[str, Any]] = None,
    ) -> int:
        """
        Envía un evento a todas las suscripciones correspondientes

        Args:
            db: Sesión de base de datos
            evento: Tipo de evento
            payload: Datos del evento
            filtros_evento: Filtros del evento (ej: {"prioridad": "alta"})

        Returns:
            Número de webhooks enviados
        """
        # Obtener suscripciones activas para este evento
        query = select(WebhookSuscripcion).where(
            and_(
                WebhookSuscripcion.activo == True,
                WebhookSuscripcion.estado.in_(
                    [EstadoWebhook.ACTIVO, EstadoWebhook.ERROR]
                ),
                WebhookSuscripcion.eventos.contains([evento]),
            )
        )

        result = await db.execute(query)
        suscripciones = result.scalars().all()

        # Filtrar suscripciones según filtros del evento
        suscripciones_filtradas = []
        for suscripcion in suscripciones:
            if WebhookService._cumple_filtros(suscripcion, filtros_evento):
                suscripciones_filtradas.append(suscripcion)

        # Enviar a cada suscripción de forma asíncrona
        tareas = []
        for suscripcion in suscripciones_filtradas:
            tarea = WebhookService._enviar_a_suscripcion(
                db, suscripcion, evento, payload
            )
            tareas.append(tarea)

        if tareas:
            await asyncio.gather(*tareas, return_exceptions=True)

        return len(tareas)

    @staticmethod
    def _cumple_filtros(
        suscripcion: WebhookSuscripcion, filtros_evento: Optional[Dict[str, Any]]
    ) -> bool:
        """
        Verifica si el evento cumple con los filtros de la suscripción

        Args:
            suscripcion: Suscripción a verificar
            filtros_evento: Filtros del evento

        Returns:
            True si cumple los filtros
        """
        if not suscripcion.filtros or not filtros_evento:
            return True

        for key, valores_permitidos in suscripcion.filtros.items():
            if key in filtros_evento:
                valor_evento = filtros_evento[key]
                if isinstance(valores_permitidos, list):
                    if valor_evento not in valores_permitidos:
                        return False
                else:
                    if valor_evento != valores_permitidos:
                        return False

        return True

    @staticmethod
    async def _enviar_a_suscripcion(
        db: AsyncSession,
        suscripcion: WebhookSuscripcion,
        evento: str,
        payload: Dict[str, Any],
    ):
        """
        Envía un evento a una suscripción específica con reintentos

        Args:
            db: Sesión de base de datos
            suscripcion: Suscripción de destino
            evento: Tipo de evento
            payload: Datos del evento
        """
        # Preparar payload completo
        payload_completo = {
            "evento": evento,
            "timestamp": datetime.utcnow().isoformat(),
            "data": payload,
            "suscripcion_id": str(suscripcion.id),
        }

        # Generar firma
        firma = WebhookService.generar_firma(payload_completo, suscripcion.secret_key)

        # Preparar headers
        headers = {
            "Content-Type": "application/json",
            "X-Webhook-Signature": firma,
            "X-Webhook-Event": evento,
            "User-Agent": "DDX-Interoperabilidad-Webhook/1.0",
        }

        if suscripcion.headers_adicionales:
            headers.update(suscripcion.headers_adicionales)

        # Intentar envío con reintentos
        for intento in range(1, suscripcion.reintentos_max + 1):
            entrega = WebhookEntrega(
                suscripcion_id=suscripcion.id,
                evento=evento,
                payload=payload_completo,
                url=suscripcion.url,
                metodo="POST",
                headers=headers,
                intento=intento,
                max_intentos=suscripcion.reintentos_max,
                exitoso=False,
            )

            try:
                inicio = time.time()

                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        suscripcion.url,
                        json=payload_completo,
                        headers=headers,
                        timeout=aiohttp.ClientTimeout(
                            total=suscripcion.timeout_segundos
                        ),
                    ) as response:
                        tiempo_respuesta = int((time.time() - inicio) * 1000)

                        entrega.codigo_http = response.status
                        entrega.tiempo_respuesta_ms = tiempo_respuesta
                        entrega.respuesta = await response.text()
                        entrega.completado_at = datetime.utcnow()

                        # Considerar exitoso si el código es 2xx
                        if 200 <= response.status < 300:
                            entrega.exitoso = True
                            suscripcion.incrementar_estadisticas(exitoso=True)
                            db.add(entrega)
                            await db.commit()
                            return  # Éxito, no reintentar
                        else:
                            entrega.error = (
                                f"HTTP {response.status}: {entrega.respuesta[:500]}"
                            )

            except asyncio.TimeoutError:
                entrega.error = f"Timeout después de {suscripcion.timeout_segundos}s"
                entrega.completado_at = datetime.utcnow()
            except Exception as e:
                entrega.error = f"Error: {str(e)}"
                entrega.completado_at = datetime.utcnow()

            # Guardar intento fallido
            db.add(entrega)

            # Si no es el último intento, esperar antes de reintentar
            if intento < suscripcion.reintentos_max:
                await asyncio.sleep(2**intento)  # Backoff exponencial

        # Todos los intentos fallaron
        suscripcion.incrementar_estadisticas(exitoso=False)
        suscripcion.registrar_error(entrega.error or "Error desconocido")
        await db.commit()

    @staticmethod
    async def obtener_entregas(
        db: AsyncSession,
        suscripcion_id: Optional[UUID] = None,
        evento: Optional[str] = None,
        exitoso: Optional[bool] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[WebhookEntrega]:
        """
        Obtiene el historial de entregas de webhooks

        Args:
            db: Sesión de base de datos
            suscripcion_id: Filtrar por suscripción
            evento: Filtrar por evento
            exitoso: Filtrar por éxito/fallo
            limit: Límite de resultados
            offset: Offset para paginación

        Returns:
            Lista de entregas
        """
        query = select(WebhookEntrega)

        conditions = []
        if suscripcion_id:
            conditions.append(WebhookEntrega.suscripcion_id == suscripcion_id)
        if evento:
            conditions.append(WebhookEntrega.evento == evento)
        if exitoso is not None:
            conditions.append(WebhookEntrega.exitoso == exitoso)

        if conditions:
            query = query.where(and_(*conditions))

        query = query.order_by(desc(WebhookEntrega.created_at))
        query = query.limit(limit).offset(offset)

        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def probar_webhook(
        db: AsyncSession, suscripcion_id: UUID, usuario_id: UUID
    ) -> Dict[str, Any]:
        """
        Envía un evento de prueba a un webhook

        Args:
            db: Sesión de base de datos
            suscripcion_id: ID de la suscripción
            usuario_id: ID del usuario (para verificar permisos)

        Returns:
            Resultado de la prueba
        """
        query = select(WebhookSuscripcion).where(
            and_(
                WebhookSuscripcion.id == suscripcion_id,
                WebhookSuscripcion.usuario_id == usuario_id,
            )
        )

        result = await db.execute(query)
        suscripcion = result.scalar_one_or_none()

        if not suscripcion:
            return {"error": "Suscripción no encontrada"}

        # Payload de prueba
        payload_prueba = {
            "mensaje": "Este es un evento de prueba",
            "timestamp": datetime.utcnow().isoformat(),
            "suscripcion": {"id": str(suscripcion.id), "nombre": suscripcion.nombre},
        }

        # Enviar evento de prueba
        await WebhookService._enviar_a_suscripcion(
            db, suscripcion, "prueba.webhook", payload_prueba
        )

        return {
            "mensaje": "Evento de prueba enviado",
            "url": suscripcion.url,
            "timestamp": datetime.utcnow().isoformat(),
        }
