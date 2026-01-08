"""
Endpoints API para el módulo de Integraciones
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from typing import List, Optional
from datetime import datetime, timedelta
from uuid import UUID
import secrets
import string

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.usuario import Usuario
from app.models.integraciones import (
    ConfiguracionIntegracion,
    ConfiguracionPACS,
    ConfiguracionLIS,
    RecetaElectronica,
    SolicitudFarmacia,
    FacturaElectronica,
    IntegracionERP,
    LogIntegracion,
)
from app.schemas.integraciones import (
    ConfiguracionIntegracionCreate,
    ConfiguracionIntegracionUpdate,
    ConfiguracionIntegracionResponse,
    RecetaElectronicaCreate,
    RecetaElectronicaResponse,
    ValidarReceta,
    SurtirReceta,
    SolicitudFarmaciaCreate,
    SolicitudFarmaciaResponse,
    DispensarMedicamentos,
    ConsultarDisponibilidad,
    FacturaElectronicaCreate,
    FacturaElectronicaResponse,
    TimbrarFactura,
    CancelarFactura,
    IntegracionERPCreate,
    IntegracionERPResponse,
    SincronizarPacienteERP,
    RegistrarServicioERP,
    LogIntegracionResponse,
    DashboardIntegraciones,
    EstadisticasIntegracion,
)

router = APIRouter(tags=["Integraciones"])


# ============================================================================
# Configuración General
# ============================================================================


@router.get("/configuraciones", response_model=List[ConfiguracionIntegracionResponse])
async def listar_configuraciones(
    tipo_sistema: Optional[str] = None,
    activo: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Listar todas las configuraciones de integración"""
    query = select(ConfiguracionIntegracion)

    if tipo_sistema:
        query = query.where(ConfiguracionIntegracion.tipo_sistema == tipo_sistema)
    if activo is not None:
        query = query.where(ConfiguracionIntegracion.activo == activo)

    result = await db.execute(query)
    return result.scalars().all()


@router.post("/configuraciones", response_model=ConfiguracionIntegracionResponse)
async def crear_configuracion(
    config: ConfiguracionIntegracionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Crear nueva configuración de integración"""
    # TODO: Encriptar credenciales antes de guardar
    nueva_config = ConfiguracionIntegracion(
        nombre=config.nombre,
        tipo_sistema=config.tipo_sistema,
        descripcion=config.descripcion,
        url_base=config.url_base,
        puerto=config.puerto,
        protocolo=config.protocolo,
        tipo_auth=config.tipo_auth,
        usuario=config.usuario,
        configuracion_adicional=config.configuracion_adicional,
        webhook_url=config.webhook_url,
        timeout_segundos=config.timeout_segundos,
        max_reintentos=config.max_reintentos,
        intervalo_reintento_segundos=config.intervalo_reintento_segundos,
        activo=config.activo,
        log_requests=config.log_requests,
        log_responses=config.log_responses,
    )

    db.add(nueva_config)
    await db.commit()
    await db.refresh(nueva_config)
    return nueva_config


@router.get(
    "/configuraciones/{config_id}", response_model=ConfiguracionIntegracionResponse
)
async def obtener_configuracion(
    config_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Obtener configuración por ID"""
    result = await db.execute(
        select(ConfiguracionIntegracion).where(ConfiguracionIntegracion.id == config_id)
    )
    config = result.scalar_one_or_none()

    if not config:
        raise HTTPException(status_code=404, detail="Configuración no encontrada")

    return config


@router.put(
    "/configuraciones/{config_id}", response_model=ConfiguracionIntegracionResponse
)
async def actualizar_configuracion(
    config_id: UUID,
    config_update: ConfiguracionIntegracionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Actualizar configuración existente"""
    result = await db.execute(
        select(ConfiguracionIntegracion).where(ConfiguracionIntegracion.id == config_id)
    )
    config = result.scalar_one_or_none()

    if not config:
        raise HTTPException(status_code=404, detail="Configuración no encontrada")

    # Actualizar campos
    for field, value in config_update.dict(exclude_unset=True).items():
        setattr(config, field, value)

    await db.commit()
    await db.refresh(config)
    return config


@router.delete("/configuraciones/{config_id}")
async def eliminar_configuracion(
    config_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Eliminar configuración"""
    result = await db.execute(
        select(ConfiguracionIntegracion).where(ConfiguracionIntegracion.id == config_id)
    )
    config = result.scalar_one_or_none()

    if not config:
        raise HTTPException(status_code=404, detail="Configuración no encontrada")

    await db.delete(config)
    await db.commit()
    return {"message": "Configuración eliminada exitosamente"}


# ============================================================================
# Receta Electrónica
# ============================================================================


def generar_folio_receta() -> str:
    """Generar folio único para receta"""
    return f"RX-{datetime.now().strftime('%Y%m%d')}-{secrets.randbelow(999999):06d}"


def generar_codigo_verificacion() -> str:
    """Generar código de verificación alfanumérico"""
    chars = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(chars) for _ in range(8))


@router.post("/receta-electronica", response_model=RecetaElectronicaResponse)
async def generar_receta_electronica(
    receta: RecetaElectronicaCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Generar nueva receta electrónica"""
    nueva_receta = RecetaElectronica(
        folio=generar_folio_receta(),
        codigo_verificacion=generar_codigo_verificacion(),
        paciente_id=receta.paciente_id,
        medico_id=receta.medico_id,
        consulta_id=receta.consulta_id,
        diagnostico_cie10=receta.diagnostico_cie10,
        medicamentos=[med.dict() for med in receta.medicamentos],
        fecha_vencimiento=datetime.utcnow() + timedelta(days=receta.vigencia_dias),
        estado="ACTIVA",
    )

    # TODO: Generar firma electrónica

    db.add(nueva_receta)
    await db.commit()
    await db.refresh(nueva_receta)
    return nueva_receta


@router.post("/receta-electronica/validar")
async def validar_receta_electronica(
    validacion: ValidarReceta, db: AsyncSession = Depends(get_db)
):
    """Validar receta electrónica"""
    result = await db.execute(
        select(RecetaElectronica).where(
            and_(
                RecetaElectronica.folio == validacion.folio_receta,
                RecetaElectronica.codigo_verificacion == validacion.codigo_verificacion,
            )
        )
    )
    receta = result.scalar_one_or_none()

    if not receta:
        raise HTTPException(
            status_code=404, detail="Receta no encontrada o código inválido"
        )

    # Actualizar intentos de validación
    receta.intentos_validacion += 1
    receta.ultima_validacion = datetime.utcnow()
    await db.commit()

    # Verificar estado
    valida = receta.estado == "ACTIVA" and receta.fecha_vencimiento > datetime.utcnow()

    return {
        "valida": valida,
        "estado": receta.estado,
        "fecha_emision": receta.fecha_emision,
        "fecha_vencimiento": receta.fecha_vencimiento,
        "medicamentos": receta.medicamentos,
    }


@router.post("/receta-electronica/surtir")
async def surtir_receta_electronica(
    surtido: SurtirReceta,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Registrar surtido de receta"""
    result = await db.execute(
        select(RecetaElectronica).where(RecetaElectronica.folio == surtido.folio_receta)
    )
    receta = result.scalar_one_or_none()

    if not receta:
        raise HTTPException(status_code=404, detail="Receta no encontrada")

    if receta.estado != "ACTIVA":
        raise HTTPException(status_code=400, detail="Receta no está activa")

    receta.estado = "SURTIDA"
    receta.fecha_surtido = surtido.fecha_surtido
    receta.farmacia_id = surtido.farmacia_id

    await db.commit()
    return {"message": "Receta surtida exitosamente"}


@router.get("/receta-electronica", response_model=List[RecetaElectronicaResponse])
async def listar_recetas(
    paciente_id: Optional[UUID] = None,
    medico_id: Optional[UUID] = None,
    estado: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Listar recetas electrónicas"""
    query = select(RecetaElectronica)

    if paciente_id:
        query = query.where(RecetaElectronica.paciente_id == paciente_id)
    if medico_id:
        query = query.where(RecetaElectronica.medico_id == medico_id)
    if estado:
        query = query.where(RecetaElectronica.estado == estado)

    query = (
        query.order_by(RecetaElectronica.fecha_emision.desc()).offset(skip).limit(limit)
    )

    result = await db.execute(query)
    return result.scalars().all()


# ============================================================================
# Farmacia
# ============================================================================


def generar_folio_solicitud() -> str:
    """Generar folio único para solicitud de farmacia"""
    return f"SF-{datetime.now().strftime('%Y%m%d')}-{secrets.randbelow(999999):06d}"


@router.post("/farmacia/solicitud", response_model=SolicitudFarmaciaResponse)
async def crear_solicitud_farmacia(
    solicitud: SolicitudFarmaciaCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Crear solicitud de medicamentos a farmacia"""
    nueva_solicitud = SolicitudFarmacia(
        folio=generar_folio_solicitud(),
        paciente_id=solicitud.paciente_id,
        medico_id=solicitud.medico_id,
        receta_id=solicitud.receta_id,
        medicamentos_solicitados=[
            med.dict() for med in solicitud.medicamentos_solicitados
        ],
        urgente=solicitud.urgente,
        destino=solicitud.destino,
        ubicacion=solicitud.ubicacion,
        notas=solicitud.notas,
        estado="PENDIENTE",
    )

    db.add(nueva_solicitud)
    await db.commit()
    await db.refresh(nueva_solicitud)
    return nueva_solicitud


@router.post("/farmacia/dispensar")
async def dispensar_medicamentos(
    dispensacion: DispensarMedicamentos,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Registrar dispensación de medicamentos"""
    result = await db.execute(
        select(SolicitudFarmacia).where(
            SolicitudFarmacia.id == dispensacion.solicitud_id
        )
    )
    solicitud = result.scalar_one_or_none()

    if not solicitud:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")

    solicitud.estado = "DISPENSADO"
    solicitud.fecha_dispensacion = datetime.utcnow()
    solicitud.farmaceutico_id = dispensacion.farmaceutico_id
    solicitud.medicamentos_dispensados = dispensacion.medicamentos_dispensados
    solicitud.costo_total = dispensacion.costo_total
    solicitud.verificado = True
    solicitud.verificado_por = dispensacion.verificado_por
    solicitud.fecha_verificacion = datetime.utcnow()

    await db.commit()
    return {"message": "Medicamentos dispensados exitosamente"}


@router.get("/farmacia/solicitudes", response_model=List[SolicitudFarmaciaResponse])
async def listar_solicitudes_farmacia(
    estado: Optional[str] = None,
    urgente: Optional[bool] = None,
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Listar solicitudes de farmacia"""
    query = select(SolicitudFarmacia)

    if estado:
        query = query.where(SolicitudFarmacia.estado == estado)
    if urgente is not None:
        query = query.where(SolicitudFarmacia.urgente == urgente)

    query = (
        query.order_by(SolicitudFarmacia.fecha_solicitud.desc())
        .offset(skip)
        .limit(limit)
    )

    result = await db.execute(query)
    return result.scalars().all()


@router.post("/farmacia/disponibilidad")
async def consultar_disponibilidad(
    consulta: ConsultarDisponibilidad,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Consultar disponibilidad de medicamento"""
    # TODO: Integrar con sistema de inventario
    return {
        "disponible": True,
        "stock_actual": 500,
        "precio_unitario": 2.50,
        "precio_total": consulta.cantidad_requerida * 2.50,
        "ubicacion": "Anaquel A-12",
    }


# ============================================================================
# Facturación Electrónica
# ============================================================================


def generar_folio_factura() -> str:
    """Generar folio único para factura"""
    return f"F-{datetime.now().strftime('%Y%m%d')}-{secrets.randbelow(999999):06d}"


@router.post("/facturacion/generar", response_model=FacturaElectronicaResponse)
async def generar_factura(
    factura: FacturaElectronicaCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Generar factura electrónica"""
    nueva_factura = FacturaElectronica(
        serie=factura.serie or "A",
        folio=generar_folio_factura(),
        paciente_id=factura.paciente_id,
        consulta_id=factura.consulta_id,
        hospitalizacion_id=factura.hospitalizacion_id,
        tipo_comprobante=factura.tipo_comprobante,
        uso_cfdi=factura.uso_cfdi,
        metodo_pago=factura.metodo_pago,
        forma_pago=factura.forma_pago,
        receptor_rfc=factura.receptor.rfc,
        receptor_nombre=factura.receptor.nombre,
        receptor_cp=factura.receptor.codigo_postal,
        receptor_regimen=factura.receptor.regimen_fiscal,
        conceptos=[concepto.dict() for concepto in factura.conceptos],
        subtotal=factura.subtotal,
        descuento=factura.descuento,
        total=factura.total,
        fecha_emision=datetime.utcnow(),
        estado="PENDIENTE",
    )

    db.add(nueva_factura)
    await db.commit()
    await db.refresh(nueva_factura)
    return nueva_factura


@router.post("/facturacion/timbrar")
async def timbrar_factura(
    timbrado: TimbrarFactura,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Timbrar factura con PAC"""
    result = await db.execute(
        select(FacturaElectronica).where(FacturaElectronica.id == timbrado.factura_id)
    )
    factura = result.scalar_one_or_none()

    if not factura:
        raise HTTPException(status_code=404, detail="Factura no encontrada")

    # TODO: Integrar con PAC para timbrado real
    factura.uuid_sat = str(UUID(int=secrets.randbits(128)))
    factura.fecha_timbrado = datetime.utcnow()
    factura.estado = "TIMBRADA"
    factura.pac_proveedor = timbrado.pac_proveedor

    await db.commit()

    return {
        "uuid": factura.uuid_sat,
        "fecha_timbrado": factura.fecha_timbrado,
        "message": "Factura timbrada exitosamente",
    }


@router.get("/facturacion", response_model=List[FacturaElectronicaResponse])
async def listar_facturas(
    paciente_id: Optional[UUID] = None,
    estado: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Listar facturas electrónicas"""
    query = select(FacturaElectronica)

    if paciente_id:
        query = query.where(FacturaElectronica.paciente_id == paciente_id)
    if estado:
        query = query.where(FacturaElectronica.estado == estado)

    query = (
        query.order_by(FacturaElectronica.fecha_emision.desc())
        .offset(skip)
        .limit(limit)
    )

    result = await db.execute(query)
    return result.scalars().all()


# ============================================================================
# Dashboard
# ============================================================================


@router.get("/dashboard", response_model=DashboardIntegraciones)
async def obtener_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Obtener dashboard de integraciones"""
    hoy = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

    # Estadísticas de PACS (configuraciones activas)
    pacs_config_result = await db.execute(
        select(func.count(ConfiguracionIntegracion.id)).where(
            and_(
                ConfiguracionIntegracion.tipo_sistema == "PACS",
                ConfiguracionIntegracion.activo == True,
            )
        )
    )
    pacs_activo = (pacs_config_result.scalar() or 0) > 0

    # Estadísticas de LIS (configuraciones activas)
    lis_config_result = await db.execute(
        select(func.count(ConfiguracionIntegracion.id)).where(
            and_(
                ConfiguracionIntegracion.tipo_sistema == "LIS",
                ConfiguracionIntegracion.activo == True,
            )
        )
    )
    lis_activo = (lis_config_result.scalar() or 0) > 0

    # Estadísticas de Receta Electrónica
    recetas_hoy_result = await db.execute(
        select(func.count(RecetaElectronica.id)).where(
            RecetaElectronica.fecha_emision >= hoy
        )
    )
    recetas_hoy_count = recetas_hoy_result.scalar() or 0

    recetas_activas_result = await db.execute(
        select(func.count(RecetaElectronica.id)).where(
            RecetaElectronica.estado == "ACTIVA"
        )
    )
    recetas_activas_count = recetas_activas_result.scalar() or 0

    # Estadísticas de Farmacia
    solicitudes_hoy_result = await db.execute(
        select(func.count(SolicitudFarmacia.id)).where(
            SolicitudFarmacia.fecha_solicitud >= hoy
        )
    )
    solicitudes_hoy_count = solicitudes_hoy_result.scalar() or 0

    solicitudes_pendientes_result = await db.execute(
        select(func.count(SolicitudFarmacia.id)).where(
            SolicitudFarmacia.estado == "PENDIENTE"
        )
    )
    solicitudes_pendientes_count = solicitudes_pendientes_result.scalar() or 0

    # Estadísticas de Facturación
    facturas_hoy_result = await db.execute(
        select(func.count(FacturaElectronica.id)).where(
            FacturaElectronica.fecha_emision >= hoy
        )
    )
    facturas_hoy_count = facturas_hoy_result.scalar() or 0

    facturas_pendientes_result = await db.execute(
        select(func.count(FacturaElectronica.id)).where(
            FacturaElectronica.estado == "PENDIENTE"
        )
    )
    facturas_pendientes_count = facturas_pendientes_result.scalar() or 0

    # Estadísticas de ERP (configuraciones activas)
    erp_config_result = await db.execute(
        select(func.count(ConfiguracionIntegracion.id)).where(
            and_(
                ConfiguracionIntegracion.tipo_sistema == "ERP",
                ConfiguracionIntegracion.activo == True,
            )
        )
    )
    erp_activo = (erp_config_result.scalar() or 0) > 0

    return {
        "pacs": {
            "activo": pacs_activo,
            "operaciones_hoy": 0,
            "operaciones_exitosas_hoy": 0,
            "operaciones_fallidas_hoy": 0,
            "operaciones_pendientes": 0,
            "tasa_exito": 100.0 if pacs_activo else 0.0,
        },
        "lis": {
            "activo": lis_activo,
            "operaciones_hoy": 0,
            "operaciones_exitosas_hoy": 0,
            "operaciones_fallidas_hoy": 0,
            "operaciones_pendientes": 0,
            "tasa_exito": 100.0 if lis_activo else 0.0,
        },
        "receta_electronica": {
            "activo": True,
            "operaciones_hoy": recetas_hoy_count,
            "operaciones_exitosas_hoy": recetas_hoy_count,
            "operaciones_fallidas_hoy": 0,
            "operaciones_pendientes": recetas_activas_count,
            "tasa_exito": 100.0,
        },
        "farmacia": {
            "activo": True,
            "operaciones_hoy": solicitudes_hoy_count,
            "operaciones_exitosas_hoy": solicitudes_hoy_count,
            "operaciones_fallidas_hoy": 0,
            "operaciones_pendientes": solicitudes_pendientes_count,
            "tasa_exito": 100.0,
        },
        "facturacion": {
            "activo": True,
            "operaciones_hoy": facturas_hoy_count,
            "operaciones_exitosas_hoy": facturas_hoy_count,
            "operaciones_fallidas_hoy": 0,
            "operaciones_pendientes": facturas_pendientes_count,
            "tasa_exito": 100.0,
        },
        "erp": {
            "activo": erp_activo,
            "operaciones_hoy": 0,
            "operaciones_exitosas_hoy": 0,
            "operaciones_fallidas_hoy": 0,
            "operaciones_pendientes": 0,
            "tasa_exito": 100.0 if erp_activo else 0.0,
        },
    }


# ============================================================================
# Logs
# ============================================================================


@router.get("/logs", response_model=List[LogIntegracionResponse])
async def listar_logs(
    tipo_sistema: Optional[str] = None,
    exitoso: Optional[bool] = None,
    fecha_desde: Optional[datetime] = None,
    fecha_hasta: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Listar logs de integraciones"""
    query = select(LogIntegracion)

    if tipo_sistema:
        query = query.where(LogIntegracion.tipo_sistema == tipo_sistema)
    if exitoso is not None:
        query = query.where(LogIntegracion.exitoso == exitoso)
    if fecha_desde:
        query = query.where(LogIntegracion.fecha_hora >= fecha_desde)
    if fecha_hasta:
        query = query.where(LogIntegracion.fecha_hora <= fecha_hasta)

    query = query.order_by(LogIntegracion.fecha_hora.desc()).offset(skip).limit(limit)

    result = await db.execute(query)
    return result.scalars().all()
