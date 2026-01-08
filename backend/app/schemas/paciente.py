from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional, List, Union
from uuid import UUID
from datetime import datetime, date
import re

# Si sigues usando GeneroEnum en otra parte, lo puedes dejar importado.
# from app.models.paciente import GeneroEnum


class DireccionMX(BaseModel):
    codigo_postal: str = Field(..., min_length=5, max_length=5)
    pais: str = "México"
    estado: str
    municipio: str
    ciudad: Optional[str] = None
    colonia: Optional[str] = None
    calle: Optional[str] = None
    numero_exterior: Optional[str] = None
    numero_interior: Optional[str] = None

    @field_validator("codigo_postal")
    @classmethod
    def cp_solo_digitos(cls, v: str):
        v = (v or "").strip()
        if not re.fullmatch(r"\d{5}", v):
            raise ValueError("codigo_postal debe tener 5 dígitos")
        return v

    @model_validator(mode="after")
    def defaults(self):
        # Si ciudad viene vacía, usar municipio
        if not (self.ciudad and self.ciudad.strip()):
            self.ciudad = self.municipio
        return self


class TelefonoMX(BaseModel):
    pais: str = "+52"
    lada: str
    numero: str

    @field_validator("lada")
    @classmethod
    def lada_valida(cls, v: str):
        v = re.sub(r"\D", "", v or "")
        if len(v) not in (2, 3):
            raise ValueError("lada debe tener 2 o 3 dígitos")
        return v

    @field_validator("numero")
    @classmethod
    def numero_valido(cls, v: str):
        v = re.sub(r"\D", "", v or "")
        if len(v) not in (7, 8):
            raise ValueError("numero debe tener 7 u 8 dígitos")
        return v

    @model_validator(mode="after")
    def suma_10(self):
        if len(self.lada) + len(self.numero) != 10:
            raise ValueError("lada + numero deben sumar 10 dígitos")
        return self

    def e164(self) -> str:
        # +52 + lada + numero
        p = (self.pais or "+52").strip()
        if not p.startswith("+"):
            p = "+" + p
        return f"{p}{self.lada}{self.numero}"


class PacienteBase(BaseModel):
    nombre_completo: str = Field(..., min_length=1, max_length=255)
    fecha_nacimiento: date

    # Aceptamos string para tolerar valores "M", "F", etc.
    genero: Optional[str] = None
    tipo_sangre: Optional[str] = None

    # Antes era Optional[str]. Ahora acepta también objeto.
    telefono: Optional[Union[str, TelefonoMX]] = None

    # Usamos str opcional para tolerar emails viejos/vacíos en BD
    email: Optional[str] = None

    # Antes era Optional[str]. Ahora acepta también objeto.
    direccion: Optional[Union[str, DireccionMX]] = None

    contacto_emergencia_nombre: Optional[str] = None
    contacto_emergencia_telefono: Optional[Union[str, TelefonoMX]] = None

    alergias: Optional[List[str]] = []


class PacienteCreate(PacienteBase):
    pass


class PacienteUpdate(BaseModel):
    nombre_completo: Optional[str] = None
    fecha_nacimiento: Optional[date] = None
    genero: Optional[str] = None
    tipo_sangre: Optional[str] = None
    telefono: Optional[Union[str, TelefonoMX]] = None
    email: Optional[str] = None
    direccion: Optional[Union[str, DireccionMX]] = None
    contacto_emergencia_nombre: Optional[str] = None
    contacto_emergencia_telefono: Optional[Union[str, TelefonoMX]] = None
    alergias: Optional[List[str]] = None


class PacienteResponse(PacienteBase):
    id: UUID
    numero_expediente: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
