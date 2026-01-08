"""
WebSocket Endpoints para Telemedicina
"""

from fastapi import WebSocket, WebSocketDisconnect, Depends, Query
from typing import Optional
import logging
import json

from app.websocket.telemedicina_socket import socket_manager

logger = logging.getLogger(__name__)


async def websocket_telemedicina_endpoint(
    websocket: WebSocket,
    sala_id: str = Query(...),
    user_id: str = Query(...),
    role: str = Query(...),  # "medico" o "paciente"
    token: str = Query(...),
):
    """
    Endpoint WebSocket para telemedicina

    Maneja:
    - Chat en tiempo real
    - Señalización WebRTC
    - Notificaciones de estado
    - Compartir pantalla
    """

    await websocket.accept()

    try:
        # Conectar usuario a la sala
        await socket_manager.conectar_usuario(
            websocket=websocket,
            sala_id=sala_id,
            user_id=user_id,
            role=role,
        )

        logger.info(f"WebSocket conectado: user={user_id}, sala={sala_id}, role={role}")

        # Loop principal para recibir mensajes
        while True:
            data = await websocket.receive_text()
            mensaje = json.loads(data)

            tipo = mensaje.get("type")

            # Manejar diferentes tipos de mensajes
            if tipo == "chat_message":
                # Mensaje de chat
                await socket_manager.enviar_mensaje_chat(
                    sala_id=sala_id,
                    user_id=user_id,
                    mensaje=mensaje.get("mensaje", {}),
                )

            elif tipo == "webrtc_signal":
                # Señal WebRTC (offer, answer, ice-candidate)
                await socket_manager.enviar_senal_webrtc(
                    sala_id=sala_id,
                    user_id=user_id,
                    senal=mensaje.get("signal", {}),
                    target_user_id=mensaje.get("target_user_id"),
                )

            elif tipo == "screen_share":
                # Compartir pantalla
                await socket_manager.compartir_pantalla(
                    sala_id=sala_id,
                    user_id=user_id,
                    estado=mensaje.get("estado", False),
                )

            elif tipo == "media_state":
                # Cambio en audio/video
                await socket_manager.actualizar_estado_media(
                    sala_id=sala_id,
                    user_id=user_id,
                    audio=mensaje.get("audio"),
                    video=mensaje.get("video"),
                )

            elif tipo == "ping":
                # Ping para mantener conexión viva
                await websocket.send_json({"type": "pong"})

            else:
                logger.warning(f"Tipo de mensaje desconocido: {tipo}")

    except WebSocketDisconnect:
        logger.info(f"WebSocket desconectado: user={user_id}, sala={sala_id}")
        await socket_manager.desconectar_usuario(user_id)

    except Exception as e:
        logger.error(f"Error en WebSocket: {e}")
        await socket_manager.desconectar_usuario(user_id)
        await websocket.close()
