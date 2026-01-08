from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel

from app.core.database import get_db
from app.api.dependencies import get_current_user, get_current_admin
from app.models.usuario import Usuario
from app.models.cumplimiento import (
    TipoNormativa,
    TipoConsentimiento,
    EstadoConsentimiento,
    TipoAccesoSensible,
)
from app.services.cumplimiento_service import CumplimientoService

router = APIRouter(prefix="/api/cumplimiento", tags=["Cumplimiento Normativo"])


# ==================== SCHEMAS ====================


class ConfiguracionCumplimientoCreate(BaseModel):
    normativa: TipoNormativa
    habilitado: bool = True
    configuracion: dict = {}
    requiere_autorizacion_acceso: bool = True
    requiere_log_acceso: bool = True
    dias_retencion_logs: int = 2555
    requiere_consentimiento_explicito: bool = True
    permite_portabilidad_datos: bool = True
    permite_derecho_olvido: bool = True
    dias_respuesta_solicitud: int = 30
    requiere_firma_electronica: bool = True
    requiere_expediente_electronico: bool = True
    requiere_respaldo_informacion: bool = True
    notas: Optional[str] = None


class ConsentimientoInformadoCreate(BaseModel):
    paciente_id: UUID
    tipo: TipoConsentimiento
    titulo: str
    descripcion: str
    riesgos: Optional[List[str]] = None
    beneficios: Optional[List[str]] = None
    alternativas: Optional[List[str]] = None
    consulta_id: Optional[UUID] = None


class FirmarConsentimientoRequest(BaseModel):
    contenido: str


class RevocarConsentimientoRequest(BaseModel):
    motivo: str


class LogAccesoSensibleCreate(BaseModel):
    recurso_tipo: str
    recurso_id: UUID
    tipo_acceso: TipoAccesoSensible
    accion: str
    paciente_id: Optional[UUID] = None
    descripcion: Optional[str] = None
    datos_accedidos: Optional[dict] = None
    justificacion: Optional[str] = None
    normativa_aplicable: Optional[TipoNormativa] = None


class SolicitudDatosPersonalesCreate(BaseModel):
    tipo_solicitud: str
    descripcion: str
    datos_solicitados: Optional[List[str]] = None


class ProcesarSolicitudRequest(BaseModel):
    respuesta: str
    archivo_respuesta_url: Optional[str] = None


class AuditoriaHIPAACreate(BaseModel):
    fecha_inicio: datetime
    fecha_fin: datetime


# ==================== CONFIGURACIÓN ====================


@router.get("/configuracion")
async def list_configuraciones(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_admin),
):
    """Lista todas las configuraciones de normativas (solo admin)"""
    service = CumplimientoService(db)
    configs = await service.list_configuraciones()

    return [
        {
            "id": str(c.id),
            "normativa": c.normativa,
            "habilitado": c.habilitado,
            "configuracion": c.configuracion,
            "requiere_autorizacion_acceso": c.requiere_autorizacion_acceso,
            "requiere_log_acceso": c.requiere_log_acceso,
            "dias_retencion_logs": c.dias_retencion_logs,
            "requiere_consentimiento_explicito": c.requiere_consentimiento_explicito,
            "permite_portabilidad_datos": c.permite_portabilidad_datos,
            "permite_derecho_olvido": c.permite_derecho_olvido,
            "dias_respuesta_solicitud": c.dias_respuesta_solicitud,
            "requiere_firma_electronica": c.requiere_firma_electronica,
            "requiere_expediente_electronico": c.requiere_expediente_electronico,
            "requiere_respaldo_informacion": c.requiere_respaldo_informacion,
            "notas": c.notas,
            "created_at": c.created_at.isoformat() if c.created_at else None,
            "updated_at": c.updated_at.isoformat() if c.updated_at else None,
        }
        for c in configs
    ]


@router.post("/configuracion")
async def create_configuracion(
    data: ConfiguracionCumplimientoCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_admin),
):
    """Crea o actualiza configuración de normativa (solo admin)"""
    service = CumplimientoService(db)

    config = await service.create_configuracion(
        normativa=data.normativa,
        configuracion=data.configuracion,
        habilitado=data.habilitado,
        requiere_autorizacion_acceso=data.requiere_autorizacion_acceso,
        requiere_log_acceso=data.requiere_log_acceso,
        dias_retencion_logs=data.dias_retencion_logs,
        requiere_consentimiento_explicito=data.requiere_consentimiento_explicito,
        permite_portabilidad_datos=data.permite_portabilidad_datos,
        permite_derecho_olvido=data.permite_derecho_olvido,
        dias_respuesta_solicitud=data.dias_respuesta_solicitud,
        requiere_firma_electronica=data.requiere_firma_electronica,
        requiere_expediente_electronico=data.requiere_expediente_electronico,
        requiere_respaldo_informacion=data.requiere_respaldo_informacion,
        notas=data.notas,
    )

    return {
        "id": str(config.id),
        "normativa": config.normativa,
        "habilitado": config.habilitado,
        "message": "Configuración guardada exitosamente",
    }


@router.get("/configuracion/{normativa}")
async def get_configuracion(
    normativa: TipoNormativa,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Obtiene la configuración de una normativa específica"""
    service = CumplimientoService(db)
    config = await service.get_configuracion(normativa)

    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Configuración para {normativa} no encontrada",
        )

    return {
        "id": str(config.id),
        "normativa": config.normativa,
        "habilitado": config.habilitado,
        "configuracion": config.configuracion,
        "requiere_autorizacion_acceso": config.requiere_autorizacion_acceso,
        "requiere_log_acceso": config.requiere_log_acceso,
        "dias_retencion_logs": config.dias_retencion_logs,
        "requiere_consentimiento_explicito": config.requiere_consentimiento_explicito,
        "permite_portabilidad_datos": config.permite_portabilidad_datos,
        "permite_derecho_olvido": config.permite_derecho_olvido,
        "dias_respuesta_solicitud": config.dias_respuesta_solicitud,
        "requiere_firma_electronica": config.requiere_firma_electronica,
        "requiere_expediente_electronico": config.requiere_expediente_electronico,
        "requiere_respaldo_informacion": config.requiere_respaldo_informacion,
        "notas": config.notas,
    }


# ==================== CONSENTIMIENTOS INFORMADOS ====================


@router.post("/consentimientos")
async def crear_consentimiento(
    data: ConsentimientoInformadoCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Crea un consentimiento informado"""
    service = CumplimientoService(db)

    consentimiento = await service.crear_consentimiento(
        paciente_id=data.paciente_id,
        medico_id=current_user.id,
        tipo=data.tipo,
        titulo=data.titulo,
        descripcion=data.descripcion,
        riesgos=data.riesgos,
        beneficios=data.beneficios,
        alternativas=data.alternativas,
        consulta_id=data.consulta_id,
    )

    return {
        "id": str(consentimiento.id),
        "paciente_id": str(consentimiento.paciente_id),
        "tipo": consentimiento.tipo,
        "estado": consentimiento.estado,
        "titulo": consentimiento.titulo,
        "created_at": consentimiento.created_at.isoformat(),
    }


@router.post("/consentimientos/{consentimiento_id}/firmar-paciente")
async def firmar_consentimiento_paciente(
    consentimiento_id: UUID,
    data: FirmarConsentimientoRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Firma un consentimiento por parte del paciente"""
    service = CumplimientoService(db)

    try:
        consentimiento = await service.firmar_consentimiento_paciente(
            consentimiento_id=consentimiento_id,
            contenido=data.contenido,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
        )

        return {
            "id": str(consentimiento.id),
            "estado": consentimiento.estado,
            "fecha_firma_paciente": (
                consentimiento.fecha_firma_paciente.isoformat()
                if consentimiento.fecha_firma_paciente
                else None
            ),
            "message": "Consentimiento firmado exitosamente",
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/consentimientos/{consentimiento_id}/firmar-medico")
async def firmar_consentimiento_medico(
    consentimiento_id: UUID,
    data: FirmarConsentimientoRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Firma un consentimiento por parte del médico"""
    service = CumplimientoService(db)

    try:
        consentimiento = await service.firmar_consentimiento_medico(
            consentimiento_id=consentimiento_id,
            contenido=data.contenido,
            ip_address=request.client.host if request.client else None,
        )

        return {
            "id": str(consentimiento.id),
            "fecha_firma_medico": (
                consentimiento.fecha_firma_medico.isoformat()
                if consentimiento.fecha_firma_medico
                else None
            ),
            "message": "Consentimiento firmado por médico exitosamente",
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/consentimientos/{consentimiento_id}/revocar")
async def revocar_consentimiento(
    consentimiento_id: UUID,
    data: RevocarConsentimientoRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Revoca un consentimiento informado"""
    service = CumplimientoService(db)

    consentimiento = await service.revocar_consentimiento(
        consentimiento_id=consentimiento_id,
        motivo=data.motivo,
    )

    return {
        "id": str(consentimiento.id),
        "estado": consentimiento.estado,
        "fecha_revocacion": (
            consentimiento.fecha_revocacion.isoformat()
            if consentimiento.fecha_revocacion
            else None
        ),
        "message": "Consentimiento revocado exitosamente",
    }


@router.get("/consentimientos/paciente/{paciente_id}")
async def get_consentimientos_paciente(
    paciente_id: UUID,
    tipo: Optional[TipoConsentimiento] = None,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Obtiene los consentimientos de un paciente"""
    service = CumplimientoService(db)
    consentimientos = await service.get_consentimientos_paciente(paciente_id, tipo)

    return [
        {
            "id": str(c.id),
            "tipo": c.tipo,
            "estado": c.estado,
            "titulo": c.titulo,
            "descripcion": c.descripcion,
            "riesgos": c.riesgos,
            "beneficios": c.beneficios,
            "alternativas": c.alternativas,
            "fecha_firma_paciente": (
                c.fecha_firma_paciente.isoformat() if c.fecha_firma_paciente else None
            ),
            "fecha_firma_medico": (
                c.fecha_firma_medico.isoformat() if c.fecha_firma_medico else None
            ),
            "created_at": c.created_at.isoformat(),
        }
        for c in consentimientos
    ]


# ==================== LOGS DE ACCESO SENSIBLE ====================


@router.post("/logs-acceso")
async def registrar_acceso_sensible(
    data: LogAccesoSensibleCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Registra un acceso a información sensible (HIPAA)"""
    service = CumplimientoService(db)

    log = await service.registrar_acceso_sensible(
        usuario_id=current_user.id,
        recurso_tipo=data.recurso_tipo,
        recurso_id=data.recurso_id,
        tipo_acceso=data.tipo_acceso,
        accion=data.accion,
        paciente_id=data.paciente_id,
        descripcion=data.descripcion,
        datos_accedidos=data.datos_accedidos,
        justificacion=data.justificacion,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        endpoint=str(request.url),
        metodo_http=request.method,
        normativa_aplicable=data.normativa_aplicable,
    )

    return {
        "id": str(log.id),
        "message": "Acceso registrado exitosamente",
    }


@router.get("/logs-acceso/paciente/{paciente_id}")
async def get_logs_acceso_paciente(
    paciente_id: UUID,
    fecha_inicio: Optional[datetime] = None,
    fecha_fin: Optional[datetime] = None,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Obtiene los logs de acceso a información de un paciente"""
    service = CumplimientoService(db)
    logs = await service.get_logs_acceso_paciente(
        paciente_id, fecha_inicio, fecha_fin, limit
    )

    return [
        {
            "id": str(log.id),
            "usuario_id": str(log.usuario_id),
            "recurso_tipo": log.recurso_tipo,
            "recurso_id": str(log.recurso_id),
            "tipo_acceso": log.tipo_acceso,
            "accion": log.accion,
            "descripcion": log.descripcion,
            "justificacion": log.justificacion,
            "autorizado": log.autorizado,
            "ip_address": log.ip_address,
            "created_at": log.created_at.isoformat(),
        }
        for log in logs
    ]


@router.get("/logs-acceso/usuario/{usuario_id}")
async def get_logs_acceso_usuario(
    usuario_id: UUID,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_admin),
):
    """Obtiene los logs de acceso de un usuario (solo admin)"""
    service = CumplimientoService(db)
    logs = await service.get_logs_acceso_usuario(usuario_id, limit)

    return [
        {
            "id": str(log.id),
            "recurso_tipo": log.recurso_tipo,
            "recurso_id": str(log.recurso_id),
            "paciente_id": str(log.paciente_id) if log.paciente_id else None,
            "tipo_acceso": log.tipo_acceso,
            "accion": log.accion,
            "descripcion": log.descripcion,
            "autorizado": log.autorizado,
            "created_at": log.created_at.isoformat(),
        }
        for log in logs
    ]


# ==================== SOLICITUDES DATOS PERSONALES (GDPR) ====================


@router.post("/solicitudes-datos")
async def crear_solicitud_datos(
    data: SolicitudDatosPersonalesCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Crea una solicitud de datos personales (GDPR)"""
    service = CumplimientoService(db)

    # Asumimos que el usuario actual es un paciente o tiene acceso a su paciente_id
    # En producción, deberías obtener el paciente_id del usuario actual
    solicitud = await service.crear_solicitud_datos(
        paciente_id=current_user.id,  # Ajustar según tu lógica
        tipo_solicitud=data.tipo_solicitud,
        descripcion=data.descripcion,
        datos_solicitados=data.datos_solicitados,
    )

    return {
        "id": str(solicitud.id),
        "tipo_solicitud": solicitud.tipo_solicitud,
        "estado": solicitud.estado,
        "fecha_limite": solicitud.fecha_limite.isoformat(),
        "created_at": solicitud.created_at.isoformat(),
    }


@router.post("/solicitudes-datos/{solicitud_id}/procesar")
async def procesar_solicitud_datos(
    solicitud_id: UUID,
    data: ProcesarSolicitudRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_admin),
):
    """Procesa una solicitud de datos personales (solo admin)"""
    service = CumplimientoService(db)

    solicitud = await service.procesar_solicitud_datos(
        solicitud_id=solicitud_id,
        procesado_por_id=current_user.id,
        respuesta=data.respuesta,
        archivo_respuesta_url=data.archivo_respuesta_url,
    )

    return {
        "id": str(solicitud.id),
        "estado": solicitud.estado,
        "fecha_respuesta": (
            solicitud.fecha_respuesta.isoformat() if solicitud.fecha_respuesta else None
        ),
        "message": "Solicitud procesada exitosamente",
    }


@router.get("/solicitudes-datos/pendientes")
async def get_solicitudes_pendientes(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_admin),
):
    """Obtiene solicitudes pendientes de procesar (solo admin)"""
    service = CumplimientoService(db)
    solicitudes = await service.get_solicitudes_pendientes()

    return [
        {
            "id": str(s.id),
            "paciente_id": str(s.paciente_id),
            "tipo_solicitud": s.tipo_solicitud,
            "descripcion": s.descripcion,
            "estado": s.estado,
            "fecha_limite": s.fecha_limite.isoformat(),
            "created_at": s.created_at.isoformat(),
        }
        for s in solicitudes
    ]


# ==================== AUDITORÍA HIPAA ====================


@router.post("/auditoria-hipaa")
async def crear_auditoria_hipaa(
    data: AuditoriaHIPAACreate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_admin),
):
    """Crea una auditoría HIPAA (solo admin)"""
    service = CumplimientoService(db)

    auditoria = await service.crear_auditoria_hipaa(
        auditor_id=current_user.id,
        fecha_inicio=data.fecha_inicio,
        fecha_fin=data.fecha_fin,
    )

    return {
        "id": str(auditoria.id),
        "total_accesos": auditoria.total_accesos,
        "accesos_autorizados": auditoria.accesos_autorizados,
        "accesos_no_autorizados": auditoria.accesos_no_autorizados,
        "nivel_cumplimiento": auditoria.nivel_cumplimiento,
        "cumple_normativa": auditoria.cumple_normativa,
        "created_at": auditoria.created_at.isoformat(),
    }


@router.get("/auditoria-hipaa")
async def get_auditorias_recientes(
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_admin),
):
    """Obtiene las auditorías más recientes (solo admin)"""
    service = CumplimientoService(db)
    auditorias = await service.get_auditorias_recientes(limit)

    return [
        {
            "id": str(a.id),
            "fecha_inicio": a.fecha_inicio.isoformat(),
            "fecha_fin": a.fecha_fin.isoformat(),
            "total_accesos": a.total_accesos,
            "accesos_autorizados": a.accesos_autorizados,
            "accesos_no_autorizados": a.accesos_no_autorizados,
            "nivel_cumplimiento": a.nivel_cumplimiento,
            "cumple_normativa": a.cumple_normativa,
            "created_at": a.created_at.isoformat(),
        }
        for a in auditorias
    ]


# ==================== ESTADÍSTICAS ====================


@router.get("/estadisticas")
async def get_estadisticas_cumplimiento(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_admin),
):
    """Obtiene estadísticas generales de cumplimiento (solo admin)"""
    service = CumplimientoService(db)
    return await service.get_estadisticas_cumplimiento()
