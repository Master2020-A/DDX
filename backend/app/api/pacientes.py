from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from uuid import UUID
from app.core.database import get_db
from app.models.paciente import Paciente
from app.models.usuario import Usuario
from app.schemas.paciente import PacienteCreate, PacienteResponse, PacienteUpdate
from app.api.dependencies import get_current_user
from typing import Optional as OptionalType
import random
import string

router = APIRouter()


def _require_institucion(current_user: Usuario) -> UUID:
    if not current_user.institucion_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El usuario no tiene una institución asignada",
        )
    return current_user.institucion_id


async def _get_paciente_institucion(
    paciente_id: UUID, institucion_id: UUID, db: AsyncSession
) -> Paciente:
    result = await db.execute(
        select(Paciente).where(
            Paciente.id == paciente_id, Paciente.institucion_id == institucion_id
        )
    )
    paciente = result.scalar_one_or_none()
    if not paciente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paciente no encontrado",
        )
    return paciente


def generar_numero_expediente() -> str:
    """Genera un número base de expediente."""
    year = datetime.now().strftime("%Y")
    random_part = "".join(random.choices(string.digits, k=6))
    return f"EXP-{year}-{random_part}"


async def generar_numero_expediente_unico(
    db: AsyncSession, institucion_id: UUID
) -> str:
    while True:
        numero = generar_numero_expediente()
        result = await db.execute(
            select(Paciente).where(
                Paciente.institucion_id == institucion_id,
                Paciente.numero_expediente == numero,
            )
        )
        if result.scalar_one_or_none() is None:
            return numero


@router.post("/", response_model=PacienteResponse, status_code=status.HTTP_201_CREATED)
async def crear_paciente(
    paciente_data: PacienteCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Crear un nuevo paciente en el sistema.
    """
    institucion_id = _require_institucion(current_user)
    numero_expediente = await generar_numero_expediente_unico(db, institucion_id)

    nuevo_paciente = Paciente(
        numero_expediente=numero_expediente,
        institucion_id=institucion_id,
        **paciente_data.model_dump(),
    )

    db.add(nuevo_paciente)
    await db.commit()
    await db.refresh(nuevo_paciente)

    return nuevo_paciente


@router.get("/", response_model=List[PacienteResponse])
async def listar_pacientes(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Listar todos los pacientes con paginación.
    Accesible para todos los usuarios autenticados.
    """
    institucion_id = _require_institucion(current_user)
    query = (
        select(Paciente)
        .where(Paciente.institucion_id == institucion_id)
        .offset(skip)
        .limit(limit)
        .order_by(Paciente.created_at.desc())
    )
    result = await db.execute(query)
    pacientes = result.scalars().all()
    return pacientes


@router.get("/basico", response_model=List[PacienteResponse])
async def listar_pacientes_basico(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Listar pacientes básico - para selectores y formularios.
    Requiere autenticación.
    """
    try:
        institucion_id = _require_institucion(current_user)
        result = await db.execute(
            select(Paciente)
            .where(Paciente.institucion_id == institucion_id)
            .limit(100)
            .order_by(Paciente.nombre_completo)
        )
        pacientes = result.scalars().all()
        return pacientes
    except Exception as e:
        print(f"Error al listar pacientes: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener pacientes: {str(e)}",
        )


@router.get("/{paciente_id}", response_model=PacienteResponse)
async def obtener_paciente(
    paciente_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Obtener información de un paciente por ID.
    """
    institucion_id = _require_institucion(current_user)
    paciente = await _get_paciente_institucion(paciente_id, institucion_id, db)
    return paciente


@router.put("/{paciente_id}", response_model=PacienteResponse)
async def actualizar_paciente(
    paciente_id: UUID,
    paciente_data: PacienteUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Actualizar información de un paciente.
    """
    institucion_id = _require_institucion(current_user)
    paciente = await _get_paciente_institucion(paciente_id, institucion_id, db)

    # Update only provided fields
    update_data = paciente_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(paciente, field, value)

    await db.commit()
    await db.refresh(paciente)

    return paciente


@router.get("/buscar/{numero_expediente}", response_model=PacienteResponse)
async def buscar_por_expediente(
    numero_expediente: str,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Buscar paciente por número de expediente.
    """
    institucion_id = _require_institucion(current_user)
    result = await db.execute(
        select(Paciente).where(
            Paciente.numero_expediente == numero_expediente,
            Paciente.institucion_id == institucion_id,
        )
    )
    paciente = result.scalar_one_or_none()

    if not paciente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Paciente no encontrado"
        )

    return paciente
