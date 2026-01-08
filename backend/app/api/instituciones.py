"""
API Endpoints para Multi-Tenancy
Gestión de instituciones, facturación y métricas
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc
from typing import List, Optional
from datetime import datetime, timedelta
from uuid import UUID
import secrets

from app.core.database import get_db
from app.core.tenant import (
    get_current_tenant_id,
    get_current_institucion,
    require_super_admin,
    verificar_limite_usuarios,
    verificar_limite_pacientes,
    TenantFilter,
)
from app.models.institucion import (
    Institucion,
    MetricaUso,
    FacturaInstitucion,
    ConfiguracionModulo,
    EstadoInstitucion,
    PlanSuscripcion,
)
from app.schemas.institucion import (
    InstitucionCreate,
    InstitucionUpdate,
    InstitucionResponse,
    InstitucionResumen,
    MetricaUsoCreate,
    MetricaUsoResponse,
    ResumenUso,
    FacturaCreate,
    FacturaUpdate,
    FacturaResponse,
    ResumenFacturacion,
    ConfiguracionModuloCreate,
    ConfiguracionModuloUpdate,
    ConfiguracionModuloResponse,
    EstadisticasInstitucion,
    DashboardMultiTenant,
)

router = APIRouter(tags=["Multi-Tenancy"])


# ============================================================================
# GESTIÓN DE INSTITUCIONES (Solo Super Admin)
# ============================================================================


@router.post(
    "/", response_model=InstitucionResponse, status_code=status.HTTP_201_CREATED
)
async def crear_institucion(
    institucion: InstitucionCreate,
    db: AsyncSession = Depends(get_db),
    _super_admin=Depends(require_super_admin),
):
    """Crear nueva institución (Solo Super Admin)"""

    # Verificar que el código no exista
    result = await db.execute(
        select(Institucion).where(Institucion.codigo == institucion.codigo.lower())
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El código de institución ya existe",
        )

    # Verificar RFC único si se proporciona
    if institucion.rfc:
        result = await db.execute(
            select(Institucion).where(Institucion.rfc == institucion.rfc)
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El RFC ya está registrado",
            )

    # Calcular fecha de fin de prueba (30 días)
    fecha_fin_prueba = datetime.utcnow() + timedelta(days=30)

    # Crear institución
    nueva_institucion = Institucion(
        **institucion.model_dump(),
        estado=EstadoInstitucion.PRUEBA,
        fecha_fin_prueba=fecha_fin_prueba,
    )

    db.add(nueva_institucion)
    await db.commit()
    await db.refresh(nueva_institucion)

    return nueva_institucion


@router.get("/", response_model=List[InstitucionResumen])
async def listar_instituciones(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    estado: Optional[EstadoInstitucion] = None,
    plan: Optional[PlanSuscripcion] = None,
    activa: Optional[bool] = None,
    buscar: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    _super_admin=Depends(require_super_admin),
):
    """Listar todas las instituciones (Solo Super Admin)"""

    query = select(Institucion)

    # Filtros
    if estado:
        query = query.where(Institucion.estado == estado)
    if plan:
        query = query.where(Institucion.plan == plan)
    if activa is not None:
        query = query.where(Institucion.activa == activa)
    if buscar:
        query = query.where(
            or_(
                Institucion.nombre.ilike(f"%{buscar}%"),
                Institucion.codigo.ilike(f"%{buscar}%"),
                Institucion.razon_social.ilike(f"%{buscar}%"),
            )
        )

    query = query.offset(skip).limit(limit).order_by(Institucion.nombre)

    result = await db.execute(query)
    instituciones = result.scalars().all()

    return instituciones


@router.get("/{institucion_id}", response_model=InstitucionResponse)
async def obtener_institucion(
    institucion_id: UUID,
    db: AsyncSession = Depends(get_db),
    _super_admin=Depends(require_super_admin),
):
    """Obtener detalles de una institución (Solo Super Admin)"""

    result = await db.execute(
        select(Institucion).where(Institucion.id == institucion_id)
    )
    institucion = result.scalar_one_or_none()

    if not institucion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Institución no encontrada"
        )

    return institucion


@router.put("/{institucion_id}", response_model=InstitucionResponse)
async def actualizar_institucion(
    institucion_id: UUID,
    institucion_update: InstitucionUpdate,
    db: AsyncSession = Depends(get_db),
    _super_admin=Depends(require_super_admin),
):
    """Actualizar institución (Solo Super Admin)"""

    result = await db.execute(
        select(Institucion).where(Institucion.id == institucion_id)
    )
    institucion = result.scalar_one_or_none()

    if not institucion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Institución no encontrada"
        )

    # Actualizar campos
    for key, value in institucion_update.model_dump(exclude_unset=True).items():
        setattr(institucion, key, value)

    await db.commit()
    await db.refresh(institucion)

    return institucion


@router.delete("/{institucion_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_institucion(
    institucion_id: UUID,
    db: AsyncSession = Depends(get_db),
    _super_admin=Depends(require_super_admin),
):
    """Eliminar institución (Solo Super Admin)"""

    result = await db.execute(
        select(Institucion).where(Institucion.id == institucion_id)
    )
    institucion = result.scalar_one_or_none()

    if not institucion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Institución no encontrada"
        )

    await db.delete(institucion)
    await db.commit()


# ============================================================================
# INFORMACIÓN DE LA INSTITUCIÓN ACTUAL
# ============================================================================


@router.get("/mi-institucion/info", response_model=InstitucionResponse)
async def obtener_mi_institucion(
    institucion: Institucion = Depends(get_current_institucion),
):
    """Obtener información de la institución del usuario actual"""
    return institucion


@router.put("/mi-institucion/configuracion", response_model=InstitucionResponse)
async def actualizar_configuracion_institucion(
    configuracion: dict,
    institucion: Institucion = Depends(get_current_institucion),
    db: AsyncSession = Depends(get_db),
):
    """Actualizar configuración de la institución actual"""

    # Merge con configuración existente
    config_actual = institucion.configuracion or {}
    config_actual.update(configuracion)

    institucion.configuracion = config_actual

    await db.commit()
    await db.refresh(institucion)

    return institucion


# ============================================================================
# MÉTRICAS DE USO
# ============================================================================


@router.post(
    "/metricas", response_model=MetricaUsoResponse, status_code=status.HTTP_201_CREATED
)
async def registrar_metrica_uso(
    metrica: MetricaUsoCreate,
    db: AsyncSession = Depends(get_db),
    _super_admin=Depends(require_super_admin),
):
    """Registrar métrica de uso (Solo Super Admin - llamado por sistema)"""

    nueva_metrica = MetricaUso(**metrica.model_dump())
    db.add(nueva_metrica)
    await db.commit()
    await db.refresh(nueva_metrica)

    return nueva_metrica


@router.get("/metricas/{institucion_id}", response_model=List[MetricaUsoResponse])
async def obtener_metricas_institucion(
    institucion_id: UUID,
    fecha_inicio: Optional[datetime] = None,
    fecha_fin: Optional[datetime] = None,
    tipo_periodo: str = "diario",
    db: AsyncSession = Depends(get_db),
    _super_admin=Depends(require_super_admin),
):
    """Obtener métricas de uso de una institución"""

    query = select(MetricaUso).where(
        and_(
            MetricaUso.institucion_id == institucion_id,
            MetricaUso.tipo_periodo == tipo_periodo,
        )
    )

    if fecha_inicio:
        query = query.where(MetricaUso.fecha >= fecha_inicio)
    if fecha_fin:
        query = query.where(MetricaUso.fecha <= fecha_fin)

    query = query.order_by(MetricaUso.fecha.desc())

    result = await db.execute(query)
    metricas = result.scalars().all()

    return metricas


@router.get("/mi-institucion/resumen-uso", response_model=ResumenUso)
async def obtener_resumen_uso(
    dias: int = Query(30, ge=1, le=365),
    institucion: Institucion = Depends(get_current_institucion),
    db: AsyncSession = Depends(get_db),
):
    """Obtener resumen de uso de la institución actual"""

    fecha_fin = datetime.utcnow()
    fecha_inicio = fecha_fin - timedelta(days=dias)

    # Obtener métricas del período
    result = await db.execute(
        select(MetricaUso).where(
            and_(
                MetricaUso.institucion_id == institucion.id,
                MetricaUso.fecha >= fecha_inicio,
                MetricaUso.fecha <= fecha_fin,
            )
        )
    )
    metricas = result.scalars().all()

    # Calcular totales
    total_usuarios = max([m.usuarios_activos for m in metricas], default=0)
    total_pacientes = sum([m.pacientes_nuevos for m in metricas], default=0)
    total_consultas = sum([m.consultas_realizadas for m in metricas], default=0)
    total_estudios = sum(
        [m.estudios_laboratorio + m.estudios_imagenes for m in metricas], default=0
    )
    almacenamiento_total = max([m.almacenamiento_gb for m in metricas], default=0)

    # Calcular tendencias (comparar con período anterior)
    fecha_inicio_anterior = fecha_inicio - timedelta(days=dias)
    result_anterior = await db.execute(
        select(MetricaUso).where(
            and_(
                MetricaUso.institucion_id == institucion.id,
                MetricaUso.fecha >= fecha_inicio_anterior,
                MetricaUso.fecha < fecha_inicio,
            )
        )
    )
    metricas_anterior = result_anterior.scalars().all()

    total_usuarios_anterior = max(
        [m.usuarios_activos for m in metricas_anterior], default=1
    )
    total_pacientes_anterior = sum(
        [m.pacientes_nuevos for m in metricas_anterior], default=1
    )
    total_consultas_anterior = sum(
        [m.consultas_realizadas for m in metricas_anterior], default=1
    )

    tendencia_usuarios = (
        ((total_usuarios - total_usuarios_anterior) / total_usuarios_anterior * 100)
        if total_usuarios_anterior > 0
        else 0
    )
    tendencia_pacientes = (
        ((total_pacientes - total_pacientes_anterior) / total_pacientes_anterior * 100)
        if total_pacientes_anterior > 0
        else 0
    )
    tendencia_consultas = (
        ((total_consultas - total_consultas_anterior) / total_consultas_anterior * 100)
        if total_consultas_anterior > 0
        else 0
    )

    return ResumenUso(
        periodo_inicio=fecha_inicio,
        periodo_fin=fecha_fin,
        total_usuarios=total_usuarios,
        total_pacientes=total_pacientes,
        total_consultas=total_consultas,
        total_estudios=total_estudios,
        almacenamiento_total_gb=float(almacenamiento_total),
        tendencia_usuarios=round(tendencia_usuarios, 2),
        tendencia_pacientes=round(tendencia_pacientes, 2),
        tendencia_consultas=round(tendencia_consultas, 2),
    )


# ============================================================================
# FACTURACIÓN
# ============================================================================


@router.post(
    "/facturas", response_model=FacturaResponse, status_code=status.HTTP_201_CREATED
)
async def crear_factura(
    factura: FacturaCreate,
    db: AsyncSession = Depends(get_db),
    _super_admin=Depends(require_super_admin),
):
    """Crear factura para una institución (Solo Super Admin)"""

    # Generar número de factura único
    numero_factura = (
        f"FAC-{datetime.utcnow().strftime('%Y%m')}-{secrets.token_hex(4).upper()}"
    )

    nueva_factura = FacturaInstitucion(
        **factura.model_dump(),
        numero_factura=numero_factura,
    )

    db.add(nueva_factura)
    await db.commit()
    await db.refresh(nueva_factura)

    return nueva_factura


@router.get("/facturas/{institucion_id}", response_model=List[FacturaResponse])
async def listar_facturas_institucion(
    institucion_id: UUID,
    estado: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    _super_admin=Depends(require_super_admin),
):
    """Listar facturas de una institución"""

    query = select(FacturaInstitucion).where(
        FacturaInstitucion.institucion_id == institucion_id
    )

    if estado:
        query = query.where(FacturaInstitucion.estado == estado)

    query = (
        query.order_by(desc(FacturaInstitucion.fecha_emision)).offset(skip).limit(limit)
    )

    result = await db.execute(query)
    facturas = result.scalars().all()

    return facturas


@router.get("/mi-institucion/facturas", response_model=List[FacturaResponse])
async def obtener_mis_facturas(
    estado: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    institucion: Institucion = Depends(get_current_institucion),
    db: AsyncSession = Depends(get_db),
):
    """Obtener facturas de la institución actual"""

    query = select(FacturaInstitucion).where(
        FacturaInstitucion.institucion_id == institucion.id
    )

    if estado:
        query = query.where(FacturaInstitucion.estado == estado)

    query = (
        query.order_by(desc(FacturaInstitucion.fecha_emision)).offset(skip).limit(limit)
    )

    result = await db.execute(query)
    facturas = result.scalars().all()

    return facturas


@router.put("/facturas/{factura_id}", response_model=FacturaResponse)
async def actualizar_factura(
    factura_id: UUID,
    factura_update: FacturaUpdate,
    db: AsyncSession = Depends(get_db),
    _super_admin=Depends(require_super_admin),
):
    """Actualizar factura"""

    result = await db.execute(
        select(FacturaInstitucion).where(FacturaInstitucion.id == factura_id)
    )
    factura = result.scalar_one_or_none()

    if not factura:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Factura no encontrada"
        )

    for key, value in factura_update.model_dump(exclude_unset=True).items():
        setattr(factura, key, value)

    await db.commit()
    await db.refresh(factura)

    return factura


@router.get("/mi-institucion/resumen-facturacion", response_model=ResumenFacturacion)
async def obtener_resumen_facturacion(
    institucion: Institucion = Depends(get_current_institucion),
    db: AsyncSession = Depends(get_db),
):
    """Obtener resumen de facturación de la institución actual"""

    # Obtener todas las facturas
    result = await db.execute(
        select(FacturaInstitucion).where(
            FacturaInstitucion.institucion_id == institucion.id
        )
    )
    facturas = result.scalars().all()

    total_facturado = sum([f.total for f in facturas])
    total_cobrado = sum([f.total for f in facturas if f.estado == "pagada"])
    total_pendiente = sum([f.total for f in facturas if f.estado == "pendiente"])
    facturas_vencidas = len(
        [
            f
            for f in facturas
            if f.estado == "pendiente" and f.fecha_vencimiento < datetime.utcnow()
        ]
    )

    # Calcular MRR (Monthly Recurring Revenue)
    # Asumiendo que el plan tiene un costo mensual
    precios_plan = {
        PlanSuscripcion.BASICO: 1000,
        PlanSuscripcion.PROFESIONAL: 5000,
        PlanSuscripcion.EMPRESARIAL: 15000,
        PlanSuscripcion.PERSONALIZADO: 0,
    }
    mrr = precios_plan.get(institucion.plan, 0)

    return ResumenFacturacion(
        total_facturado=float(total_facturado),
        total_cobrado=float(total_cobrado),
        total_pendiente=float(total_pendiente),
        facturas_vencidas=facturas_vencidas,
        proxima_facturacion=institucion.fecha_renovacion,
        mrr=float(mrr),
    )


# ============================================================================
# CONFIGURACIÓN DE MÓDULOS
# ============================================================================


@router.post(
    "/modulos",
    response_model=ConfiguracionModuloResponse,
    status_code=status.HTTP_201_CREATED,
)
async def crear_configuracion_modulo(
    config: ConfiguracionModuloCreate,
    db: AsyncSession = Depends(get_db),
    _super_admin=Depends(require_super_admin),
):
    """Crear configuración de módulo para una institución"""

    nueva_config = ConfiguracionModulo(**config.model_dump())
    db.add(nueva_config)
    await db.commit()
    await db.refresh(nueva_config)

    return nueva_config


@router.get("/mi-institucion/modulos", response_model=List[ConfiguracionModuloResponse])
async def obtener_configuraciones_modulos(
    institucion: Institucion = Depends(get_current_institucion),
    db: AsyncSession = Depends(get_db),
):
    """Obtener configuraciones de módulos de la institución actual"""

    result = await db.execute(
        select(ConfiguracionModulo).where(
            ConfiguracionModulo.institucion_id == institucion.id
        )
    )
    configuraciones = result.scalars().all()

    return configuraciones


# ============================================================================
# DASHBOARD MULTI-TENANT (Solo Super Admin)
# ============================================================================


@router.get("/dashboard/estadisticas", response_model=DashboardMultiTenant)
async def obtener_dashboard_multitenant(
    db: AsyncSession = Depends(get_db),
    _super_admin=Depends(require_super_admin),
):
    """Obtener dashboard completo multi-tenant (Solo Super Admin)"""

    # Contar instituciones por estado
    result = await db.execute(select(func.count(Institucion.id)))
    total_instituciones = result.scalar()

    result = await db.execute(
        select(func.count(Institucion.id)).where(
            Institucion.estado == EstadoInstitucion.ACTIVA
        )
    )
    instituciones_activas = result.scalar()

    result = await db.execute(
        select(func.count(Institucion.id)).where(
            Institucion.estado == EstadoInstitucion.PRUEBA
        )
    )
    instituciones_prueba = result.scalar()

    result = await db.execute(
        select(func.count(Institucion.id)).where(
            Institucion.estado == EstadoInstitucion.SUSPENDIDA
        )
    )
    instituciones_suspendidas = result.scalar()

    # Métricas globales
    result = await db.execute(
        select(
            func.sum(Institucion.usuarios_activos),
            func.sum(Institucion.pacientes_registrados),
            func.sum(Institucion.almacenamiento_usado_gb),
        )
    )
    totales = result.one()

    total_usuarios = totales[0] or 0
    total_pacientes = totales[1] or 0
    total_almacenamiento = float(totales[2] or 0)

    # Calcular MRR y ARR
    result = await db.execute(select(Institucion))
    instituciones = result.scalars().all()

    precios_plan = {
        PlanSuscripcion.BASICO: 1000,
        PlanSuscripcion.PROFESIONAL: 5000,
        PlanSuscripcion.EMPRESARIAL: 15000,
    }

    mrr_total = sum(
        [
            precios_plan.get(i.plan, 0)
            for i in instituciones
            if i.estado == EstadoInstitucion.ACTIVA
        ]
    )
    arr_total = mrr_total * 12

    # Ingresos del mes (facturas pagadas)
    mes_actual_inicio = datetime.utcnow().replace(
        day=1, hour=0, minute=0, second=0, microsecond=0
    )
    mes_anterior_inicio = (mes_actual_inicio - timedelta(days=1)).replace(day=1)

    result = await db.execute(
        select(func.sum(FacturaInstitucion.total)).where(
            and_(
                FacturaInstitucion.estado == "pagada",
                FacturaInstitucion.fecha_pago >= mes_actual_inicio,
            )
        )
    )
    ingresos_mes_actual = float(result.scalar() or 0)

    result = await db.execute(
        select(func.sum(FacturaInstitucion.total)).where(
            and_(
                FacturaInstitucion.estado == "pagada",
                FacturaInstitucion.fecha_pago >= mes_anterior_inicio,
                FacturaInstitucion.fecha_pago < mes_actual_inicio,
            )
        )
    )
    ingresos_mes_anterior = float(result.scalar() or 0)

    crecimiento_ingresos = (
        ((ingresos_mes_actual - ingresos_mes_anterior) / ingresos_mes_anterior * 100)
        if ingresos_mes_anterior > 0
        else 0
    )

    # Top instituciones (simplificado)
    top_instituciones = []

    # Alertas
    instituciones_limite_usuarios = [
        i.id for i in instituciones if i.usuarios_activos >= i.max_usuarios * 0.9
    ]
    instituciones_limite_almacenamiento = [
        i.id
        for i in instituciones
        if float(i.almacenamiento_usado_gb) >= i.max_almacenamiento_gb * 0.9
    ]

    result = await db.execute(
        select(func.count(FacturaInstitucion.id)).where(
            and_(
                FacturaInstitucion.estado == "pendiente",
                FacturaInstitucion.fecha_vencimiento < datetime.utcnow(),
            )
        )
    )
    facturas_vencidas = result.scalar() or 0

    proximos_30_dias = datetime.utcnow() + timedelta(days=30)
    result = await db.execute(
        select(func.count(Institucion.id)).where(
            and_(
                Institucion.fecha_renovacion.isnot(None),
                Institucion.fecha_renovacion <= proximos_30_dias,
            )
        )
    )
    renovaciones_proximas = result.scalar() or 0

    return DashboardMultiTenant(
        total_instituciones=total_instituciones,
        instituciones_activas=instituciones_activas,
        instituciones_prueba=instituciones_prueba,
        instituciones_suspendidas=instituciones_suspendidas,
        total_usuarios=total_usuarios,
        total_pacientes=total_pacientes,
        total_almacenamiento_gb=total_almacenamiento,
        mrr_total=float(mrr_total),
        arr_total=float(arr_total),
        ingresos_mes_actual=ingresos_mes_actual,
        ingresos_mes_anterior=ingresos_mes_anterior,
        crecimiento_ingresos_pct=round(crecimiento_ingresos, 2),
        top_instituciones_por_uso=[],
        top_instituciones_por_ingresos=[],
        instituciones_limite_usuarios=instituciones_limite_usuarios,
        instituciones_limite_almacenamiento=instituciones_limite_almacenamiento,
        facturas_vencidas=facturas_vencidas,
        renovaciones_proximas=renovaciones_proximas,
    )
