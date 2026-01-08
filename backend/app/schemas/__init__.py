from app.schemas.usuario import UsuarioCreate, UsuarioResponse, UsuarioLogin, Token
from app.schemas.paciente import PacienteCreate, PacienteResponse, PacienteUpdate
from app.schemas.consulta import ConsultaCreate, ConsultaResponse, ConsultaUpdate
from app.schemas.diagnostico import DiagnosticoCreate, DiagnosticoResponse
from app.schemas.prueba import PruebaMedicaCreate, PruebaMedicaResponse, ResultadoPruebaCreate
from app.schemas.tratamiento import TratamientoCreate, TratamientoResponse, PrescripcionCreate
from app.schemas.expediente import (
    ExpedienteClinicoCreate, 
    ExpedienteClinicoResponse, 
    ExpedienteClinicoUpdate,
    SignosVitalesBase
)
from app.schemas.nota_medica import (
    NotaMedicaCreate,
    NotaMedicaResponse,
    NotaMedicaUpdate
)

__all__ = [
    "UsuarioCreate",
    "UsuarioResponse",
    "UsuarioLogin",
    "Token",
    "PacienteCreate",
    "PacienteResponse",
    "PacienteUpdate",
    "ConsultaCreate",
    "ConsultaResponse",
    "ConsultaUpdate",
    "DiagnosticoCreate",
    "DiagnosticoResponse",
    "PruebaMedicaCreate",
    "PruebaMedicaResponse",
    "ResultadoPruebaCreate",
    "TratamientoCreate",
    "TratamientoResponse",
    "PrescripcionCreate",
    "ExpedienteClinicoCreate",
    "ExpedienteClinicoResponse",
    "ExpedienteClinicoUpdate",
    "SignosVitalesBase",
    "NotaMedicaCreate",
    "NotaMedicaResponse",
    "NotaMedicaUpdate",
]
