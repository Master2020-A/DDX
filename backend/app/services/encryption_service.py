"""
Servicio para encriptación end-to-end de datos sensibles
"""

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import Optional, Any
from uuid import UUID
import base64
import os
import json

from app.models.security import EncryptedData
from app.core.config import settings


class EncryptionService:
    """Servicio para encriptación de datos sensibles"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self._master_key = self._get_master_key()
        self._fernet = Fernet(self._master_key)

    def _get_master_key(self) -> bytes:
        """
        Obtiene o genera la clave maestra de encriptación
        """
        # En producción, esto debería venir de un KMS o variable de entorno segura
        key_string = getattr(settings, "ENCRYPTION_KEY", None)

        if key_string:
            return base64.urlsafe_b64decode(key_string.encode())

        # Generar clave temporal (solo para desarrollo)
        # En producción, esto debe ser una clave persistente y segura
        return Fernet.generate_key()

    def encrypt_string(self, data: str) -> str:
        """
        Encripta una cadena de texto
        """
        if not data:
            return data

        encrypted = self._fernet.encrypt(data.encode())
        return base64.urlsafe_b64encode(encrypted).decode()

    def decrypt_string(self, encrypted_data: str) -> str:
        """
        Desencripta una cadena de texto
        """
        if not encrypted_data:
            return encrypted_data

        try:
            decoded = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted = self._fernet.decrypt(decoded)
            return decrypted.decode()
        except Exception:
            return None

    def encrypt_dict(self, data: dict) -> str:
        """
        Encripta un diccionario convirtiéndolo a JSON
        """
        json_string = json.dumps(data)
        return self.encrypt_string(json_string)

    def decrypt_dict(self, encrypted_data: str) -> Optional[dict]:
        """
        Desencripta y convierte de vuelta a diccionario
        """
        decrypted = self.decrypt_string(encrypted_data)
        if decrypted:
            try:
                return json.loads(decrypted)
            except json.JSONDecodeError:
                return None
        return None

    async def store_encrypted_data(
        self,
        recurso_tipo: str,
        recurso_id: UUID,
        campo: str,
        data: Any,
        encriptado_por_id: Optional[UUID] = None,
    ) -> EncryptedData:
        """
        Almacena datos encriptados en la base de datos
        """
        # Convertir datos a string si es necesario
        if isinstance(data, dict):
            data_string = json.dumps(data)
        elif isinstance(data, (list, tuple)):
            data_string = json.dumps(list(data))
        else:
            data_string = str(data)

        # Encriptar
        encrypted = self.encrypt_string(data_string)

        # Verificar si ya existe
        result = await self.db.execute(
            select(EncryptedData).where(
                and_(
                    EncryptedData.recurso_tipo == recurso_tipo,
                    EncryptedData.recurso_id == recurso_id,
                    EncryptedData.campo == campo,
                )
            )
        )
        existing = result.scalar_one_or_none()

        if existing:
            # Actualizar
            existing.datos_encriptados = encrypted
            existing.encriptado_por_id = encriptado_por_id
            encrypted_data = existing
        else:
            # Crear nuevo
            encrypted_data = EncryptedData(
                recurso_tipo=recurso_tipo,
                recurso_id=recurso_id,
                campo=campo,
                datos_encriptados=encrypted,
                algoritmo="Fernet-AES-128",
                encriptado_por_id=encriptado_por_id,
            )
            self.db.add(encrypted_data)

        await self.db.commit()
        await self.db.refresh(encrypted_data)

        return encrypted_data

    async def retrieve_encrypted_data(
        self,
        recurso_tipo: str,
        recurso_id: UUID,
        campo: str,
    ) -> Optional[Any]:
        """
        Recupera y desencripta datos de la base de datos
        """
        result = await self.db.execute(
            select(EncryptedData).where(
                and_(
                    EncryptedData.recurso_tipo == recurso_tipo,
                    EncryptedData.recurso_id == recurso_id,
                    EncryptedData.campo == campo,
                )
            )
        )
        encrypted_data = result.scalar_one_or_none()

        if not encrypted_data:
            return None

        # Desencriptar
        decrypted = self.decrypt_string(encrypted_data.datos_encriptados)

        # Intentar parsear como JSON
        try:
            return json.loads(decrypted)
        except (json.JSONDecodeError, TypeError):
            return decrypted

    async def delete_encrypted_data(
        self,
        recurso_tipo: str,
        recurso_id: UUID,
        campo: Optional[str] = None,
    ) -> int:
        """
        Elimina datos encriptados
        Si campo es None, elimina todos los datos del recurso
        """
        query = select(EncryptedData).where(
            and_(
                EncryptedData.recurso_tipo == recurso_tipo,
                EncryptedData.recurso_id == recurso_id,
            )
        )

        if campo:
            query = query.where(EncryptedData.campo == campo)

        result = await self.db.execute(query)
        items = result.scalars().all()

        count = 0
        for item in items:
            await self.db.delete(item)
            count += 1

        await self.db.commit()
        return count

    def hash_password(
        self, password: str, salt: Optional[bytes] = None
    ) -> tuple[str, str]:
        """
        Hashea una contraseña usando PBKDF2

        Returns:
            Tuple[hash_base64, salt_base64]
        """
        if salt is None:
            salt = os.urandom(32)

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend(),
        )

        key = kdf.derive(password.encode())

        return (
            base64.urlsafe_b64encode(key).decode(),
            base64.urlsafe_b64encode(salt).decode(),
        )

    def verify_password(self, password: str, hash_b64: str, salt_b64: str) -> bool:
        """
        Verifica una contraseña contra su hash
        """
        try:
            salt = base64.urlsafe_b64decode(salt_b64.encode())
            stored_hash = base64.urlsafe_b64decode(hash_b64.encode())

            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
                backend=default_backend(),
            )

            kdf.verify(password.encode(), stored_hash)
            return True
        except Exception:
            return False

    @staticmethod
    def generate_key() -> str:
        """
        Genera una nueva clave de encriptación
        """
        key = Fernet.generate_key()
        return base64.urlsafe_b64encode(key).decode()
