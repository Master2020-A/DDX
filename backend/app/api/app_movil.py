"""
API endpoints para el módulo de Aplicación Móvil
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc
from typing import List, Optional
from datetime import datetime, timedelta
from uuid import UUID

from app.core.database import get_db
from app.api.dependencies import get_current_user, get_current_admin
from app.models.usuario import Usuario
from app.models.app_movil import (
    DispositivoMovil,
    NotificacionPush,
    DocumentoEscaneado,
    SincronizacionOffline,
    CitaMovil,
    ConfiguracionAppMovil,
    SesionMovil,
    PlataformaMovil,
    EstadoDispositivo,
    TipoNotificacion,
    EstadoNotificacion,
    TipoDocumento,
    EstadoSincronizacion,
)
from app.schemas.app_movil import (
    DispositivoMovilCreate,
    DispositivoMovilUpdate,
    DispositivoMovilResponse,
    NotificacionPushCreate,
    NotificacionPushEnviar,
    NotificacionPushResponse,
    DocumentoEscaneadoCreate,
    DocumentoEscaneadoUpdate,
    DocumentoEscaneadoResponse,
    FirmarDocumentoRequest,
    SincronizacionOfflineCreate,
    SincronizacionOfflineResponse,
    SincronizarRequest,
    SincronizarResponse,
    CitaMovilCreate,
    CitaMovilUpdate,
    CitaMovilResponse,
    ConfiguracionAppMovilUpdate,
    ConfiguracionAppMovilResponse,
    SesionMovilCreate,
    SesionMovilResponse,
    RefreshTokenRequest,
    EstadisticasAppMovilResponse,
    EstadoSincronizacionResponse,
)

router = APIRouter(prefix="/app-movil", tags=["Aplicación Móvil"])


# ==================== DISPOSITIVOS MÓVILES ====================


@router.post(
    "/dispositivos",
    response_model=DispositivoMovilResponse,
    status_code=status.HTTP_201_CREATED,
)
async def registrar_dispositivo(
    dispositivo_data: DispositivoMovilCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Registrar un nuevo dispositivo móvil
    """
    # Verificar si el dispositivo ya existe
    result = await db.execute(
        select(DispositivoMovil).where(
            DispositivoMovil.device_id == dispositivo_data.device_id
        )
    )
    dispositivo_existente = result.scalar_one_or_none()

    if dispositivo_existente:
        # Actualizar dispositivo existente
        dispositivo_existente.usuario_id = current_user.id
        dispositivo_existente.plataforma = dispositivo_data.plataforma
        dispositivo_existente.modelo = dispositivo_data.modelo
        dispositivo_existente.version_os = dispositivo_data.version_os
        dispositivo_existente.version_app = dispositivo_data.version_app
        dispositivo_existente.push_token = dispositivo_data.push_token
        dispositivo_existente.push_token_actualizado = datetime.utcnow()
        dispositivo_existente.estado = EstadoDispositivo.ACTIVO
        dispositivo_existente.ultimo_acceso = datetime.utcnow()
        dispositivo_existente.ip_registro = dispositivo_data.ip_registro
        dispositivo_existente.user_agent = dispositivo_data.user_agent
        dispositivo_existente.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(dispositivo_existente)
        return dispositivo_existente

    # Crear nuevo dispositivo
    dispositivo = DispositivoMovil(
        usuario_id=current_user.id,
        plataforma=dispositivo_data.plataforma,
        modelo=dispositivo_data.modelo,
        version_os=dispositivo_data.version_os,
        version_app=dispositivo_data.version_app,
        device_id=dispositivo_data.device_id,
        push_token=dispositivo_data.push_token,
        push_token_actualizado=(
            datetime.utcnow() if dispositivo_data.push_token else None
        ),
        ip_registro=dispositivo_data.ip_registro,
        user_agent=dispositivo_data.user_agent,
        ultimo_acceso=datetime.utcnow(),
    )

    db.add(dispositivo)
    await db.commit()
    await db.refresh(dispositivo)

    # Crear configuración por defecto
    config = ConfiguracionAppMovil(usuario_id=current_user.id)
    db.add(config)
    await db.commit()

    return dispositivo


@router.get("/dispositivos", response_model=List[DispositivoMovilResponse])
async def listar_dispositivos(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Listar dispositivos del usuario actual
    """
    result = await db.execute(
        select(DispositivoMovil)
        .where(DispositivoMovil.usuario_id == current_user.id)
        .order_by(desc(DispositivoMovil.ultimo_acceso))
    )
    dispositivos = result.scalars().all()
    return dispositivos


@router.patch("/dispositivos/{dispositivo_id}", response_model=DispositivoMovilResponse)
async def actualizar_dispositivo(
    dispositivo_id: UUID,
    dispositivo_data: DispositivoMovilUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Actualizar configuración de dispositivo
    """
    result = await db.execute(
        select(DispositivoMovil).where(
            and_(
                DispositivoMovil.id == dispositivo_id,
                DispositivoMovil.usuario_id == current_user.id,
            )
        )
    )
    dispositivo = result.scalar_one_or_none()

    if not dispositivo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Dispositivo no encontrado"
        )

    # Actualizar campos
    if dispositivo_data.push_token is not None:
        dispositivo.push_token = dispositivo_data.push_token
        dispositivo.push_token_actualizado = datetime.utcnow()
    if dispositivo_data.version_app is not None:
        dispositivo.version_app = dispositivo_data.version_app
    if dispositivo_data.notificaciones_habilitadas is not None:
        dispositivo.notificaciones_habilitadas = (
            dispositivo_data.notificaciones_habilitadas
        )
    if dispositivo_data.biometria_habilitada is not None:
        dispositivo.biometria_habilitada = dispositivo_data.biometria_habilitada
    if dispositivo_data.sincronizacion_automatica is not None:
        dispositivo.sincronizacion_automatica = (
            dispositivo_data.sincronizacion_automatica
        )

    dispositivo.ultimo_acceso = datetime.utcnow()
    dispositivo.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(dispositivo)
    return dispositivo


@router.delete("/dispositivos/{dispositivo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def revocar_dispositivo(
    dispositivo_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Revocar un dispositivo (cerrar sesión)
    """
    result = await db.execute(
        select(DispositivoMovil).where(
            and_(
                DispositivoMovil.id == dispositivo_id,
                DispositivoMovil.usuario_id == current_user.id,
            )
        )
    )
    dispositivo = result.scalar_one_or_none()

    if not dispositivo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Dispositivo no encontrado"
        )

    dispositivo.estado = EstadoDispositivo.REVOCADO
    dispositivo.fecha_revocacion = datetime.utcnow()

    await db.commit()


# ==================== NOTIFICACIONES PUSH ====================


@router.post(
    "/notificaciones",
    response_model=NotificacionPushResponse,
    status_code=status.HTTP_201_CREATED,
)
async def crear_notificacion(
    notificacion_data: NotificacionPushCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Crear una notificación push
    """
    notificacion = NotificacionPush(
        dispositivo_id=notificacion_data.dispositivo_id,
        usuario_id=notificacion_data.usuario_id,
        tipo=notificacion_data.tipo,
        titulo=notificacion_data.titulo,
        mensaje=notificacion_data.mensaje,
        datos=notificacion_data.datos,
        accion_url=notificacion_data.accion_url,
        prioridad=notificacion_data.prioridad,
        programada_para=notificacion_data.programada_para,
    )

    db.add(notificacion)
    await db.commit()
    await db.refresh(notificacion)

    # TODO: Enviar notificación push real (FCM/APNs)
    # Aquí se integraría con Firebase Cloud Messaging o Apple Push Notification Service

    return notificacion


@router.post("/notificaciones/enviar", status_code=status.HTTP_202_ACCEPTED)
async def enviar_notificacion_masiva(
    notificacion_data: NotificacionPushEnviar,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_admin),
):
    """
    Enviar notificación push masiva

    **Requiere:** Rol de administrador
    """
    notificaciones_creadas = []

    # Obtener dispositivos destino
    query = select(DispositivoMovil).where(
        DispositivoMovil.estado == EstadoDispositivo.ACTIVO,
        DispositivoMovil.notificaciones_habilitadas == True,
    )

    if notificacion_data.usuarios_ids:
        query = query.where(
            DispositivoMovil.usuario_id.in_(notificacion_data.usuarios_ids)
        )
    elif notificacion_data.dispositivos_ids:
        query = query.where(DispositivoMovil.id.in_(notificacion_data.dispositivos_ids))

    result = await db.execute(query)
    dispositivos = result.scalars().all()

    # Crear notificación para cada dispositivo
    for dispositivo in dispositivos:
        notificacion = NotificacionPush(
            dispositivo_id=dispositivo.id,
            usuario_id=dispositivo.usuario_id,
            tipo=notificacion_data.tipo,
            titulo=notificacion_data.titulo,
            mensaje=notificacion_data.mensaje,
            datos=notificacion_data.datos,
            accion_url=notificacion_data.accion_url,
            prioridad=notificacion_data.prioridad,
        )
        db.add(notificacion)
        notificaciones_creadas.append(notificacion)

    await db.commit()

    # TODO: Enviar notificaciones push reales

    return {
        "mensaje": f"Se crearon {len(notificaciones_creadas)} notificaciones",
        "total": len(notificaciones_creadas),
    }


@router.get("/notificaciones", response_model=List[NotificacionPushResponse])
async def listar_notificaciones(
    limite: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Listar notificaciones del usuario
    """
    result = await db.execute(
        select(NotificacionPush)
        .where(NotificacionPush.usuario_id == current_user.id)
        .order_by(desc(NotificacionPush.created_at))
        .limit(limite)
    )
    notificaciones = result.scalars().all()
    return notificaciones


@router.patch(
    "/notificaciones/{notificacion_id}/leer", response_model=NotificacionPushResponse
)
async def marcar_notificacion_leida(
    notificacion_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Marcar notificación como leída
    """
    result = await db.execute(
        select(NotificacionPush).where(
            and_(
                NotificacionPush.id == notificacion_id,
                NotificacionPush.usuario_id == current_user.id,
            )
        )
    )
    notificacion = result.scalar_one_or_none()

    if not notificacion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Notificación no encontrada"
        )

    notificacion.estado = EstadoNotificacion.LEIDA
    notificacion.fecha_lectura = datetime.utcnow()

    await db.commit()
    await db.refresh(notificacion)
    return notificacion


# ==================== DOCUMENTOS ESCANEADOS ====================


@router.post(
    "/documentos",
    response_model=DocumentoEscaneadoResponse,
    status_code=status.HTTP_201_CREATED,
)
async def subir_documento_escaneado(
    tipo: TipoDocumento,
    nombre: str,
    archivo: UploadFile = File(...),
    descripcion: Optional[str] = None,
    paciente_id: Optional[UUID] = None,
    dispositivo_id: Optional[UUID] = None,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Subir documento escaneado desde la app móvil
    """
    import os
    from pathlib import Path

    # Crear directorio si no existe
    upload_dir = Path("uploads/documentos_escaneados")
    upload_dir.mkdir(parents=True, exist_ok=True)

    # Generar nombre único
    file_extension = os.path.splitext(archivo.filename)[1]
    unique_filename = (
        f"{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{nombre}{file_extension}"
    )
    file_path = upload_dir / unique_filename

    # Guardar archivo
    with open(file_path, "wb") as f:
        content = await archivo.read()
        f.write(content)

    # Crear registro
    documento = DocumentoEscaneado(
        dispositivo_id=dispositivo_id,
        usuario_id=current_user.id,
        paciente_id=paciente_id,
        tipo=tipo,
        nombre=nombre,
        descripcion=descripcion,
        ruta_archivo=str(file_path),
        tamano_bytes=len(content),
        mime_type=archivo.content_type,
        fecha_captura=datetime.utcnow(),
    )

    db.add(documento)
    await db.commit()
    await db.refresh(documento)

    # TODO: Procesar OCR en background

    return documento


@router.get("/documentos", response_model=List[DocumentoEscaneadoResponse])
async def listar_documentos_escaneados(
    paciente_id: Optional[UUID] = None,
    tipo: Optional[TipoDocumento] = None,
    limite: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Listar documentos escaneados
    """
    query = select(DocumentoEscaneado).where(
        DocumentoEscaneado.usuario_id == current_user.id
    )

    if paciente_id:
        query = query.where(DocumentoEscaneado.paciente_id == paciente_id)
    if tipo:
        query = query.where(DocumentoEscaneado.tipo == tipo)

    query = query.order_by(desc(DocumentoEscaneado.created_at)).limit(limite)

    result = await db.execute(query)
    documentos = result.scalars().all()
    return documentos


@router.post(
    "/documentos/{documento_id}/firmar", response_model=DocumentoEscaneadoResponse
)
async def firmar_documento(
    documento_id: UUID,
    firma_data: FirmarDocumentoRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Firmar documento con biometría
    """
    result = await db.execute(
        select(DocumentoEscaneado).where(
            and_(
                DocumentoEscaneado.id == documento_id,
                DocumentoEscaneado.usuario_id == current_user.id,
            )
        )
    )
    documento = result.scalar_one_or_none()

    if not documento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Documento no encontrado"
        )

    documento.firmado = True
    documento.firma_biometrica = firma_data.firma_biometrica
    documento.fecha_firma = datetime.utcnow()

    await db.commit()
    await db.refresh(documento)
    return documento


# ==================== SINCRONIZACIÓN OFFLINE ====================


@router.post("/sincronizar", response_model=SincronizarResponse)
async def sincronizar_operaciones(
    sincronizar_data: SincronizarRequest,
    dispositivo_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Sincronizar operaciones offline
    """
    resultados = []
    exitosas = 0
    fallidas = 0
    conflictos = 0

    for operacion_data in sincronizar_data.operaciones:
        try:
            # Crear registro de sincronización
            operacion = SincronizacionOffline(
                dispositivo_id=dispositivo_id,
                usuario_id=current_user.id,
                entidad=operacion_data.entidad,
                operacion=operacion_data.operacion,
                entidad_id=operacion_data.entidad_id,
                datos=operacion_data.datos,
                datos_anteriores=operacion_data.datos_anteriores,
                prioridad=operacion_data.prioridad,
                fecha_creacion_local=operacion_data.fecha_creacion_local,
                estado=EstadoSincronizacion.EN_PROGRESO,
            )

            db.add(operacion)
            await db.flush()

            # TODO: Procesar operación (crear/actualizar/eliminar entidad)
            # Aquí se implementaría la lógica específica por tipo de entidad

            operacion.estado = EstadoSincronizacion.COMPLETADA
            operacion.fecha_procesamiento = datetime.utcnow()
            operacion.fecha_completado = datetime.utcnow()
            exitosas += 1

            resultados.append(operacion)

        except Exception as e:
            operacion.estado = EstadoSincronizacion.FALLIDA
            operacion.mensaje_error = str(e)
            operacion.intentos += 1
            fallidas += 1
            resultados.append(operacion)

    await db.commit()

    return SincronizarResponse(
        total=len(sincronizar_data.operaciones),
        exitosas=exitosas,
        fallidas=fallidas,
        conflictos=conflictos,
        resultados=resultados,
    )


@router.get("/sincronizacion/estado", response_model=EstadoSincronizacionResponse)
async def obtener_estado_sincronizacion(
    dispositivo_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Obtener estado de sincronización del dispositivo
    """
    # Última sincronización
    result = await db.execute(
        select(SincronizacionOffline)
        .where(
            and_(
                SincronizacionOffline.dispositivo_id == dispositivo_id,
                SincronizacionOffline.estado == EstadoSincronizacion.COMPLETADA,
            )
        )
        .order_by(desc(SincronizacionOffline.fecha_completado))
        .limit(1)
    )
    ultima_sync = result.scalar_one_or_none()

    # Contar operaciones por estado
    pendientes = await db.scalar(
        select(func.count(SincronizacionOffline.id)).where(
            and_(
                SincronizacionOffline.dispositivo_id == dispositivo_id,
                SincronizacionOffline.estado == EstadoSincronizacion.PENDIENTE,
            )
        )
    )

    en_progreso = await db.scalar(
        select(func.count(SincronizacionOffline.id)).where(
            and_(
                SincronizacionOffline.dispositivo_id == dispositivo_id,
                SincronizacionOffline.estado == EstadoSincronizacion.EN_PROGRESO,
            )
        )
    )

    fallidas = await db.scalar(
        select(func.count(SincronizacionOffline.id)).where(
            and_(
                SincronizacionOffline.dispositivo_id == dispositivo_id,
                SincronizacionOffline.estado == EstadoSincronizacion.FALLIDA,
            )
        )
    )

    conflictos = await db.scalar(
        select(func.count(SincronizacionOffline.id)).where(
            and_(
                SincronizacionOffline.dispositivo_id == dispositivo_id,
                SincronizacionOffline.conflicto == True,
            )
        )
    )

    return EstadoSincronizacionResponse(
        ultima_sincronizacion=ultima_sync.fecha_completado if ultima_sync else None,
        operaciones_pendientes=pendientes or 0,
        operaciones_en_progreso=en_progreso or 0,
        operaciones_fallidas=fallidas or 0,
        conflictos_sin_resolver=conflictos or 0,
    )


# ==================== CITAS MÓVILES ====================


@router.post(
    "/citas", response_model=CitaMovilResponse, status_code=status.HTTP_201_CREATED
)
async def crear_cita_movil(
    cita_data: CitaMovilCreate,
    dispositivo_id: Optional[UUID] = None,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Crear cita desde la app móvil
    """
    cita = CitaMovil(
        paciente_id=cita_data.paciente_id,
        medico_id=cita_data.medico_id,
        dispositivo_id=dispositivo_id,
        fecha_hora=cita_data.fecha_hora,
        duracion_minutos=cita_data.duracion_minutos,
        motivo=cita_data.motivo,
        notas=cita_data.notas,
        es_telemedicina=cita_data.es_telemedicina,
    )

    db.add(cita)
    await db.commit()
    await db.refresh(cita)

    # TODO: Crear notificación de recordatorio

    return cita


@router.get("/citas", response_model=List[CitaMovilResponse])
async def listar_citas_moviles(
    fecha_desde: Optional[datetime] = None,
    fecha_hasta: Optional[datetime] = None,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Listar citas del usuario
    """
    query = select(CitaMovil).where(
        or_(
            CitaMovil.paciente_id == current_user.id,
            CitaMovil.medico_id == current_user.id,
        )
    )

    if fecha_desde:
        query = query.where(CitaMovil.fecha_hora >= fecha_desde)
    if fecha_hasta:
        query = query.where(CitaMovil.fecha_hora <= fecha_hasta)

    query = query.order_by(CitaMovil.fecha_hora)

    result = await db.execute(query)
    citas = result.scalars().all()
    return citas


@router.patch("/citas/{cita_id}", response_model=CitaMovilResponse)
async def actualizar_cita_movil(
    cita_id: UUID,
    cita_data: CitaMovilUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Actualizar cita (confirmar/cancelar)
    """
    result = await db.execute(select(CitaMovil).where(CitaMovil.id == cita_id))
    cita = result.scalar_one_or_none()

    if not cita:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Cita no encontrada"
        )

    # Actualizar campos
    if cita_data.fecha_hora is not None:
        cita.fecha_hora = cita_data.fecha_hora
    if cita_data.duracion_minutos is not None:
        cita.duracion_minutos = cita_data.duracion_minutos
    if cita_data.motivo is not None:
        cita.motivo = cita_data.motivo
    if cita_data.notas is not None:
        cita.notas = cita_data.notas
    if cita_data.confirmada is not None:
        cita.confirmada = cita_data.confirmada
        cita.fecha_confirmacion = datetime.utcnow() if cita_data.confirmada else None
    if cita_data.cancelada is not None:
        cita.cancelada = cita_data.cancelada
        cita.fecha_cancelacion = datetime.utcnow() if cita_data.cancelada else None
        cita.motivo_cancelacion = cita_data.motivo_cancelacion

    await db.commit()
    await db.refresh(cita)
    return cita


# ==================== CONFIGURACIÓN ====================


@router.get("/configuracion", response_model=ConfiguracionAppMovilResponse)
async def obtener_configuracion(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Obtener configuración de la app móvil
    """
    result = await db.execute(
        select(ConfiguracionAppMovil).where(
            ConfiguracionAppMovil.usuario_id == current_user.id
        )
    )
    config = result.scalar_one_or_none()

    if not config:
        # Crear configuración por defecto
        config = ConfiguracionAppMovil(usuario_id=current_user.id)
        db.add(config)
        await db.commit()
        await db.refresh(config)

    return config


@router.patch("/configuracion", response_model=ConfiguracionAppMovilResponse)
async def actualizar_configuracion(
    config_data: ConfiguracionAppMovilUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Actualizar configuración de la app móvil
    """
    result = await db.execute(
        select(ConfiguracionAppMovil).where(
            ConfiguracionAppMovil.usuario_id == current_user.id
        )
    )
    config = result.scalar_one_or_none()

    if not config:
        config = ConfiguracionAppMovil(usuario_id=current_user.id)
        db.add(config)

    # Actualizar campos
    for field, value in config_data.dict(exclude_unset=True).items():
        setattr(config, field, value)

    config.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(config)
    return config


# ==================== ESTADÍSTICAS ====================


@router.get("/estadisticas", response_model=EstadisticasAppMovilResponse)
async def obtener_estadisticas(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_admin),
):
    """
    Obtener estadísticas de la app móvil

    **Requiere:** Rol de administrador
    """
    # Total dispositivos
    total_dispositivos = await db.scalar(select(func.count(DispositivoMovil.id)))

    # Dispositivos activos (último acceso < 30 días)
    fecha_limite = datetime.utcnow() - timedelta(days=30)
    dispositivos_activos = await db.scalar(
        select(func.count(DispositivoMovil.id)).where(
            and_(
                DispositivoMovil.estado == EstadoDispositivo.ACTIVO,
                DispositivoMovil.ultimo_acceso >= fecha_limite,
            )
        )
    )

    # Por plataforma
    dispositivos_ios = await db.scalar(
        select(func.count(DispositivoMovil.id)).where(
            DispositivoMovil.plataforma == PlataformaMovil.IOS
        )
    )

    dispositivos_android = await db.scalar(
        select(func.count(DispositivoMovil.id)).where(
            DispositivoMovil.plataforma == PlataformaMovil.ANDROID
        )
    )

    # Notificaciones hoy
    hoy = datetime.utcnow().date()
    notificaciones_hoy = await db.scalar(
        select(func.count(NotificacionPush.id)).where(
            func.date(NotificacionPush.created_at) == hoy
        )
    )

    # Notificaciones pendientes
    notificaciones_pendientes = await db.scalar(
        select(func.count(NotificacionPush.id)).where(
            NotificacionPush.estado == EstadoNotificacion.PENDIENTE
        )
    )

    # Documentos escaneados este mes
    primer_dia_mes = datetime.utcnow().replace(
        day=1, hour=0, minute=0, second=0, microsecond=0
    )
    documentos_mes = await db.scalar(
        select(func.count(DocumentoEscaneado.id)).where(
            DocumentoEscaneado.created_at >= primer_dia_mes
        )
    )

    # Citas programadas (futuras)
    ahora = datetime.utcnow()
    citas_programadas = await db.scalar(
        select(func.count(CitaMovil.id)).where(
            and_(CitaMovil.fecha_hora >= ahora, CitaMovil.cancelada == False)
        )
    )

    # Sincronizaciones pendientes
    sincronizaciones_pendientes = await db.scalar(
        select(func.count(SincronizacionOffline.id)).where(
            SincronizacionOffline.estado == EstadoSincronizacion.PENDIENTE
        )
    )

    return EstadisticasAppMovilResponse(
        total_dispositivos=total_dispositivos or 0,
        dispositivos_activos=dispositivos_activos or 0,
        dispositivos_ios=dispositivos_ios or 0,
        dispositivos_android=dispositivos_android or 0,
        notificaciones_enviadas_hoy=notificaciones_hoy or 0,
        notificaciones_pendientes=notificaciones_pendientes or 0,
        documentos_escaneados_mes=documentos_mes or 0,
        citas_programadas=citas_programadas or 0,
        sincronizaciones_pendientes=sincronizaciones_pendientes or 0,
    )
