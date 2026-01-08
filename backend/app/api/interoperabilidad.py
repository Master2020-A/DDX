"""
API Endpoints para Interoperabilidad HL7 FHIR
Red Nacional de Salud e Intercambio de Expedientes
"""

from datetime import datetime, timedelta
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.usuario import Usuario
from app.models.interoperabilidad import (
    InstitucionExterna,
    SolicitudIntercambio,
    HistoriaClinicaUnificada,
    ConsentimientoIntercambio,
    LogIntercambio,
    MapeoCodigos,
    TipoIntercambio,
    EstadoIntercambio,
    ProtocoloIntercambio,
)
from app.schemas.interoperabilidad import (
    InstitucionExternaCreate,
    InstitucionExternaUpdate,
    InstitucionExternaResponse,
    SolicitudIntercambioCreate,
    SolicitudIntercambioUpdate,
    SolicitudIntercambioResponse,
    HistoriaClinicaUnificadaResponse,
    ConsentimientoIntercambioCreate,
    ConsentimientoIntercambioUpdate,
    ConsentimientoIntercambioResponse,
    MapeoCodigosCreate,
    MapeoCodigosResponse,
    ExpedienteCompletoFHIR,
    EstadisticasIntercambio,
)
from app.services.intercambio_expedientes import ServicioIntercambioExpedientes
from app.services.metricas_interoperabilidad import MetricasInteroperabilidadService
from app.services.notificaciones_interoperabilidad import (
    NotificacionesInteroperabilidadService,
)
from app.models.notificacion_interoperabilidad import (
    TipoNotificacion,
    PrioridadNotificacion,
)
from app.services.webhook_service import WebhookService
from app.schemas.webhook import (
    WebhookSuscripcionCreate,
    WebhookSuscripcionUpdate,
    WebhookSuscripcionResponse,
    WebhookEntregaResponse,
)

router = APIRouter(tags=["Interoperabilidad"])


# ==================== INSTITUCIONES EXTERNAS ====================


@router.post("/instituciones-externas/", response_model=InstitucionExternaResponse)
async def crear_institucion_externa(
    institucion: InstitucionExternaCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Registra una nueva institución externa en la red de salud"""
    nueva_institucion = InstitucionExterna(**institucion.dict())
    db.add(nueva_institucion)
    await db.commit()
    await db.refresh(nueva_institucion)
    return nueva_institucion


@router.get("/instituciones-externas/", response_model=List[InstitucionExternaResponse])
async def listar_instituciones_externas(
    skip: int = 0,
    limit: int = 100,
    activa: Optional[bool] = None,
    nivel: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Lista todas las instituciones externas registradas"""
    query = select(InstitucionExterna)

    if activa is not None:
        query = query.where(InstitucionExterna.activa == activa)

    if nivel:
        query = query.where(InstitucionExterna.nivel_atencion == nivel)

    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.get(
    "/instituciones-externas/{institucion_id}",
    response_model=InstitucionExternaResponse,
)
async def obtener_institucion_externa(
    institucion_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Obtiene los detalles de una institución externa"""
    result = await db.execute(
        select(InstitucionExterna).where(InstitucionExterna.id == institucion_id)
    )
    institucion = result.scalar_one_or_none()

    if not institucion:
        raise HTTPException(status_code=404, detail="Institución no encontrada")

    return institucion


@router.put(
    "/instituciones-externas/{institucion_id}",
    response_model=InstitucionExternaResponse,
)
async def actualizar_institucion_externa(
    institucion_id: UUID,
    institucion_update: InstitucionExternaUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Actualiza la información de una institución externa"""
    result = await db.execute(
        select(InstitucionExterna).where(InstitucionExterna.id == institucion_id)
    )
    institucion = result.scalar_one_or_none()

    if not institucion:
        raise HTTPException(status_code=404, detail="Institución no encontrada")

    for key, value in institucion_update.dict(exclude_unset=True).items():
        setattr(institucion, key, value)

    institucion.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(institucion)
    return institucion


# ==================== SOLICITUDES DE INTERCAMBIO ====================


@router.post("/solicitudes/", response_model=SolicitudIntercambioResponse)
async def crear_solicitud_intercambio(
    solicitud: SolicitudIntercambioCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Crea una nueva solicitud de intercambio de información"""
    servicio = ServicioIntercambioExpedientes(db)

    # Verificar consentimiento del paciente
    tiene_consentimiento = await servicio.verificar_consentimiento(
        solicitud.paciente_id,
        solicitud.institucion_destino_id,
        solicitud.tipo_intercambio.value,
    )

    if not tiene_consentimiento:
        raise HTTPException(
            status_code=403,
            detail="El paciente no ha autorizado compartir esta información con la institución destino",
        )

    nueva_solicitud = SolicitudIntercambio(
        **solicitud.dict(),
        solicitante_id=current_user.id,
        estado=EstadoIntercambio.PENDIENTE,
    )

    db.add(nueva_solicitud)
    await db.commit()
    await db.refresh(nueva_solicitud)

    # Registrar log
    await servicio.registrar_log_intercambio(
        solicitud_id=nueva_solicitud.id,
        accion="SOLICITUD_CREADA",
        protocolo=solicitud.protocolo.value,
        direccion="SALIDA",
        usuario_id=current_user.id,
    )

    return nueva_solicitud


@router.get("/solicitudes/", response_model=List[SolicitudIntercambioResponse])
async def listar_solicitudes_intercambio(
    skip: int = 0,
    limit: int = 100,
    estado: Optional[EstadoIntercambio] = None,
    tipo: Optional[TipoIntercambio] = None,
    paciente_id: Optional[UUID] = None,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Lista las solicitudes de intercambio"""
    query = select(SolicitudIntercambio)

    if estado:
        query = query.where(SolicitudIntercambio.estado == estado)

    if tipo:
        query = query.where(SolicitudIntercambio.tipo_intercambio == tipo)

    if paciente_id:
        query = query.where(SolicitudIntercambio.paciente_id == paciente_id)

    query = (
        query.order_by(desc(SolicitudIntercambio.created_at)).offset(skip).limit(limit)
    )
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/solicitudes/{solicitud_id}", response_model=SolicitudIntercambioResponse)
async def obtener_solicitud_intercambio(
    solicitud_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Obtiene los detalles de una solicitud de intercambio"""
    result = await db.execute(
        select(SolicitudIntercambio).where(SolicitudIntercambio.id == solicitud_id)
    )
    solicitud = result.scalar_one_or_none()

    if not solicitud:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")

    return solicitud


@router.put(
    "/solicitudes/{solicitud_id}/aprobar", response_model=SolicitudIntercambioResponse
)
async def aprobar_solicitud_intercambio(
    solicitud_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Aprueba una solicitud de intercambio"""
    result = await db.execute(
        select(SolicitudIntercambio).where(SolicitudIntercambio.id == solicitud_id)
    )
    solicitud = result.scalar_one_or_none()

    if not solicitud:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")

    if solicitud.estado != EstadoIntercambio.PENDIENTE:
        raise HTTPException(status_code=400, detail="La solicitud ya fue procesada")

    solicitud.estado = EstadoIntercambio.APROBADA
    solicitud.aprobador_id = current_user.id
    solicitud.fecha_aprobacion = datetime.utcnow()
    solicitud.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(solicitud)

    # Registrar log
    servicio = ServicioIntercambioExpedientes(db)
    await servicio.registrar_log_intercambio(
        solicitud_id=solicitud.id,
        accion="SOLICITUD_APROBADA",
        protocolo=solicitud.protocolo.value,
        direccion="SALIDA",
        usuario_id=current_user.id,
    )

    return solicitud


@router.put(
    "/solicitudes/{solicitud_id}/rechazar", response_model=SolicitudIntercambioResponse
)
async def rechazar_solicitud_intercambio(
    solicitud_id: UUID,
    motivo: str = Query(..., description="Motivo del rechazo"),
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Rechaza una solicitud de intercambio"""
    result = await db.execute(
        select(SolicitudIntercambio).where(SolicitudIntercambio.id == solicitud_id)
    )
    solicitud = result.scalar_one_or_none()

    if not solicitud:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")

    if solicitud.estado != EstadoIntercambio.PENDIENTE:
        raise HTTPException(status_code=400, detail="La solicitud ya fue procesada")

    solicitud.estado = EstadoIntercambio.RECHAZADA
    solicitud.aprobador_id = current_user.id
    solicitud.motivo_rechazo = motivo
    solicitud.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(solicitud)

    # Registrar log
    servicio = ServicioIntercambioExpedientes(db)
    await servicio.registrar_log_intercambio(
        solicitud_id=solicitud.id,
        accion="SOLICITUD_RECHAZADA",
        protocolo=solicitud.protocolo.value,
        direccion="SALIDA",
        error=motivo,
        usuario_id=current_user.id,
    )

    return solicitud


@router.post(
    "/solicitudes/{solicitud_id}/generar-expediente",
    response_model=ExpedienteCompletoFHIR,
)
async def generar_expediente_fhir(
    solicitud_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Genera el expediente completo en formato FHIR para una solicitud aprobada"""
    result = await db.execute(
        select(SolicitudIntercambio).where(SolicitudIntercambio.id == solicitud_id)
    )
    solicitud = result.scalar_one_or_none()

    if not solicitud:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")

    if solicitud.estado != EstadoIntercambio.APROBADA:
        raise HTTPException(status_code=400, detail="La solicitud debe estar aprobada")

    servicio = ServicioIntercambioExpedientes(db)

    # Generar expediente FHIR
    inicio = datetime.utcnow()
    bundle_fhir = await servicio.generar_expediente_fhir(
        paciente_id=solicitud.paciente_id,
        incluir_consultas=True,
        incluir_laboratorios=True,
        incluir_imagenes=True,
        periodo_inicio=solicitud.periodo_inicio,
        periodo_fin=solicitud.periodo_fin,
    )
    tiempo_ms = int((datetime.utcnow() - inicio).total_seconds() * 1000)

    # Generar checksum
    checksum = await servicio.generar_checksum(bundle_fhir)

    # Actualizar solicitud
    solicitud.estado = EstadoIntercambio.COMPLETADA
    solicitud.fecha_completado = datetime.utcnow()
    solicitud.datos_enviados = bundle_fhir
    solicitud.checksum_datos = checksum
    solicitud.updated_at = datetime.utcnow()

    await db.commit()

    # Registrar log
    await servicio.registrar_log_intercambio(
        solicitud_id=solicitud.id,
        accion="EXPEDIENTE_GENERADO",
        protocolo=solicitud.protocolo.value,
        direccion="SALIDA",
        codigo_respuesta=200,
        tiempo_respuesta_ms=tiempo_ms,
        usuario_id=current_user.id,
    )

    return ExpedienteCompletoFHIR(
        bundle=bundle_fhir,
        checksum=checksum,
        fecha_generacion=datetime.utcnow(),
        solicitud_id=solicitud.id,
    )


# ==================== HISTORIA CLÍNICA UNIFICADA ====================


@router.get(
    "/historia-unificada/{paciente_id}", response_model=HistoriaClinicaUnificadaResponse
)
async def obtener_historia_unificada(
    paciente_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Obtiene la historia clínica unificada de un paciente"""
    result = await db.execute(
        select(HistoriaClinicaUnificada).where(
            HistoriaClinicaUnificada.paciente_id == paciente_id
        )
    )
    historia = result.scalar_one_or_none()

    if not historia:
        raise HTTPException(
            status_code=404, detail="Historia clínica unificada no encontrada"
        )

    return historia


@router.post("/historia-unificada/{paciente_id}/consolidar")
async def consolidar_datos_externos(
    paciente_id: UUID,
    datos_externos: dict,
    institucion_origen: str,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Consolida datos externos en la historia clínica unificada"""
    servicio = ServicioIntercambioExpedientes(db)

    await servicio.consolidar_historia_clinica(
        paciente_id=paciente_id,
        datos_externos=datos_externos,
        institucion_origen=institucion_origen,
    )

    return {"message": "Datos consolidados exitosamente"}


# ==================== CONSENTIMIENTOS ====================


@router.post("/consentimientos/", response_model=ConsentimientoIntercambioResponse)
async def crear_consentimiento(
    consentimiento: ConsentimientoIntercambioCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Registra el consentimiento de un paciente para compartir información"""
    nuevo_consentimiento = ConsentimientoIntercambio(**consentimiento.dict())
    db.add(nuevo_consentimiento)
    await db.commit()
    await db.refresh(nuevo_consentimiento)
    return nuevo_consentimiento


@router.get(
    "/consentimientos/paciente/{paciente_id}",
    response_model=List[ConsentimientoIntercambioResponse],
)
async def listar_consentimientos_paciente(
    paciente_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Lista los consentimientos de un paciente"""
    result = await db.execute(
        select(ConsentimientoIntercambio)
        .where(ConsentimientoIntercambio.paciente_id == paciente_id)
        .order_by(desc(ConsentimientoIntercambio.created_at))
    )
    return result.scalars().all()


@router.put(
    "/consentimientos/{consentimiento_id}/revocar",
    response_model=ConsentimientoIntercambioResponse,
)
async def revocar_consentimiento(
    consentimiento_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Revoca un consentimiento"""
    result = await db.execute(
        select(ConsentimientoIntercambio).where(
            ConsentimientoIntercambio.id == consentimiento_id
        )
    )
    consentimiento = result.scalar_one_or_none()

    if not consentimiento:
        raise HTTPException(status_code=404, detail="Consentimiento no encontrado")

    consentimiento.revocado = True
    consentimiento.fecha_revocacion = datetime.utcnow()
    consentimiento.activo = False
    consentimiento.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(consentimiento)
    return consentimiento


# ==================== MAPEO DE CÓDIGOS ====================


@router.post("/mapeo-codigos/", response_model=MapeoCodigosResponse)
async def crear_mapeo_codigo(
    mapeo: MapeoCodigosCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Crea un mapeo entre códigos de diferentes sistemas"""
    nuevo_mapeo = MapeoCodigos(**mapeo.dict())
    db.add(nuevo_mapeo)
    await db.commit()
    await db.refresh(nuevo_mapeo)
    return nuevo_mapeo


@router.get("/mapeo-codigos/", response_model=List[MapeoCodigosResponse])
async def listar_mapeos_codigos(
    sistema_origen: Optional[str] = None,
    sistema_destino: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Lista los mapeos de códigos"""
    query = select(MapeoCodigos)

    if sistema_origen:
        query = query.where(MapeoCodigos.sistema_origen == sistema_origen)

    if sistema_destino:
        query = query.where(MapeoCodigos.sistema_destino == sistema_destino)

    result = await db.execute(query)
    return result.scalars().all()


# ==================== ESTADÍSTICAS ====================


@router.get("/estadisticas/", response_model=EstadisticasIntercambio)
async def obtener_estadisticas_intercambio(
    dias: int = Query(30, description="Número de días para el reporte"),
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Obtiene estadísticas del sistema de intercambio"""
    fecha_inicio = datetime.utcnow() - timedelta(days=dias)

    # Total de solicitudes
    result = await db.execute(
        select(func.count(SolicitudIntercambio.id)).where(
            SolicitudIntercambio.created_at >= fecha_inicio
        )
    )
    total_solicitudes = result.scalar() or 0

    # Solicitudes por estado
    result = await db.execute(
        select(SolicitudIntercambio.estado, func.count(SolicitudIntercambio.id))
        .where(SolicitudIntercambio.created_at >= fecha_inicio)
        .group_by(SolicitudIntercambio.estado)
    )
    por_estado = {estado.value: count for estado, count in result.all()}

    # Solicitudes por tipo
    result = await db.execute(
        select(
            SolicitudIntercambio.tipo_intercambio, func.count(SolicitudIntercambio.id)
        )
        .where(SolicitudIntercambio.created_at >= fecha_inicio)
        .group_by(SolicitudIntercambio.tipo_intercambio)
    )
    por_tipo = {tipo.value: count for tipo, count in result.all()}

    # Instituciones activas
    result = await db.execute(
        select(func.count(InstitucionExterna.id)).where(
            InstitucionExterna.activa == True
        )
    )
    instituciones_activas = result.scalar() or 0

    # Pacientes con consentimiento
    result = await db.execute(
        select(func.count(func.distinct(ConsentimientoIntercambio.paciente_id))).where(
            and_(
                ConsentimientoIntercambio.activo == True,
                ConsentimientoIntercambio.revocado == False,
            )
        )
    )
    pacientes_con_consentimiento = result.scalar() or 0

    return EstadisticasIntercambio(
        total_solicitudes=total_solicitudes,
        solicitudes_por_estado=por_estado,
        solicitudes_por_tipo=por_tipo,
        instituciones_activas=instituciones_activas,
        pacientes_con_consentimiento=pacientes_con_consentimiento,
        periodo_dias=dias,
    )


# ==================== LOGS DE AUDITORÍA ====================


@router.get("/logs/solicitud/{solicitud_id}")
async def obtener_logs_solicitud(
    solicitud_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Obtiene los logs de auditoría de una solicitud"""
    result = await db.execute(
        select(LogIntercambio)
        .where(LogIntercambio.solicitud_id == solicitud_id)
        .order_by(LogIntercambio.timestamp)
    )
    return result.scalars().all()


# ==================== MÉTRICAS EN TIEMPO REAL ====================


@router.get("/metricas/tiempo-real")
async def obtener_metricas_tiempo_real(
    periodo_dias: int = Query(
        7, ge=1, le=90, description="Días hacia atrás para calcular métricas"
    ),
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Obtiene métricas en tiempo real del sistema de interoperabilidad

    Incluye:
    - Métricas de solicitudes (total, por estado, por prioridad, tiempos)
    - Métricas de instituciones (activas, por nivel, por tipo)
    - Métricas de rendimiento (solicitudes por día, disponibilidad)
    - Métricas de seguridad (consentimientos, auditoría)
    - Métricas de volumen (historias, bundles FHIR, datos transferidos)
    """
    metricas = await MetricasInteroperabilidadService.obtener_metricas_tiempo_real(
        db, periodo_dias
    )
    return metricas


@router.get("/metricas/alertas")
async def obtener_alertas_sistema(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Obtiene alertas del sistema que requieren atención

    Incluye:
    - Solicitudes pendientes antiguas
    - Instituciones inactivas
    - Consentimientos próximos a expirar
    - Solicitudes con errores
    """
    alertas = await MetricasInteroperabilidadService.obtener_alertas_sistema(db)
    return {"alertas": alertas, "total": len(alertas)}


# ==================== NOTIFICACIONES ====================


@router.get("/notificaciones/")
async def obtener_notificaciones(
    solo_no_leidas: bool = Query(False, description="Solo notificaciones no leídas"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Obtiene las notificaciones del usuario actual
    """
    notificaciones = (
        await NotificacionesInteroperabilidadService.obtener_notificaciones_usuario(
            db=db,
            usuario_id=current_user.id,
            solo_no_leidas=solo_no_leidas,
            limit=limit,
            offset=offset,
        )
    )

    return [notif.to_dict() for notif in notificaciones]


@router.get("/notificaciones/count")
async def contar_notificaciones_no_leidas(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Cuenta las notificaciones no leídas del usuario actual
    """
    count = (
        await NotificacionesInteroperabilidadService.contar_notificaciones_no_leidas(
            db=db, usuario_id=current_user.id
        )
    )

    return {"count": count}


@router.put("/notificaciones/{notificacion_id}/marcar-leida")
async def marcar_notificacion_leida(
    notificacion_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Marca una notificación como leída
    """
    notificacion = await NotificacionesInteroperabilidadService.marcar_como_leida(
        db=db, notificacion_id=notificacion_id, usuario_id=current_user.id
    )

    if not notificacion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Notificación no encontrada"
        )

    return notificacion.to_dict()


@router.put("/notificaciones/marcar-todas-leidas")
async def marcar_todas_notificaciones_leidas(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Marca todas las notificaciones del usuario como leídas
    """
    count = await NotificacionesInteroperabilidadService.marcar_todas_como_leidas(
        db=db, usuario_id=current_user.id
    )

    return {"marcadas": count}


@router.delete("/notificaciones/{notificacion_id}")
async def eliminar_notificacion(
    notificacion_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Elimina una notificación
    """
    eliminada = await NotificacionesInteroperabilidadService.eliminar_notificacion(
        db=db, notificacion_id=notificacion_id, usuario_id=current_user.id
    )

    if not eliminada:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Notificación no encontrada"
        )

    return {"mensaje": "Notificación eliminada"}


# ==================== WEBHOOKS ====================


@router.post("/webhooks/", response_model=WebhookSuscripcionResponse)
async def crear_webhook(
    webhook: WebhookSuscripcionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Crea una nueva suscripción de webhook

    Permite suscribirse a eventos del sistema de interoperabilidad
    para recibir notificaciones automáticas en una URL externa.
    """
    suscripcion = await WebhookService.crear_suscripcion(
        db=db,
        nombre=webhook.nombre,
        url=webhook.url,
        eventos=webhook.eventos,
        usuario_id=current_user.id,
        descripcion=webhook.descripcion,
        secret_key=webhook.secret_key,
        headers_adicionales=webhook.headers_adicionales,
        timeout_segundos=webhook.timeout_segundos,
        reintentos_max=webhook.reintentos_max,
        filtros=webhook.filtros,
        institucion_id=webhook.institucion_id,
    )

    return suscripcion


@router.get("/webhooks/", response_model=List[WebhookSuscripcionResponse])
async def listar_webhooks(
    activo: Optional[bool] = Query(None, description="Filtrar por estado activo"),
    evento: Optional[str] = Query(None, description="Filtrar por evento"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Lista las suscripciones de webhooks del usuario actual
    """
    suscripciones = await WebhookService.obtener_suscripciones(
        db=db,
        usuario_id=current_user.id,
        activo=activo,
        evento=evento,
        limit=limit,
        offset=offset,
    )

    return suscripciones


@router.get("/webhooks/{webhook_id}", response_model=WebhookSuscripcionResponse)
async def obtener_webhook(
    webhook_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Obtiene una suscripción de webhook por ID
    """
    suscripciones = await WebhookService.obtener_suscripciones(
        db=db, usuario_id=current_user.id, limit=1, offset=0
    )

    suscripcion = next((s for s in suscripciones if s.id == webhook_id), None)

    if not suscripcion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Webhook no encontrado"
        )

    return suscripcion


@router.put("/webhooks/{webhook_id}", response_model=WebhookSuscripcionResponse)
async def actualizar_webhook(
    webhook_id: UUID,
    webhook: WebhookSuscripcionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Actualiza una suscripción de webhook
    """
    datos = webhook.dict(exclude_unset=True)

    suscripcion = await WebhookService.actualizar_suscripcion(
        db=db, suscripcion_id=webhook_id, usuario_id=current_user.id, **datos
    )

    if not suscripcion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Webhook no encontrado"
        )

    return suscripcion


@router.delete("/webhooks/{webhook_id}")
async def eliminar_webhook(
    webhook_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Elimina una suscripción de webhook
    """
    eliminado = await WebhookService.eliminar_suscripcion(
        db=db, suscripcion_id=webhook_id, usuario_id=current_user.id
    )

    if not eliminado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Webhook no encontrado"
        )

    return {"mensaje": "Webhook eliminado exitosamente"}


@router.post("/webhooks/{webhook_id}/probar")
async def probar_webhook(
    webhook_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Envía un evento de prueba al webhook
    """
    resultado = await WebhookService.probar_webhook(
        db=db, suscripcion_id=webhook_id, usuario_id=current_user.id
    )

    if "error" in resultado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=resultado["error"]
        )

    return resultado


@router.get(
    "/webhooks/{webhook_id}/entregas", response_model=List[WebhookEntregaResponse]
)
async def listar_entregas_webhook(
    webhook_id: UUID,
    exitoso: Optional[bool] = Query(None, description="Filtrar por éxito/fallo"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Lista el historial de entregas de un webhook
    """
    # Verificar que el webhook pertenece al usuario
    suscripciones = await WebhookService.obtener_suscripciones(
        db=db, usuario_id=current_user.id, limit=1, offset=0
    )

    suscripcion = next((s for s in suscripciones if s.id == webhook_id), None)

    if not suscripcion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Webhook no encontrado"
        )

    entregas = await WebhookService.obtener_entregas(
        db=db, suscripcion_id=webhook_id, exitoso=exitoso, limit=limit, offset=offset
    )

    return entregas


@router.get("/webhooks/eventos/disponibles")
async def listar_eventos_disponibles(
    current_user: Usuario = Depends(get_current_user),
):
    """
    Lista todos los eventos disponibles para suscripción
    """
    from app.models.webhook_interoperabilidad import EventoWebhook

    eventos = [
        {
            "evento": evento.value,
            "descripcion": _obtener_descripcion_evento(evento.value),
        }
        for evento in EventoWebhook
    ]

    return {"eventos": eventos}


def _obtener_descripcion_evento(evento: str) -> str:
    """Obtiene la descripción de un evento"""
    descripciones = {
        "solicitud.creada": "Se crea una nueva solicitud de intercambio",
        "solicitud.aprobada": "Una solicitud es aprobada",
        "solicitud.rechazada": "Una solicitud es rechazada",
        "solicitud.completada": "Una solicitud se completa exitosamente",
        "solicitud.error": "Ocurre un error en una solicitud",
        "institucion.creada": "Se registra una nueva institución",
        "institucion.actualizada": "Se actualiza una institución",
        "institucion.desactivada": "Una institución es desactivada",
        "consentimiento.creado": "Se crea un nuevo consentimiento",
        "consentimiento.revocado": "Un consentimiento es revocado",
        "consentimiento.expirando": "Un consentimiento está próximo a expirar",
        "bundle.generado": "Se genera un bundle FHIR",
        "historia.creada": "Se crea una historia clínica unificada",
    }
    return descripciones.get(evento, "Sin descripción")
