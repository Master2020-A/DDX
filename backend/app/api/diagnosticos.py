from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Dict, Any
from uuid import UUID
import io
from app.core.database import get_db
from app.models.diagnostico import Diagnostico
from app.models.paciente import Paciente
from app.models.usuario import Usuario
from app.schemas.diagnostico import DiagnosticoCreate, DiagnosticoResponse
from app.api.dependencies import get_current_active_medico
from app.services.diagnostico_sugerido import DiagnosticoSugeridoService
from app.services.generador_pdf_diagnostico import GeneradorPDFDiagnostico

router = APIRouter()


@router.post("/", response_model=DiagnosticoResponse, status_code=status.HTTP_201_CREATED)
async def crear_diagnostico(
    diagnostico_data: DiagnosticoCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_medico)
):
    """
    Crear un nuevo diagnóstico o pre-diagnóstico.
    """
    nuevo_diagnostico = Diagnostico(
        **diagnostico_data.model_dump(),
        medico_id=current_user.id
    )
    
    db.add(nuevo_diagnostico)
    await db.commit()
    await db.refresh(nuevo_diagnostico)
    
    return nuevo_diagnostico


@router.get("/consulta/{consulta_id}", response_model=List[DiagnosticoResponse])
async def listar_diagnosticos_consulta(
    consulta_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_medico)
):
    """
    Listar todos los diagnósticos de una consulta.
    """
    result = await db.execute(
        select(Diagnostico)
        .where(Diagnostico.consulta_id == consulta_id)
        .order_by(Diagnostico.created_at.desc())
    )
    diagnosticos = result.scalars().all()
    return diagnosticos


@router.get("/{diagnostico_id}", response_model=DiagnosticoResponse)
async def obtener_diagnostico(
    diagnostico_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_medico)
):
    """
    Obtener detalles de un diagnóstico específico.
    """
    result = await db.execute(
        select(Diagnostico).where(Diagnostico.id == diagnostico_id)
    )
    diagnostico = result.scalar_one_or_none()
    
    if not diagnostico:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Diagnóstico no encontrado"
        )
    
    return diagnostico


@router.patch("/{diagnostico_id}/estado/{nuevo_estado}", response_model=DiagnosticoResponse)
async def actualizar_estado_diagnostico(
    diagnostico_id: UUID,
    nuevo_estado: str,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_medico)
):
    """
    Actualizar el estado de un diagnóstico (activo, confirmado, descartado).
    """
    result = await db.execute(
        select(Diagnostico).where(Diagnostico.id == diagnostico_id)
    )
    diagnostico = result.scalar_one_or_none()
    
    if not diagnostico:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Diagnóstico no encontrado"
        )
    
    # Validate state
    from app.models.diagnostico import EstadoDiagnosticoEnum
    try:
        estado_enum = EstadoDiagnosticoEnum(nuevo_estado)
        diagnostico.estado = estado_enum
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Estado inválido. Debe ser: activo, confirmado o descartado"
        )
    
    await db.commit()
    await db.refresh(diagnostico)
    
    return diagnostico


@router.post("/sugerido/paciente/{paciente_id}", response_model=Dict[str, Any])
async def generar_diagnostico_sugerido(
    paciente_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_medico)
):
    """
    Genera un diagnóstico sugerido basado en toda la información del paciente.
    
    Analiza:
    - Última consulta (síntomas, signos vitales, exploración)
    - Laboratorios recientes (últimos 30 días)
    - Estudios especiales recientes (EKG, EEG, Ecografías)
    - Antecedentes médicos
    
    Retorna:
    - Lista de diagnósticos diferenciales con probabilidad
    - Evidencia que soporta cada diagnóstico
    - Alertas clínicas
    - Recomendaciones de estudios y tratamiento
    """
    try:
        servicio = DiagnosticoSugeridoService(db)
        resultado = await servicio.generar_diagnostico_sugerido(paciente_id)
        return resultado
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al generar diagnóstico sugerido: {str(e)}"
        )


@router.post("/sugerido/paciente/{paciente_id}/pdf")
async def generar_pdf_diagnostico_sugerido(
    paciente_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_medico)
):
    """
    Genera un PDF del diagnóstico sugerido.
    """
    try:
        # Obtener paciente
        result = await db.execute(
            select(Paciente).where(Paciente.id == paciente_id)
        )
        paciente = result.scalar_one_or_none()
        
        if not paciente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Paciente no encontrado"
            )
        
        # Generar diagnóstico sugerido
        servicio = DiagnosticoSugeridoService(db)
        resultado = await servicio.generar_diagnostico_sugerido(paciente_id)
        
        # Preparar datos del paciente
        paciente_data = {
            'nombre_completo': paciente.nombre_completo,
            'numero_expediente': paciente.numero_expediente,
            'edad': paciente.edad
        }
        
        # Generar PDF
        generador_pdf = GeneradorPDFDiagnostico()
        pdf_bytes = generador_pdf.generar_pdf(resultado, paciente_data)
        
        # Retornar PDF
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=diagnostico_sugerido_{paciente.numero_expediente}.pdf"
            }
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al generar PDF: {str(e)}"
        )
