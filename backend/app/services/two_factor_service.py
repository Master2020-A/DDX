"""
Servicio para autenticación de dos factores (2FA)
"""

import pyotp
import qrcode
from io import BytesIO
import base64
import secrets
from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from uuid import UUID

from app.models.security import TwoFactorAuth
from app.models.usuario import Usuario


class TwoFactorService:
    """Servicio para gestión de 2FA"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def generate_secret(self, usuario_id: UUID) -> Tuple[str, str, str]:
        """
        Genera un secreto TOTP y códigos de respaldo para un usuario

        Returns:
            Tuple[secret, qr_code_base64, provisioning_uri]
        """
        # Obtener usuario
        result = await self.db.execute(select(Usuario).where(Usuario.id == usuario_id))
        usuario = result.scalar_one_or_none()

        if not usuario:
            raise ValueError("Usuario no encontrado")

        # Generar secreto TOTP
        secret = pyotp.random_base32()

        # Crear URI de aprovisionamiento
        totp = pyotp.TOTP(secret)
        provisioning_uri = totp.provisioning_uri(
            name=usuario.email, issuer_name="DDX Medical System"
        )

        # Generar código QR
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(provisioning_uri)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()

        # Generar códigos de respaldo
        backup_codes = [secrets.token_hex(4).upper() for _ in range(10)]

        # Guardar en base de datos
        result = await self.db.execute(
            select(TwoFactorAuth).where(TwoFactorAuth.usuario_id == usuario_id)
        )
        two_factor = result.scalar_one_or_none()

        if two_factor:
            # Actualizar existente
            two_factor.secret_key = secret
            two_factor.backup_codes = backup_codes
            two_factor.enabled = False
            two_factor.verified = False
        else:
            # Crear nuevo
            two_factor = TwoFactorAuth(
                usuario_id=usuario_id,
                secret_key=secret,
                backup_codes=backup_codes,
                enabled=False,
                verified=False,
                method="totp",
            )
            self.db.add(two_factor)

        await self.db.commit()

        return secret, qr_code_base64, provisioning_uri

    async def verify_and_enable(self, usuario_id: UUID, token: str) -> bool:
        """
        Verifica el token TOTP y habilita 2FA si es correcto
        """
        result = await self.db.execute(
            select(TwoFactorAuth).where(TwoFactorAuth.usuario_id == usuario_id)
        )
        two_factor = result.scalar_one_or_none()

        if not two_factor:
            return False

        # Verificar token
        totp = pyotp.TOTP(two_factor.secret_key)
        if totp.verify(token, valid_window=1):
            two_factor.enabled = True
            two_factor.verified = True
            two_factor.last_used_at = datetime.utcnow()
            await self.db.commit()
            return True

        return False

    async def verify_token(self, usuario_id: UUID, token: str) -> bool:
        """
        Verifica un token TOTP para autenticación
        """
        result = await self.db.execute(
            select(TwoFactorAuth).where(
                TwoFactorAuth.usuario_id == usuario_id, TwoFactorAuth.enabled == True
            )
        )
        two_factor = result.scalar_one_or_none()

        if not two_factor:
            return False

        # Verificar token TOTP
        totp = pyotp.TOTP(two_factor.secret_key)
        if totp.verify(token, valid_window=1):
            two_factor.last_used_at = datetime.utcnow()
            await self.db.commit()
            return True

        # Verificar código de respaldo
        if token.upper() in two_factor.backup_codes:
            # Remover código usado
            backup_codes = two_factor.backup_codes.copy()
            backup_codes.remove(token.upper())
            two_factor.backup_codes = backup_codes
            two_factor.last_used_at = datetime.utcnow()
            await self.db.commit()
            return True

        return False

    async def disable(self, usuario_id: UUID) -> bool:
        """
        Deshabilita 2FA para un usuario
        """
        result = await self.db.execute(
            select(TwoFactorAuth).where(TwoFactorAuth.usuario_id == usuario_id)
        )
        two_factor = result.scalar_one_or_none()

        if two_factor:
            two_factor.enabled = False
            await self.db.commit()
            return True

        return False

    async def is_enabled(self, usuario_id: UUID) -> bool:
        """
        Verifica si 2FA está habilitado para un usuario
        """
        result = await self.db.execute(
            select(TwoFactorAuth).where(
                TwoFactorAuth.usuario_id == usuario_id, TwoFactorAuth.enabled == True
            )
        )
        return result.scalar_one_or_none() is not None

    async def get_backup_codes(self, usuario_id: UUID) -> Optional[List[str]]:
        """
        Obtiene los códigos de respaldo de un usuario
        """
        result = await self.db.execute(
            select(TwoFactorAuth).where(TwoFactorAuth.usuario_id == usuario_id)
        )
        two_factor = result.scalar_one_or_none()

        if two_factor:
            return two_factor.backup_codes

        return None

    async def regenerate_backup_codes(self, usuario_id: UUID) -> List[str]:
        """
        Regenera los códigos de respaldo
        """
        result = await self.db.execute(
            select(TwoFactorAuth).where(TwoFactorAuth.usuario_id == usuario_id)
        )
        two_factor = result.scalar_one_or_none()

        if not two_factor:
            raise ValueError("2FA no configurado para este usuario")

        backup_codes = [secrets.token_hex(4).upper() for _ in range(10)]
        two_factor.backup_codes = backup_codes
        await self.db.commit()

        return backup_codes
