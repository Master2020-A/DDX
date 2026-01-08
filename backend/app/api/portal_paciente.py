# app/api/portal_paciente.py

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc
from typing import List, Optional
from datetime import datetime, date, timedelta
from uuid import UUID

from app.core.database import get_db
from app.models.portal_paciente import (
    CitaPaciente,
    SolicitudEstudio,
    PagoServicio,
    MensajePacienteMedico,
    RecordatorioMedicamento,
    RegistroTomaMedicamento,
    ConfiguracionPortal,
    AccesoExpediente,
)
from app.models.paciente import Paciente
from app.schemas.portal_paciente import (
    CitaPacienteCreate,
    CitaPacienteUpdate,
    CitaPacienteResponse,
    SolicitudEstudioCreate,
    SolicitudEstudioUpdate,
    SolicitudEstudioResponse,
    PagoServicioCreate,
    PagoServicioUpdate,
    PagoServicioResponse,
    MensajePacienteMedicoCreate,
    MensajePacienteMedicoUpdate,
    MensajePacienteMedicoResponse,
    RecordatorioMedicamentoCreate,
    RecordatorioMedicamentoUpdate,
    RecordatorioMedicamentoResponse,
    RegistroTomaMedicamentoCreate,
    RegistroTomaMedicamentoResponse,
    ConfiguracionPortalCreate,
    ConfiguracionPortalUpdate,
    ConfiguracionPortalResponse,
    AccesoExpedienteResponse,
    DashboardPortalResponse,
    ExpedienteCompletoResponse,
)

router = APIRouter(tags=["Portal del Paciente"])


# ============================================================================
# DASHBOARD
# ============================================================================


@router.get("/dashboard/{paciente_id}", response_model=DashboardPortalResponse)
async def obtener_dashboard(
    paciente_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Obtener dashboard completo del portal del paciente"""

    # Verificar que el paciente existe
    result = await db.execute(select(Paciente).where(Paciente.id == paciente_id))
    paciente = result.scalar_one_or_none()
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")

    # Citas
    result = await db.execute(
        select(func.count(CitaPaciente.id)).where(
            CitaPaciente.paciente_id == paciente_id
        )
    )
    total_citas = result.scalar() or 0

    result = await db.execute(
        select(func.count(CitaPaciente.id)).where(
            and_(
                CitaPaciente.paciente_id == paciente_id,
                CitaPaciente.estado.in_(["solicitada", "confirmada"]),
            )
        )
    )
    citas_pendientes = result.scalar() or 0

    # Próxima cita
    result = await db.execute(
        select(CitaPaciente)
        .where(
            and_(
                CitaPaciente.paciente_id == paciente_id,
                CitaPaciente.estado.in_(["solicitada", "confirmada"]),
                CitaPaciente.fecha_solicitada >= date.today(),
            )
        )
        .order_by(CitaPaciente.fecha_solicitada)
        .limit(1)
    )
    proxima_cita = result.scalar_one_or_none()

    # Estudios
    result = await db.execute(
        select(func.count(SolicitudEstudio.id)).where(
            SolicitudEstudio.paciente_id == paciente_id
        )
    )
    total_estudios = result.scalar() or 0

    result = await db.execute(
        select(func.count(SolicitudEstudio.id)).where(
            and_(
                SolicitudEstudio.paciente_id == paciente_id,
                SolicitudEstudio.estado.in_(["pendiente", "aprobada", "en_proceso"]),
            )
        )
    )
    estudios_pendientes = result.scalar() or 0

    result = await db.execute(
        select(func.count(SolicitudEstudio.id)).where(
            and_(
                SolicitudEstudio.paciente_id == paciente_id,
                SolicitudEstudio.resultado_disponible == True,
            )
        )
    )
    resultados_disponibles = result.scalar() or 0

    # Medicamentos
    result = await db.execute(
        select(func.count(RecordatorioMedicamento.id)).where(
            and_(
                RecordatorioMedicamento.paciente_id == paciente_id,
                RecordatorioMedicamento.activo == True,
            )
        )
    )
    medicamentos_activos = result.scalar() or 0

    # Próxima toma (simplificado - en producción calcular según horarios)
    proxima_toma = None
    if medicamentos_activos > 0:
        proxima_toma = datetime.now() + timedelta(hours=1)

    # Mensajes
    result = await db.execute(
        select(func.count(MensajePacienteMedico.id)).where(
            and_(
                MensajePacienteMedico.paciente_id == paciente_id,
                MensajePacienteMedico.remitente_tipo == "medico",
                MensajePacienteMedico.leido == False,
            )
        )
    )
    mensajes_no_leidos = result.scalar() or 0

    # Pagos
    result = await db.execute(
        select(func.count(PagoServicio.id)).where(
            and_(
                PagoServicio.paciente_id == paciente_id,
                PagoServicio.estado == "pendiente",
            )
        )
    )
    pagos_pendientes = result.scalar() or 0

    # Total pagado este mes
    primer_dia_mes = date.today().replace(day=1)
    result = await db.execute(
        select(func.sum(PagoServicio.monto)).where(
            and_(
                PagoServicio.paciente_id == paciente_id,
                PagoServicio.estado == "completado",
                PagoServicio.fecha_pago >= primer_dia_mes,
            )
        )
    )
    total_pagado_mes = float(result.scalar() or 0)

    return DashboardPortalResponse(
        total_citas=total_citas,
        citas_pendientes=citas_pendientes,
        proxima_cita=proxima_cita,
        total_estudios=total_estudios,
        estudios_pendientes=estudios_pendientes,
        resultados_disponibles=resultados_disponibles,
        medicamentos_activos=medicamentos_activos,
        proxima_toma=proxima_toma,
        mensajes_no_leidos=mensajes_no_leidos,
        pagos_pendientes=pagos_pendientes,
        total_pagado_mes=total_pagado_mes,
    )


# ============================================================================
# EXPEDIENTE
# ============================================================================


@router.get("/expediente/{paciente_id}", response_model=ExpedienteCompletoResponse)
async def obtener_expediente_completo(
    paciente_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Obtener expediente médico completo del paciente"""

    # Obtener paciente
    result = await db.execute(select(Paciente).where(Paciente.id == paciente_id))
    paciente = result.scalar_one_or_none()
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")

    # Registrar acceso al expediente
    acceso = AccesoExpediente(
        paciente_id=paciente_id,
        usuario_id=None,  # El paciente mismo
        tipo_acceso="lectura",
        seccion_accedida="expediente_completo",
    )
    db.add(acceso)
    await db.commit()

    # Contar recursos (simplificado - en producción consultar tablas reales)
    total_consultas = 0
    ultima_consulta = None
    total_estudios = 0
    total_medicamentos = 0

    return ExpedienteCompletoResponse(
        paciente_id=paciente.id,
        numero_expediente=paciente.numero_expediente,
        nombre_completo=paciente.nombre_completo,
        fecha_nacimiento=paciente.fecha_nacimiento,
        edad=int(paciente.edad),
        genero=paciente.genero,
        tipo_sangre=paciente.tipo_sangre,
        alergias=paciente.alergias or [],
        total_consultas=total_consultas,
        ultima_consulta=ultima_consulta,
        total_estudios=total_estudios,
        total_medicamentos=total_medicamentos,
        tiene_laboratorios=False,
        tiene_imagenes=False,
        tiene_recetas=False,
        tiene_hospitalizaciones=False,
    )


# ============================================================================
# CITAS
# ============================================================================


@router.post(
    "/citas", response_model=CitaPacienteResponse, status_code=status.HTTP_201_CREATED
)
async def crear_cita(
    cita: CitaPacienteCreate,
    db: AsyncSession = Depends(get_db),
):
    """Agendar una nueva cita"""

    # Verificar que el paciente existe
    result = await db.execute(select(Paciente).where(Paciente.id == cita.paciente_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Paciente no encontrado")

    nueva_cita = CitaPaciente(**cita.model_dump())
    db.add(nueva_cita)
    await db.commit()
    await db.refresh(nueva_cita)

    return nueva_cita


@router.get("/citas/{paciente_id}", response_model=List[CitaPacienteResponse])
async def listar_citas_por_path(
    paciente_id: UUID,
    estado: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    """Listar citas del paciente (por path parameter)"""

    query = select(CitaPaciente).where(CitaPaciente.paciente_id == paciente_id)

    if estado:
        query = query.where(CitaPaciente.estado == estado)

    query = (
        query.order_by(desc(CitaPaciente.fecha_solicitada)).offset(skip).limit(limit)
    )

    result = await db.execute(query)
    citas = result.scalars().all()

    return citas


@router.get("/citas", response_model=List[CitaPacienteResponse])
async def listar_citas(
    paciente_id: UUID = Query(...),
    estado: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    """Listar citas del paciente (por query parameter)"""

    query = select(CitaPaciente).where(CitaPaciente.paciente_id == paciente_id)

    if estado:
        query = query.where(CitaPaciente.estado == estado)

    query = (
        query.order_by(desc(CitaPaciente.fecha_solicitada)).offset(skip).limit(limit)
    )

    result = await db.execute(query)
    citas = result.scalars().all()

    return citas


@router.put("/citas/{cita_id}", response_model=CitaPacienteResponse)
async def actualizar_cita(
    cita_id: UUID,
    cita_update: CitaPacienteUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Actualizar una cita"""

    result = await db.execute(select(CitaPaciente).where(CitaPaciente.id == cita_id))
    cita = result.scalar_one_or_none()

    if not cita:
        raise HTTPException(status_code=404, detail="Cita no encontrada")

    for key, value in cita_update.model_dump(exclude_unset=True).items():
        setattr(cita, key, value)

    await db.commit()
    await db.refresh(cita)

    return cita


@router.delete("/citas/{cita_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancelar_cita(
    cita_id: UUID,
    motivo: str,
    db: AsyncSession = Depends(get_db),
):
    """Cancelar una cita"""

    result = await db.execute(select(CitaPaciente).where(CitaPaciente.id == cita_id))
    cita = result.scalar_one_or_none()

    if not cita:
        raise HTTPException(status_code=404, detail="Cita no encontrada")

    cita.estado = "cancelada"
    cita.fecha_cancelacion = datetime.utcnow()
    cita.motivo_cancelacion = motivo
    cita.cancelado_por = "paciente"

    await db.commit()


# ============================================================================
# SOLICITUDES DE ESTUDIOS
# ============================================================================


@router.post(
    "/estudios",
    response_model=SolicitudEstudioResponse,
    status_code=status.HTTP_201_CREATED,
)
async def crear_solicitud_estudio(
    solicitud: SolicitudEstudioCreate,
    db: AsyncSession = Depends(get_db),
):
    """Crear solicitud de estudio"""

    # Verificar que el paciente existe
    result = await db.execute(
        select(Paciente).where(Paciente.id == solicitud.paciente_id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Paciente no encontrado")

    nueva_solicitud = SolicitudEstudio(**solicitud.model_dump())
    db.add(nueva_solicitud)
    await db.commit()
    await db.refresh(nueva_solicitud)

    return nueva_solicitud


@router.get("/estudios/{paciente_id}", response_model=List[SolicitudEstudioResponse])
async def listar_solicitudes_estudios_por_path(
    paciente_id: UUID,
    estado: Optional[str] = None,
    tipo_estudio: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    """Listar solicitudes de estudios del paciente (por path parameter)"""

    query = select(SolicitudEstudio).where(SolicitudEstudio.paciente_id == paciente_id)

    if estado:
        query = query.where(SolicitudEstudio.estado == estado)

    if tipo_estudio:
        query = query.where(SolicitudEstudio.tipo_estudio == tipo_estudio)

    query = (
        query.order_by(desc(SolicitudEstudio.fecha_solicitud)).offset(skip).limit(limit)
    )

    result = await db.execute(query)
    solicitudes = result.scalars().all()

    return solicitudes


@router.get("/solicitudes-estudios", response_model=List[SolicitudEstudioResponse])
async def listar_solicitudes_estudios(
    paciente_id: UUID = Query(...),
    estado: Optional[str] = None,
    tipo_estudio: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    """Listar solicitudes de estudios del paciente (por query parameter)"""

    query = select(SolicitudEstudio).where(SolicitudEstudio.paciente_id == paciente_id)

    if estado:
        query = query.where(SolicitudEstudio.estado == estado)

    if tipo_estudio:
        query = query.where(SolicitudEstudio.tipo_estudio == tipo_estudio)

    query = (
        query.order_by(desc(SolicitudEstudio.fecha_solicitud)).offset(skip).limit(limit)
    )

    result = await db.execute(query)
    solicitudes = result.scalars().all()

    return solicitudes


@router.get("/estudios/detalle/{solicitud_id}", response_model=SolicitudEstudioResponse)
async def obtener_solicitud_estudio(
    solicitud_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Obtener detalle de solicitud de estudio"""

    result = await db.execute(
        select(SolicitudEstudio).where(SolicitudEstudio.id == solicitud_id)
    )
    solicitud = result.scalar_one_or_none()

    if not solicitud:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")

    return solicitud


# ============================================================================
# PAGOS
# ============================================================================


@router.post(
    "/pagos", response_model=PagoServicioResponse, status_code=status.HTTP_201_CREATED
)
async def crear_pago(
    pago: PagoServicioCreate,
    db: AsyncSession = Depends(get_db),
):
    """Crear un pago de servicio"""

    # Verificar que el paciente existe
    result = await db.execute(select(Paciente).where(Paciente.id == pago.paciente_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Paciente no encontrado")

    nuevo_pago = PagoServicio(**pago.model_dump())
    db.add(nuevo_pago)
    await db.commit()
    await db.refresh(nuevo_pago)

    return nuevo_pago


@router.get("/pagos/{paciente_id}", response_model=List[PagoServicioResponse])
async def listar_pagos_por_path(
    paciente_id: UUID,
    estado: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    """Listar pagos del paciente (por path parameter)"""

    query = select(PagoServicio).where(PagoServicio.paciente_id == paciente_id)

    if estado:
        query = query.where(PagoServicio.estado == estado)

    query = query.order_by(desc(PagoServicio.fecha_pago)).offset(skip).limit(limit)

    result = await db.execute(query)
    pagos = result.scalars().all()

    return pagos


@router.get("/pagos", response_model=List[PagoServicioResponse])
async def listar_pagos(
    paciente_id: UUID = Query(...),
    estado: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    """Listar pagos del paciente (por query parameter)"""

    query = select(PagoServicio).where(PagoServicio.paciente_id == paciente_id)

    if estado:
        query = query.where(PagoServicio.estado == estado)

    query = query.order_by(desc(PagoServicio.fecha_pago)).offset(skip).limit(limit)

    result = await db.execute(query)
    pagos = result.scalars().all()

    return pagos


@router.put("/pagos/{pago_id}/procesar", response_model=PagoServicioResponse)
async def procesar_pago(
    pago_id: UUID,
    referencia_pago: str,
    db: AsyncSession = Depends(get_db),
):
    """Procesar un pago (simular integración con pasarela)"""

    result = await db.execute(select(PagoServicio).where(PagoServicio.id == pago_id))
    pago = result.scalar_one_or_none()

    if not pago:
        raise HTTPException(status_code=404, detail="Pago no encontrado")

    # Simular procesamiento
    pago.estado = "completado"
    pago.referencia_pago = referencia_pago
    pago.fecha_procesado = datetime.utcnow()
    pago.fecha_completado = datetime.utcnow()

    await db.commit()
    await db.refresh(pago)

    return pago


# ============================================================================
# MENSAJERÍA
# ============================================================================


@router.post(
    "/mensajes",
    response_model=MensajePacienteMedicoResponse,
    status_code=status.HTTP_201_CREATED,
)
async def enviar_mensaje(
    mensaje: MensajePacienteMedicoCreate,
    db: AsyncSession = Depends(get_db),
):
    """Enviar mensaje entre paciente y médico"""

    # Verificar que el paciente existe
    result = await db.execute(
        select(Paciente).where(Paciente.id == mensaje.paciente_id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Paciente no encontrado")

    nuevo_mensaje = MensajePacienteMedico(**mensaje.model_dump())
    db.add(nuevo_mensaje)
    await db.commit()
    await db.refresh(nuevo_mensaje)

    return nuevo_mensaje


@router.get(
    "/mensajes/{paciente_id}", response_model=List[MensajePacienteMedicoResponse]
)
async def listar_mensajes_por_path(
    paciente_id: UUID,
    medico_id: Optional[UUID] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    """Listar mensajes del paciente (por path parameter)"""

    query = select(MensajePacienteMedico).where(
        MensajePacienteMedico.paciente_id == paciente_id
    )

    if medico_id:
        query = query.where(MensajePacienteMedico.medico_id == medico_id)

    query = (
        query.order_by(desc(MensajePacienteMedico.created_at)).offset(skip).limit(limit)
    )

    result = await db.execute(query)
    mensajes = result.scalars().all()

    return mensajes


@router.get("/mensajes", response_model=List[MensajePacienteMedicoResponse])
async def listar_mensajes(
    paciente_id: UUID = Query(...),
    medico_id: Optional[UUID] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    """Listar mensajes del paciente (por query parameter)"""

    query = select(MensajePacienteMedico).where(
        MensajePacienteMedico.paciente_id == paciente_id
    )

    if medico_id:
        query = query.where(MensajePacienteMedico.medico_id == medico_id)

    query = (
        query.order_by(desc(MensajePacienteMedico.created_at)).offset(skip).limit(limit)
    )

    result = await db.execute(query)
    mensajes = result.scalars().all()

    return mensajes


@router.put(
    "/mensajes/{mensaje_id}/marcar-leido", response_model=MensajePacienteMedicoResponse
)
async def marcar_mensaje_leido(
    mensaje_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Marcar mensaje como leído"""

    result = await db.execute(
        select(MensajePacienteMedico).where(MensajePacienteMedico.id == mensaje_id)
    )
    mensaje = result.scalar_one_or_none()

    if not mensaje:
        raise HTTPException(status_code=404, detail="Mensaje no encontrado")

    mensaje.leido = True
    mensaje.fecha_lectura = datetime.utcnow()

    await db.commit()
    await db.refresh(mensaje)

    return mensaje


# ============================================================================
# RECORDATORIOS DE MEDICAMENTOS
# ============================================================================


@router.post(
    "/recordatorios",
    response_model=RecordatorioMedicamentoResponse,
    status_code=status.HTTP_201_CREATED,
)
async def crear_recordatorio(
    recordatorio: RecordatorioMedicamentoCreate,
    db: AsyncSession = Depends(get_db),
):
    """Crear recordatorio de medicamento"""

    # Verificar que el paciente existe
    result = await db.execute(
        select(Paciente).where(Paciente.id == recordatorio.paciente_id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Paciente no encontrado")

    nuevo_recordatorio = RecordatorioMedicamento(**recordatorio.model_dump())
    db.add(nuevo_recordatorio)
    await db.commit()
    await db.refresh(nuevo_recordatorio)

    return nuevo_recordatorio


@router.get(
    "/recordatorios/{paciente_id}", response_model=List[RecordatorioMedicamentoResponse]
)
async def listar_recordatorios_por_path(
    paciente_id: UUID,
    activo: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    """Listar recordatorios de medicamentos del paciente (por path parameter)"""

    query = select(RecordatorioMedicamento).where(
        RecordatorioMedicamento.paciente_id == paciente_id
    )

    if activo is not None:
        query = query.where(RecordatorioMedicamento.activo == activo)

    query = (
        query.order_by(desc(RecordatorioMedicamento.created_at))
        .offset(skip)
        .limit(limit)
    )

    result = await db.execute(query)
    recordatorios = result.scalars().all()

    return recordatorios


@router.get("/recordatorios", response_model=List[RecordatorioMedicamentoResponse])
async def listar_recordatorios(
    paciente_id: UUID = Query(...),
    activo: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    """Listar recordatorios de medicamentos del paciente (por query parameter)"""

    query = select(RecordatorioMedicamento).where(
        RecordatorioMedicamento.paciente_id == paciente_id
    )

    if activo is not None:
        query = query.where(RecordatorioMedicamento.activo == activo)

    query = (
        query.order_by(desc(RecordatorioMedicamento.created_at))
        .offset(skip)
        .limit(limit)
    )

    result = await db.execute(query)
    recordatorios = result.scalars().all()

    return recordatorios


@router.put(
    "/recordatorios/{recordatorio_id}", response_model=RecordatorioMedicamentoResponse
)
async def actualizar_recordatorio(
    recordatorio_id: UUID,
    recordatorio_update: RecordatorioMedicamentoUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Actualizar recordatorio de medicamento"""

    result = await db.execute(
        select(RecordatorioMedicamento).where(
            RecordatorioMedicamento.id == recordatorio_id
        )
    )
    recordatorio = result.scalar_one_or_none()

    if not recordatorio:
        raise HTTPException(status_code=404, detail="Recordatorio no encontrado")

    for key, value in recordatorio_update.model_dump(exclude_unset=True).items():
        setattr(recordatorio, key, value)

    await db.commit()
    await db.refresh(recordatorio)

    return recordatorio


@router.post(
    "/recordatorios/{recordatorio_id}/registrar-toma",
    response_model=RegistroTomaMedicamentoResponse,
    status_code=status.HTTP_201_CREATED,
)
async def registrar_toma_medicamento(
    recordatorio_id: UUID,
    registro: RegistroTomaMedicamentoCreate,
    db: AsyncSession = Depends(get_db),
):
    """Registrar toma de medicamento"""

    # Verificar que el recordatorio existe
    result = await db.execute(
        select(RecordatorioMedicamento).where(
            RecordatorioMedicamento.id == recordatorio_id
        )
    )
    recordatorio = result.scalar_one_or_none()

    if not recordatorio:
        raise HTTPException(status_code=404, detail="Recordatorio no encontrado")

    nuevo_registro = RegistroTomaMedicamento(**registro.model_dump())
    db.add(nuevo_registro)

    # Actualizar contador en recordatorio
    if nuevo_registro.tomado:
        recordatorio.tomas_registradas += 1
        recordatorio.ultima_toma_registrada = datetime.utcnow()
    elif nuevo_registro.omitido:
        recordatorio.tomas_omitidas += 1

    await db.commit()
    await db.refresh(nuevo_registro)

    return nuevo_registro


# ============================================================================
# CONFIGURACIÓN
# ============================================================================


@router.post(
    "/configuracion",
    response_model=ConfiguracionPortalResponse,
    status_code=status.HTTP_201_CREATED,
)
async def crear_configuracion(
    configuracion: ConfiguracionPortalCreate,
    db: AsyncSession = Depends(get_db),
):
    """Crear configuración del portal"""

    # Verificar que el paciente existe
    result = await db.execute(
        select(Paciente).where(Paciente.id == configuracion.paciente_id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Paciente no encontrado")

    # Verificar que no existe configuración previa
    result = await db.execute(
        select(ConfiguracionPortal).where(
            ConfiguracionPortal.paciente_id == configuracion.paciente_id
        )
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=400, detail="Ya existe configuración para este paciente"
        )

    nueva_configuracion = ConfiguracionPortal(**configuracion.model_dump())
    db.add(nueva_configuracion)
    await db.commit()
    await db.refresh(nueva_configuracion)

    return nueva_configuracion


@router.get("/configuracion/{paciente_id}", response_model=ConfiguracionPortalResponse)
async def obtener_configuracion(
    paciente_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Obtener configuración del portal (crea una por defecto si no existe)"""

    # Verificar que el paciente existe
    result = await db.execute(select(Paciente).where(Paciente.id == paciente_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Paciente no encontrado")

    # Buscar configuración existente
    result = await db.execute(
        select(ConfiguracionPortal).where(
            ConfiguracionPortal.paciente_id == paciente_id
        )
    )
    configuracion = result.scalar_one_or_none()

    # Si no existe, crear una configuración por defecto
    if not configuracion:
        configuracion = ConfiguracionPortal(
            paciente_id=paciente_id,
            notificaciones_email=True,
            notificaciones_sms=False,
            notificaciones_push=True,
            compartir_datos_investigacion=False,
            mostrar_perfil_publico=False,
            idioma="es",
            tema="claro",
            zona_horaria="America/Mexico_City",
            recordatorios_citas=True,
            recordatorios_medicamentos=True,
            recordatorios_estudios=True,
        )
        db.add(configuracion)
        await db.commit()
        await db.refresh(configuracion)

    return configuracion


@router.put("/configuracion/{paciente_id}", response_model=ConfiguracionPortalResponse)
async def actualizar_configuracion(
    paciente_id: UUID,
    configuracion_update: ConfiguracionPortalUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Actualizar configuración del portal"""

    result = await db.execute(
        select(ConfiguracionPortal).where(
            ConfiguracionPortal.paciente_id == paciente_id
        )
    )
    configuracion = result.scalar_one_or_none()

    if not configuracion:
        raise HTTPException(status_code=404, detail="Configuración no encontrada")

    for key, value in configuracion_update.model_dump(exclude_unset=True).items():
        setattr(configuracion, key, value)

    await db.commit()
    await db.refresh(configuracion)

    return configuracion


# ============================================================================
# ACCESOS AL EXPEDIENTE
# ============================================================================


@router.get("/accesos/{paciente_id}", response_model=List[AccesoExpedienteResponse])
async def listar_accesos_expediente(
    paciente_id: UUID,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    """Listar accesos al expediente del paciente"""

    query = (
        select(AccesoExpediente)
        .where(AccesoExpediente.paciente_id == paciente_id)
        .order_by(desc(AccesoExpediente.fecha_acceso))
        .offset(skip)
        .limit(limit)
    )

    result = await db.execute(query)
    accesos = result.scalars().all()

    return accesos
