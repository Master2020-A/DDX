"""
API endpoints para Hospitalización
Incluye: Ingresos, Camas, Notas de Evolución, Indicaciones Médicas, Notas de Alta, Censo
"""

print(" RECARGANDO MÓDULO hospitalizacion.py - VERSIÓN MODIFICADA")
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload
from typing import List, Optional
from uuid import UUID
from datetime import datetime, timedelta

from app.core.database import get_db
from app.api.dependencies import get_current_user, get_current_active_medico
from app.models.usuario import Usuario
from app.models.hospitalizacion import (
    Hospitalizacion,
    Cama,
    NotaEvolucion,
    IndicacionMedica,
    NotaAlta,
)
from app.models.paciente import Paciente
from app.schemas.hospitalizacion import (
    HospitalizacionCreate,
    HospitalizacionUpdate,
    HospitalizacionResponse,
    CamaCreate,
    CamaUpdate,
    CamaResponse,
    NotaEvolucionCreate,
    NotaEvolucionUpdate,
    NotaEvolucionResponse,
    IndicacionMedicaCreate,
    IndicacionMedicaUpdate,
    IndicacionMedicaResponse,
    NotaAltaCreate,
    NotaAltaUpdate,
    NotaAltaResponse,
    CensoHospitalarioResponse,
)

router = APIRouter(prefix="/hospitalizacion", tags=["Hospitalización"])


# ==================== HOSPITALIZACIÓN ====================


@router.post(
    "/", status_code=status.HTTP_201_CREATED, response_model=HospitalizacionResponse
)
async def crear_hospitalizacion(
    data: HospitalizacionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_medico),
):
    """Crear un nuevo ingreso hospitalario"""

    # Verificar que el paciente existe
    result = await db.execute(select(Paciente).where(Paciente.id == data.paciente_id))
    paciente = result.scalar_one_or_none()
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")

    # Crear hospitalización
    hospitalizacion = Hospitalizacion(
        **data.model_dump(), medico_responsable_id=current_user.id, estado="activo"
    )

    # Si se asignó una cama, marcarla como ocupada
    if data.numero_cama:
        result_cama = await db.execute(
            select(Cama).where(Cama.numero_cama == data.numero_cama)
        )
        cama = result_cama.scalar_one_or_none()
        if cama:
            cama.estado = "ocupada"
            cama.hospitalizacion_actual_id = hospitalizacion.id

    db.add(hospitalizacion)
    await db.commit()
    await db.refresh(hospitalizacion)

    return hospitalizacion


@router.get("/", response_model=List[HospitalizacionResponse])
async def listar_hospitalizaciones(
    skip: int = Query(default=0),
    limit: int = Query(default=100),
    estado: Optional[str] = Query(default=None),
    area: Optional[str] = Query(default=None),
    paciente_id: Optional[UUID] = Query(default=None),
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Listar hospitalizaciones con filtros"""

    query = select(Hospitalizacion)

    # Aplicar filtros
    if estado:
        query = query.where(Hospitalizacion.estado == estado)
    if area:
        query = query.where(Hospitalizacion.area_hospitalizacion == area)
    if paciente_id:
        query = query.where(Hospitalizacion.paciente_id == paciente_id)

    query = query.order_by(Hospitalizacion.fecha_ingreso.desc())
    query = query.offset(skip).limit(limit)

    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{hospitalizacion_id}", response_model=HospitalizacionResponse)
async def obtener_hospitalizacion(
    hospitalizacion_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Obtener detalles de una hospitalización"""

    result = await db.execute(
        select(Hospitalizacion).where(Hospitalizacion.id == hospitalizacion_id)
    )
    hospitalizacion = result.scalar_one_or_none()

    if not hospitalizacion:
        raise HTTPException(status_code=404, detail="Hospitalización no encontrada")

    return hospitalizacion


@router.put("/{hospitalizacion_id}", response_model=HospitalizacionResponse)
async def actualizar_hospitalizacion(
    hospitalizacion_id: UUID,
    data: HospitalizacionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_medico),
):
    """Actualizar una hospitalización"""

    result = await db.execute(
        select(Hospitalizacion).where(Hospitalizacion.id == hospitalizacion_id)
    )
    hospitalizacion = result.scalar_one_or_none()

    if not hospitalizacion:
        raise HTTPException(status_code=404, detail="Hospitalización no encontrada")

    # Actualizar campos
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(hospitalizacion, field, value)

    await db.commit()
    await db.refresh(hospitalizacion)

    return hospitalizacion


@router.delete("/{hospitalizacion_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_hospitalizacion(
    hospitalizacion_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_medico),
):
    """Eliminar una hospitalización"""

    result = await db.execute(
        select(Hospitalizacion).where(Hospitalizacion.id == hospitalizacion_id)
    )
    hospitalizacion = result.scalar_one_or_none()

    if not hospitalizacion:
        raise HTTPException(status_code=404, detail="Hospitalización no encontrada")

    # Liberar cama si está asignada
    if hospitalizacion.numero_cama:
        result_cama = await db.execute(
            select(Cama).where(Cama.numero_cama == hospitalizacion.numero_cama)
        )
        cama = result_cama.scalar_one_or_none()
        if cama and cama.hospitalizacion_actual_id == hospitalizacion_id:
            cama.estado = "disponible"
            cama.hospitalizacion_actual_id = None

    await db.delete(hospitalizacion)
    await db.commit()


# ==================== CAMAS ====================


@router.get("/camas/test")
async def test_camas_endpoint():
    """Endpoint de prueba para verificar que el módulo se recargó"""
    return {
        "status": "OK",
        "message": "Módulo hospitalizacion.py cargado correctamente - VERSIÓN MODIFICADA",
        "timestamp": datetime.now().isoformat(),
    }


@router.post("/camas", status_code=status.HTTP_201_CREATED, response_model=CamaResponse)
async def crear_cama(
    data: CamaCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_medico),
):
    """Registrar una nueva cama"""

    # Verificar que no exista una cama con el mismo número
    result = await db.execute(select(Cama).where(Cama.numero_cama == data.numero_cama))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=400, detail="Ya existe una cama con este número"
        )

    cama = Cama(**data.model_dump())
    db.add(cama)
    await db.commit()
    await db.refresh(cama)

    return cama


@router.get("/camas")
async def listar_camas(
    skip: int = Query(default=0),
    limit: int = Query(default=100),
    estado: Optional[str] = Query(default=None),
    area: Optional[str] = Query(default=None),
    disponibles: Optional[bool] = Query(default=None),
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Listar camas con filtros - SIN VALIDACION TEMPORAL"""

    query = select(Cama)

    if estado:
        query = query.where(Cama.estado == estado)
    if area:
        query = query.where(Cama.area == area)
    if disponibles is not None:
        if disponibles:
            query = query.where(Cama.estado == "disponible")
        else:
            query = query.where(Cama.estado != "disponible")

    query = query.order_by(Cama.area, Cama.numero_cama)
    query = query.offset(skip).limit(limit)

    result = await db.execute(query)
    camas = result.scalars().all()

    # Convertir a dict para ver todos los campos
    camas_dict = []
    for cama in camas:
        cama_dict = {
            "id": str(cama.id),
            "numero_cama": cama.numero_cama,
            "area": cama.area,
            "piso": cama.piso,
            "habitacion": cama.habitacion,
            "estado": cama.estado,
            "tipo_cama": cama.tipo_cama,
            "tiene_oxigeno": cama.tiene_oxigeno,
            "tiene_monitor": cama.tiene_monitor,
            "tiene_ventilador": cama.tiene_ventilador,
            "capacidad_peso": cama.capacidad_peso,
            "hospitalizacion_actual_id": (
                str(cama.hospitalizacion_actual_id)
                if cama.hospitalizacion_actual_id
                else None
            ),
            "fecha_ultima_limpieza": (
                cama.fecha_ultima_limpieza.isoformat()
                if cama.fecha_ultima_limpieza
                else None
            ),
            "fecha_ultimo_mantenimiento": (
                cama.fecha_ultimo_mantenimiento.isoformat()
                if cama.fecha_ultimo_mantenimiento
                else None
            ),
            "observaciones": cama.observaciones,
            "created_at": cama.created_at.isoformat() if cama.created_at else None,
            "updated_at": cama.updated_at.isoformat() if cama.updated_at else None,
        }
        print(f"Cama dict: {cama_dict}")
        camas_dict.append(cama_dict)

    return {"camas": camas_dict, "total": len(camas_dict)}


@router.put("/camas/{cama_id}", response_model=CamaResponse)
async def actualizar_cama(
    cama_id: UUID,
    data: CamaUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_medico),
):
    """Actualizar información de una cama"""

    result = await db.execute(select(Cama).where(Cama.id == cama_id))
    cama = result.scalar_one_or_none()

    if not cama:
        raise HTTPException(status_code=404, detail="Cama no encontrada")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(cama, field, value)

    await db.commit()
    await db.refresh(cama)

    return cama


# ==================== NOTAS DE EVOLUCIÓN ====================


@router.post(
    "/notas-evolucion",
    status_code=status.HTTP_201_CREATED,
    response_model=NotaEvolucionResponse,
)
async def crear_nota_evolucion(
    data: NotaEvolucionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_medico),
):
    """Crear una nota de evolución"""

    # Verificar que la hospitalización existe y está activa
    result = await db.execute(
        select(Hospitalizacion).where(Hospitalizacion.id == data.hospitalizacion_id)
    )
    hospitalizacion = result.scalar_one_or_none()

    if not hospitalizacion:
        raise HTTPException(status_code=404, detail="Hospitalización no encontrada")

    if hospitalizacion.estado != "activo":
        raise HTTPException(status_code=400, detail="La hospitalización no está activa")

    nota = NotaEvolucion(**data.model_dump(), medico_id=current_user.id)

    db.add(nota)
    await db.commit()
    await db.refresh(nota)

    return nota


@router.get("/notas-evolucion", response_model=List[NotaEvolucionResponse])
async def listar_notas_evolucion(
    hospitalizacion_id: Optional[UUID] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Listar notas de evolución"""

    query = select(NotaEvolucion)

    if hospitalizacion_id:
        query = query.where(NotaEvolucion.hospitalizacion_id == hospitalizacion_id)

    query = query.order_by(NotaEvolucion.fecha_nota.desc())
    query = query.offset(skip).limit(limit)

    result = await db.execute(query)
    return result.scalars().all()


# ==================== INDICACIONES MÉDICAS ====================


@router.post(
    "/indicaciones",
    status_code=status.HTTP_201_CREATED,
    response_model=IndicacionMedicaResponse,
)
async def crear_indicacion(
    data: IndicacionMedicaCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_medico),
):
    """Crear una indicación médica"""

    # Verificar hospitalización
    result = await db.execute(
        select(Hospitalizacion).where(Hospitalizacion.id == data.hospitalizacion_id)
    )
    hospitalizacion = result.scalar_one_or_none()

    if not hospitalizacion:
        raise HTTPException(status_code=404, detail="Hospitalización no encontrada")

    indicacion = IndicacionMedica(**data.model_dump(), medico_id=current_user.id)

    db.add(indicacion)
    await db.commit()
    await db.refresh(indicacion)

    return indicacion


@router.get("/indicaciones", response_model=List[IndicacionMedicaResponse])
async def listar_indicaciones(
    hospitalizacion_id: Optional[UUID] = None,
    estado: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Listar indicaciones médicas"""

    query = select(IndicacionMedica)

    if hospitalizacion_id:
        query = query.where(IndicacionMedica.hospitalizacion_id == hospitalizacion_id)
    if estado:
        query = query.where(IndicacionMedica.estado == estado)

    query = query.order_by(IndicacionMedica.fecha_indicacion.desc())
    query = query.offset(skip).limit(limit)

    result = await db.execute(query)
    return result.scalars().all()


@router.put("/indicaciones/{indicacion_id}", response_model=IndicacionMedicaResponse)
async def actualizar_indicacion(
    indicacion_id: UUID,
    data: IndicacionMedicaUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_medico),
):
    """Actualizar una indicación médica"""

    result = await db.execute(
        select(IndicacionMedica).where(IndicacionMedica.id == indicacion_id)
    )
    indicacion = result.scalar_one_or_none()

    if not indicacion:
        raise HTTPException(status_code=404, detail="Indicación no encontrada")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(indicacion, field, value)

    await db.commit()
    await db.refresh(indicacion)

    return indicacion


# ==================== NOTAS DE ALTA ====================


@router.post(
    "/notas-alta", status_code=status.HTTP_201_CREATED, response_model=NotaAltaResponse
)
async def crear_nota_alta(
    data: NotaAltaCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_medico),
):
    """Crear nota de alta y dar de alta al paciente"""

    # Verificar hospitalización
    result = await db.execute(
        select(Hospitalizacion).where(Hospitalizacion.id == data.hospitalizacion_id)
    )
    hospitalizacion = result.scalar_one_or_none()

    if not hospitalizacion:
        raise HTTPException(status_code=404, detail="Hospitalización no encontrada")

    if hospitalizacion.estado != "activo":
        raise HTTPException(status_code=400, detail="La hospitalización no está activa")

    # Crear nota de alta
    nota_alta = NotaAlta(**data.model_dump(), medico_id=current_user.id)

    # Actualizar hospitalización
    hospitalizacion.estado = (
        "alta_medica" if data.tipo_alta == "medica" else data.tipo_alta
    )
    hospitalizacion.fecha_alta = datetime.now()
    hospitalizacion.diagnostico_egreso = data.diagnostico_egreso

    # Liberar cama
    if hospitalizacion.numero_cama:
        result_cama = await db.execute(
            select(Cama).where(Cama.numero_cama == hospitalizacion.numero_cama)
        )
        cama = result_cama.scalar_one_or_none()
        if cama:
            cama.estado = "limpieza"
            cama.hospitalizacion_actual_id = None

    db.add(nota_alta)
    await db.commit()
    await db.refresh(nota_alta)

    return nota_alta


@router.get("/notas-alta/{hospitalizacion_id}", response_model=NotaAltaResponse)
async def obtener_nota_alta(
    hospitalizacion_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Obtener nota de alta de una hospitalización"""

    result = await db.execute(
        select(NotaAlta).where(NotaAlta.hospitalizacion_id == hospitalizacion_id)
    )
    nota_alta = result.scalar_one_or_none()

    if not nota_alta:
        raise HTTPException(status_code=404, detail="Nota de alta no encontrada")

    return nota_alta


# ==================== CENSO HOSPITALARIO ====================


@router.get("/censo/actual", response_model=CensoHospitalarioResponse)
async def obtener_censo_hospitalario(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Obtener censo hospitalario actual"""

    # Total de hospitalizados activos
    result_total = await db.execute(
        select(func.count(Hospitalizacion.id)).where(Hospitalizacion.estado == "activo")
    )
    total_hospitalizados = result_total.scalar()

    # Por área
    result_area = await db.execute(
        select(Hospitalizacion.area_hospitalizacion, func.count(Hospitalizacion.id))
        .where(Hospitalizacion.estado == "activo")
        .group_by(Hospitalizacion.area_hospitalizacion)
    )
    por_area = {area: count for area, count in result_area.all() if area}

    # Por estado
    result_estado = await db.execute(
        select(Hospitalizacion.estado, func.count(Hospitalizacion.id)).group_by(
            Hospitalizacion.estado
        )
    )
    por_estado = {estado: count for estado, count in result_estado.all()}

    # Estadísticas de camas
    result_camas_total = await db.execute(select(func.count(Cama.id)))
    camas_totales = result_camas_total.scalar()

    result_camas_ocupadas = await db.execute(
        select(func.count(Cama.id)).where(Cama.estado == "ocupada")
    )
    camas_ocupadas = result_camas_ocupadas.scalar()

    camas_disponibles = camas_totales - camas_ocupadas
    porcentaje_ocupacion = (
        (camas_ocupadas / camas_totales * 100) if camas_totales > 0 else 0
    )

    # Hospitalizaciones recientes (últimas 10)
    result_recientes = await db.execute(
        select(Hospitalizacion)
        .where(Hospitalizacion.estado == "activo")
        .order_by(Hospitalizacion.fecha_ingreso.desc())
        .limit(10)
    )
    hospitalizaciones_recientes = result_recientes.scalars().all()

    return {
        "total_hospitalizados": total_hospitalizados,
        "por_area": por_area,
        "por_estado": por_estado,
        "camas_disponibles": camas_disponibles,
        "camas_ocupadas": camas_ocupadas,
        "camas_totales": camas_totales,
        "porcentaje_ocupacion": round(porcentaje_ocupacion, 2),
        "hospitalizaciones_recientes": hospitalizaciones_recientes,
    }
