"""
Schemas para el módulo de seguridad avanzada
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID


# ==================== 2FA ====================


class TwoFactorSetupResponse(BaseModel):
    """Respuesta al iniciar configuración de 2FA"""

    secret: str
    qr_code: str = Field(description="QR code en base64")
    provisioning_uri: str
    backup_codes: List[str]


class TwoFactorVerifyRequest(BaseModel):
    """Request para verificar token 2FA"""

    token: str = Field(min_length=6, max_length=6)


class TwoFactorStatusResponse(BaseModel):
    """Estado de 2FA de un usuario"""

    enabled: bool
    verified: bool
    method: str
    last_used_at: Optional[datetime] = None


class BackupCodesResponse(BaseModel):
    """Códigos de respaldo"""

    backup_codes: List[str]


# ==================== SESIONES ====================


class SessionInfo(BaseModel):
    """Información de una sesión"""

    id: UUID
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    device_info: Optional[Dict[str, Any]] = None
    location: Optional[str] = None
    activa: bool
    created_at: datetime
    last_activity_at: datetime
    expires_at: datetime
    is_current: bool = False

    class Config:
        from_attributes = True


class SessionListResponse(BaseModel):
    """Lista de sesiones de un usuario"""

    sessions: List[SessionInfo]
    total: int
    active_count: int


class SessionStatistics(BaseModel):
    """Estadísticas de sesiones"""

    total_sessions: int
    active_sessions: int
    last_activity: Optional[str] = None
    max_concurrent_sessions: int


# ==================== PERMISOS Y ROLES ====================


class PermissionBase(BaseModel):
    """Base para permisos"""

    nombre: str
    codigo: str
    descripcion: Optional[str] = None
    modulo: str
    recurso: str
    accion: str


class PermissionCreate(PermissionBase):
    """Crear permiso"""

    pass


class PermissionResponse(PermissionBase):
    """Respuesta de permiso"""

    id: UUID
    activo: bool
    created_at: datetime

    class Config:
        from_attributes = True


class RoleBase(BaseModel):
    """Base para roles"""

    nombre: str
    codigo: str
    descripcion: Optional[str] = None
    nivel: int = 0


class RoleCreate(RoleBase):
    """Crear rol"""

    rol_padre_id: Optional[UUID] = None


class RoleResponse(RoleBase):
    """Respuesta de rol"""

    id: UUID
    activo: bool
    es_sistema: bool
    created_at: datetime
    permisos_count: int = 0

    class Config:
        from_attributes = True


class RoleWithPermissions(RoleResponse):
    """Rol con sus permisos"""

    permisos: List[PermissionResponse]


class AssignPermissionRequest(BaseModel):
    """Asignar permiso a rol"""

    permission_id: UUID


class AssignRoleRequest(BaseModel):
    """Asignar rol a usuario"""

    role_id: UUID


class UserPermissionsResponse(BaseModel):
    """Permisos de un usuario"""

    usuario_id: UUID
    roles: List[RoleResponse]
    permissions: List[str]


# ==================== AUDITORÍA ====================


class AuditLogResponse(BaseModel):
    """Respuesta de log de auditoría"""

    id: UUID
    usuario_id: Optional[UUID] = None
    accion: str
    recurso: str
    recurso_id: Optional[str] = None
    descripcion: Optional[str] = None
    ip_address: Optional[str] = None
    metodo_http: Optional[str] = None
    endpoint: Optional[str] = None
    exitoso: bool
    codigo_estado: Optional[int] = None
    mensaje_error: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class AuditLogListResponse(BaseModel):
    """Lista de logs de auditoría"""

    logs: List[AuditLogResponse]
    total: int


class AuditStatistics(BaseModel):
    """Estadísticas de auditoría"""

    total_acciones: int
    acciones_exitosas: int
    acciones_fallidas: int
    tasa_exito: float
    por_accion: Dict[str, int]
    por_recurso: Dict[str, int]
    usuarios_activos: List[Dict[str, Any]]


# ==================== SSO ====================


class SSOProviderBase(BaseModel):
    """Base para proveedores SSO"""

    nombre: str
    tipo: str = Field(description="oauth2, saml, oidc")
    client_id: str
    client_secret: str
    authorization_endpoint: Optional[str] = None
    token_endpoint: Optional[str] = None
    userinfo_endpoint: Optional[str] = None
    redirect_uri: str


class SSOProviderCreate(SSOProviderBase):
    """Crear proveedor SSO"""

    scopes: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


class SSOProviderResponse(BaseModel):
    """Respuesta de proveedor SSO"""

    id: UUID
    nombre: str
    tipo: str
    activo: bool
    created_at: datetime

    class Config:
        from_attributes = True


class SSOLoginRequest(BaseModel):
    """Request para login SSO"""

    provider_id: UUID
    code: str
    state: Optional[str] = None


class SSOConnectionResponse(BaseModel):
    """Conexión SSO de usuario"""

    id: UUID
    provider_id: UUID
    provider_name: str
    external_email: Optional[str] = None
    last_login_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ==================== ENCRIPTACIÓN ====================


class EncryptRequest(BaseModel):
    """Request para encriptar datos"""

    data: str


class EncryptResponse(BaseModel):
    """Respuesta de encriptación"""

    encrypted_data: str


class DecryptRequest(BaseModel):
    """Request para desencriptar datos"""

    encrypted_data: str


class DecryptResponse(BaseModel):
    """Respuesta de desencriptación"""

    data: str


# ==================== SEGURIDAD GENERAL ====================


class SecurityDashboard(BaseModel):
    """Dashboard de seguridad"""

    two_factor_enabled: bool
    active_sessions: int
    total_sessions: int
    roles: List[str]
    permissions_count: int
    last_login: Optional[datetime] = None
    failed_login_attempts: int = 0
    account_locked: bool = False


class SecuritySettings(BaseModel):
    """Configuración de seguridad"""

    two_factor_enabled: bool
    session_timeout_hours: int
    max_concurrent_sessions: int
    password_expiry_days: int
    require_password_change: bool


class PasswordChangeRequest(BaseModel):
    """Cambio de contraseña"""

    current_password: str
    new_password: str = Field(min_length=8)
    confirm_password: str


class SecurityEventResponse(BaseModel):
    """Evento de seguridad"""

    tipo: str
    descripcion: str
    severidad: str = Field(description="low, medium, high, critical")
    timestamp: datetime
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
