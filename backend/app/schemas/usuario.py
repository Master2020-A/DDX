from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from uuid import UUID
from datetime import datetime
from app.models.usuario import RolEnum


class UsuarioBase(BaseModel):
    email: EmailStr
    nombre_completo: str = Field(..., min_length=1, max_length=255)
    rol: RolEnum
    especialidad: Optional[str] = None
    cedula_profesional: Optional[str] = None


class UsuarioCreate(UsuarioBase):
    password: str = Field(..., min_length=8)


class UsuarioResponse(UsuarioBase):
    id: UUID
    activo: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UsuarioLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UsuarioResponse
