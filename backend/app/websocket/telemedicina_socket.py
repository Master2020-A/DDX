"""
WebSocket Server para Telemedicina
Maneja chat en tiempo real y señalización WebRTC
"""

import logging
from typing import Dict, Set
from uuid import UUID
import json

logger = logging.getLogger(__name__)


class TelemedicinaSocketManager:
    """Gestor de conexiones WebSocket para telemedicina"""

    def __init__(self):
        # Diccionario de salas activas: {sala_id: {user_id: websocket}}
        self.salas: Dict[str, Dict[str, any]] = {}

        # Diccionario de usuarios conectados: {user_id: {sala_id, role, websocket}}
        self.usuarios_conectados: Dict[str, Dict] = {}

        # Historial de señales WebRTC por sala (para late joiners)
        self.senales_webrtc: Dict[str, list] = {}

    async def conectar_usuario(
        self,
        websocket,
        sala_id: str,
        user_id: str,
        role: str,  # "medico" o "paciente"
    ):
        """Conectar un usuario a una sala"""

        # Crear sala si no existe
        if sala_id not in self.salas:
            self.salas[sala_id] = {}
            self.senales_webrtc[sala_id] = []

        # Agregar usuario a la sala
        self.salas[sala_id][user_id] = websocket

        # Registrar usuario conectado
        self.usuarios_conectados[user_id] = {
            "sala_id": sala_id,
            "role": role,
            "websocket": websocket,
        }

        logger.info(f"Usuario {user_id} ({role}) conectado a sala {sala_id}")

        # Notificar a otros usuarios en la sala
        await self.broadcast_to_sala(
            sala_id,
            {
                "type": "user_joined",
                "user_id": user_id,
                "role": role,
                "timestamp": self._get_timestamp(),
            },
            exclude_user=user_id,
        )

        # Enviar lista de usuarios conectados al nuevo usuario
        usuarios_en_sala = [
            {"user_id": uid, "role": self.usuarios_conectados[uid]["role"]}
            for uid in self.salas[sala_id].keys()
            if uid != user_id
        ]

        await self.send_to_user(
            user_id,
            {
                "type": "room_state",
                "usuarios": usuarios_en_sala,
                "timestamp": self._get_timestamp(),
            },
        )

    async def desconectar_usuario(self, user_id: str):
        """Desconectar un usuario"""

        if user_id not in self.usuarios_conectados:
            return

        info = self.usuarios_conectados[user_id]
        sala_id = info["sala_id"]
        role = info["role"]

        # Remover de la sala
        if sala_id in self.salas and user_id in self.salas[sala_id]:
            del self.salas[sala_id][user_id]

        # Remover de usuarios conectados
        del self.usuarios_conectados[user_id]

        logger.info(f"Usuario {user_id} ({role}) desconectado de sala {sala_id}")

        # Notificar a otros usuarios
        await self.broadcast_to_sala(
            sala_id,
            {
                "type": "user_left",
                "user_id": user_id,
                "role": role,
                "timestamp": self._get_timestamp(),
            },
        )

        # Limpiar sala si está vacía
        if sala_id in self.salas and len(self.salas[sala_id]) == 0:
            del self.salas[sala_id]
            if sala_id in self.senales_webrtc:
                del self.senales_webrtc[sala_id]

    async def enviar_mensaje_chat(
        self,
        sala_id: str,
        user_id: str,
        mensaje: Dict,
    ):
        """Enviar mensaje de chat a todos en la sala"""

        await self.broadcast_to_sala(
            sala_id,
            {
                "type": "chat_message",
                "user_id": user_id,
                "mensaje": mensaje,
                "timestamp": self._get_timestamp(),
            },
        )

    async def enviar_senal_webrtc(
        self,
        sala_id: str,
        user_id: str,
        senal: Dict,
        target_user_id: str = None,
    ):
        """
        Enviar señal WebRTC (offer, answer, ice-candidate)

        Args:
            sala_id: ID de la sala
            user_id: Usuario que envía la señal
            senal: Datos de la señal WebRTC
            target_user_id: Usuario destino (opcional, si None se envía a todos)
        """

        # Guardar señal en historial
        self.senales_webrtc[sala_id].append(
            {
                "from": user_id,
                "to": target_user_id,
                "signal": senal,
                "timestamp": self._get_timestamp(),
            }
        )

        mensaje = {
            "type": "webrtc_signal",
            "from_user_id": user_id,
            "signal": senal,
            "timestamp": self._get_timestamp(),
        }

        if target_user_id:
            # Enviar solo al usuario específico
            await self.send_to_user(target_user_id, mensaje)
        else:
            # Enviar a todos excepto al emisor
            await self.broadcast_to_sala(sala_id, mensaje, exclude_user=user_id)

    async def compartir_pantalla(
        self,
        sala_id: str,
        user_id: str,
        estado: bool,  # True = iniciando, False = deteniendo
    ):
        """Notificar que un usuario está compartiendo pantalla"""

        await self.broadcast_to_sala(
            sala_id,
            {
                "type": "screen_share",
                "user_id": user_id,
                "estado": estado,
                "timestamp": self._get_timestamp(),
            },
        )

    async def actualizar_estado_media(
        self,
        sala_id: str,
        user_id: str,
        audio: bool = None,
        video: bool = None,
    ):
        """Notificar cambios en audio/video"""

        mensaje = {
            "type": "media_state",
            "user_id": user_id,
            "timestamp": self._get_timestamp(),
        }

        if audio is not None:
            mensaje["audio"] = audio
        if video is not None:
            mensaje["video"] = video

        await self.broadcast_to_sala(sala_id, mensaje, exclude_user=user_id)

    async def broadcast_to_sala(
        self,
        sala_id: str,
        mensaje: Dict,
        exclude_user: str = None,
    ):
        """Enviar mensaje a todos los usuarios en una sala"""

        if sala_id not in self.salas:
            return

        for user_id, websocket in self.salas[sala_id].items():
            if exclude_user and user_id == exclude_user:
                continue

            try:
                await websocket.send_json(mensaje)
            except Exception as e:
                logger.error(f"Error enviando mensaje a {user_id}: {e}")

    async def send_to_user(self, user_id: str, mensaje: Dict):
        """Enviar mensaje a un usuario específico"""

        if user_id not in self.usuarios_conectados:
            logger.warning(f"Usuario {user_id} no está conectado")
            return

        websocket = self.usuarios_conectados[user_id]["websocket"]

        try:
            await websocket.send_json(mensaje)
        except Exception as e:
            logger.error(f"Error enviando mensaje a {user_id}: {e}")

    def _get_timestamp(self) -> str:
        """Obtener timestamp actual en formato ISO"""
        from datetime import datetime

        return datetime.utcnow().isoformat()

    def obtener_usuarios_en_sala(self, sala_id: str) -> list:
        """Obtener lista de usuarios conectados en una sala"""

        if sala_id not in self.salas:
            return []

        return [
            {
                "user_id": user_id,
                "role": self.usuarios_conectados[user_id]["role"],
            }
            for user_id in self.salas[sala_id].keys()
        ]

    def sala_existe(self, sala_id: str) -> bool:
        """Verificar si una sala existe"""
        return sala_id in self.salas

    def usuario_esta_conectado(self, user_id: str) -> bool:
        """Verificar si un usuario está conectado"""
        return user_id in self.usuarios_conectados


# Instancia global del gestor
socket_manager = TelemedicinaSocketManager()
