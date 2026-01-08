"""
API Endpoints para Telemedicina
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel
from datetime import datetime, timedelta

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.usuario import Usuario as UsuarioModel
from app.models.paciente import Paciente
from app.models.telemedicina import (
    ConsultaRemota,
    MensajeChat,
    PrescripcionElectronica,
    SeguimientoPostConsulta,
    EstadoConsulta,
    EmisorTipo,
)

router = APIRouter(tags=["Telemedicina"])


# ==================== MODELOS PYDANTIC ====================


class CrearConsultaRemotaRequest(BaseModel):
    paciente_id: UUID
    fecha_programada: datetime
    motivo_consulta: str
    tipo: str = "videollamada"  # videollamada, solo_chat, telefonica


class FinalizarConsultaRequest(BaseModel):
    notas_medico: Optional[str] = None
    diagnostico_preliminar: Optional[str] = None
    plan_tratamiento: Optional[str] = None
    requiere_seguimiento: bool = False


class EnviarMensajeRequest(BaseModel):
    consulta_remota_id: UUID
    contenido: str
    tipo_mensaje: str = "texto"  # texto, imagen, archivo, sistema
    archivo_url: Optional[str] = None


class CrearSeguimientoRequest(BaseModel):
    consulta_remota_id: UUID
    paciente_id: UUID
    tipo: str  # recordatorio_medicamento, cita_control, encuesta, evolucion
    titulo: str
    mensaje: str
    fecha_programada: datetime
    metodo_notificacion: str = "email"  # email, sms, push, whatsapp


class MedicamentoReceta(BaseModel):
    nombre: str
    dosis: str
    frecuencia: str
    duracion: str
    via_administracion: str = "oral"
    indicaciones: Optional[str] = None


class GenerarPrescripcionRequest(BaseModel):
    consulta_remota_id: UUID
    paciente_id: UUID
    medicamentos: List[MedicamentoReceta]
    diagnostico: str
    codigo_cie10: Optional[str] = None
    indicaciones_generales: Optional[str] = None


class CalificarConsultaRequest(BaseModel):
    calificacion: int  # 1-5
    comentarios: Optional[str] = None


# ==================== CONSULTAS REMOTAS ====================


@router.post("/consultas", status_code=status.HTTP_201_CREATED)
async def crear_consulta_remota(
    request: CrearConsultaRemotaRequest,
    current_user: UsuarioModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    consulta = ConsultaRemota(
        paciente_id=request.paciente_id,
        medico_id=current_user.id,
        fecha_programada=request.fecha_programada,
        motivo_consulta=request.motivo_consulta,
        tipo=request.tipo,  # viene como "videollamada" del request
        estado=EstadoConsulta.PROGRAMADA.value,  # "PROGRAMADA" o lo que defina tu Enum
    )

    db.add(consulta)
    await db.commit()
    await db.refresh(consulta)

    return {
        "id": str(consulta.id),
        "paciente_id": str(consulta.paciente_id),
        "medico_id": str(consulta.medico_id),
        "sala_id": getattr(consulta, "sala_id", None),
        "estado": consulta.estado,
        "tipo": consulta.tipo,
        "fecha_programada": (
            consulta.fecha_programada.isoformat() if consulta.fecha_programada else None
        ),
        "url_sala_medico": getattr(consulta, "url_sala_medico", None),
        "url_sala_paciente": getattr(consulta, "url_sala_paciente", None),
    }


@router.get("/consultas/programadas")
async def obtener_consultas_programadas(
    current_user: UsuarioModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Obtener consultas remotas programadas del médico actual.
    Usado en tu test en PASO 4.
    """
    try:
        query = (
            select(ConsultaRemota)
            .where(
                ConsultaRemota.medico_id == current_user.id,
                ConsultaRemota.estado == EstadoConsulta.PROGRAMADA,
            )
            .order_by(ConsultaRemota.fecha_programada.desc())
        )

        result = await db.execute(query)
        consultas = result.scalars().all()

        consultas_formateadas = []
        for consulta in consultas:
            # Obtener paciente
            paciente_result = await db.execute(
                select(Paciente).where(Paciente.id == consulta.paciente_id)
            )
            paciente = paciente_result.scalar_one_or_none()

            # Obtener médico
            medico_result = await db.execute(
                select(UsuarioModel).where(UsuarioModel.id == consulta.medico_id)
            )
            medico = medico_result.scalar_one_or_none()

            consultas_formateadas.append(
                {
                    "id": str(consulta.id),
                    "sala_id": getattr(consulta, "sala_id", None),
                    "paciente": {
                        "id": str(paciente.id) if paciente else None,
                        "nombre": (
                            paciente.nombre_completo if paciente else "Desconocido"
                        ),
                    },
                    "medico": {
                        "id": str(medico.id) if medico else None,
                        "nombre": medico.nombre_completo if medico else "Desconocido",
                    },
                    "estado": consulta.estado,
                    "fecha_programada": (
                        consulta.fecha_programada.isoformat()
                        if consulta.fecha_programada
                        else None
                    ),
                    "fecha_inicio": (
                        consulta.fecha_inicio.isoformat()
                        if consulta.fecha_inicio
                        else None
                    ),
                    "fecha_fin": (
                        consulta.fecha_fin.isoformat() if consulta.fecha_fin else None
                    ),
                    "motivo_consulta": consulta.motivo_consulta,
                    "tipo": consulta.tipo,
                    "duracion_minutos": consulta.duracion_minutos,
                }
            )

        return consultas_formateadas

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener consultas programadas: {str(e)}",
        )


@router.get("/consultas-lista")
async def listar_consultas(
    db: AsyncSession = Depends(get_db),
    current_user: UsuarioModel = Depends(get_current_user),
):
    """
    Listar todas las consultas remotas del médico actual
    """
    try:
        query = (
            select(ConsultaRemota)
            .where(ConsultaRemota.medico_id == current_user.id)
            .order_by(ConsultaRemota.fecha_programada.desc())
        )

        result = await db.execute(query)
        consultas = result.scalars().all()

        consultas_formateadas = []
        for consulta in consultas:
            paciente_result = await db.execute(
                select(Paciente).where(Paciente.id == consulta.paciente_id)
            )
            paciente = paciente_result.scalar_one_or_none()

            medico_result = await db.execute(
                select(UsuarioModel).where(UsuarioModel.id == consulta.medico_id)
            )
            medico = medico_result.scalar_one_or_none()

            consultas_formateadas.append(
                {
                    "id": str(consulta.id),
                    "sala_id": getattr(consulta, "sala_id", None),
                    "paciente": {
                        "id": str(paciente.id) if paciente else None,
                        "nombre": (
                            paciente.nombre_completo if paciente else "Desconocido"
                        ),
                    },
                    "medico": {
                        "id": str(medico.id) if medico else None,
                        "nombre": medico.nombre_completo if medico else "Desconocido",
                    },
                    "estado": consulta.estado,
                    "fecha_programada": (
                        consulta.fecha_programada.isoformat()
                        if consulta.fecha_programada
                        else None
                    ),
                    "fecha_inicio": (
                        consulta.fecha_inicio.isoformat()
                        if consulta.fecha_inicio
                        else None
                    ),
                    "fecha_fin": (
                        consulta.fecha_fin.isoformat() if consulta.fecha_fin else None
                    ),
                    "motivo_consulta": consulta.motivo_consulta,
                    "tipo": consulta.tipo,
                    "duracion_minutos": consulta.duracion_minutos,
                }
            )

        return consultas_formateadas

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener consultas: {str(e)}",
        )


@router.get("/consultas/{consulta_id}")
async def obtener_consulta(
    consulta_id: UUID,
    current_user: UsuarioModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Obtener detalles de una consulta remota específica
    """
    try:
        result = await db.execute(
            select(ConsultaRemota).where(ConsultaRemota.id == consulta_id)
        )
        consulta = result.scalar_one_or_none()

        if not consulta:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Consulta no encontrada",
            )

        paciente_result = await db.execute(
            select(Paciente).where(Paciente.id == consulta.paciente_id)
        )
        paciente = paciente_result.scalar_one_or_none()

        medico_result = await db.execute(
            select(UsuarioModel).where(UsuarioModel.id == consulta.medico_id)
        )
        medico = medico_result.scalar_one_or_none()

        return {
            "id": str(consulta.id),
            "sala_id": getattr(consulta, "sala_id", None),
            "paciente": {
                "id": str(paciente.id) if paciente else None,
                "nombre": paciente.nombre_completo if paciente else "Desconocido",
            },
            "medico": {
                "id": str(medico.id) if medico else None,
                "nombre": medico.nombre_completo if medico else "Desconocido",
            },
            "estado": consulta.estado,
            "fecha_programada": (
                consulta.fecha_programada.isoformat()
                if consulta.fecha_programada
                else None
            ),
            "fecha_inicio": (
                consulta.fecha_inicio.isoformat() if consulta.fecha_inicio else None
            ),
            "fecha_fin": consulta.fecha_fin.isoformat() if consulta.fecha_fin else None,
            "motivo_consulta": consulta.motivo_consulta,
            "tipo": consulta.tipo,
            "duracion_minutos": consulta.duracion_minutos,
            "notas_medico": getattr(consulta, "notas_medico", None),
            "diagnostico": getattr(consulta, "diagnostico", None),
            "calificacion": getattr(consulta, "calificacion_paciente", None),
            "comentarios_paciente": getattr(consulta, "comentarios_paciente", None),
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener consulta: {str(e)}",
        )


@router.post("/consultas/{consulta_id}/iniciar")
async def iniciar_consulta(
    consulta_id: UUID,
    current_user: UsuarioModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Iniciar una consulta remota programada
    """
    try:
        result = await db.execute(
            select(ConsultaRemota).where(ConsultaRemota.id == consulta_id)
        )
        consulta = result.scalar_one_or_none()

        if not consulta:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Consulta no encontrada"
            )

        if (
            consulta.medico_id != current_user.id
            and current_user.rol != "admin"  # por si admin
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tiene permiso para iniciar esta consulta",
            )

        if consulta.estado != EstadoConsulta.PROGRAMADA:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"La consulta no puede iniciarse desde el estado: {consulta.estado}",
            )

        consulta.estado = EstadoConsulta.EN_CURSO
        consulta.fecha_inicio = datetime.utcnow()

        await db.commit()
        await db.refresh(consulta)

        return {
            "id": str(consulta.id),
            "estado": consulta.estado,
            "fecha_inicio": (
                consulta.fecha_inicio.isoformat() if consulta.fecha_inicio else None
            ),
            "sala_id": getattr(consulta, "sala_id", None),
            "url_sala_medico": getattr(consulta, "url_sala_medico", None),
            "url_sala_paciente": getattr(consulta, "url_sala_paciente", None),
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al iniciar consulta: {str(e)}",
        )


@router.post("/consultas/{consulta_id}/finalizar")
async def finalizar_consulta(
    consulta_id: UUID,
    request: FinalizarConsultaRequest,
    current_user: UsuarioModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Finalizar una consulta remota en curso
    """
    try:
        result = await db.execute(
            select(ConsultaRemota).where(ConsultaRemota.id == consulta_id)
        )
        consulta = result.scalar_one_or_none()

        if not consulta:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Consulta no encontrada"
            )

        if consulta.medico_id != current_user.id and current_user.rol != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tiene permiso para finalizar esta consulta",
            )

        if consulta.estado != EstadoConsulta.EN_CURSO:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"La consulta no puede finalizarse desde el estado: {consulta.estado}",
            )

        consulta.estado = EstadoConsulta.FINALIZADA
        consulta.fecha_fin = datetime.utcnow()
        consulta.notas_medico = request.notas_medico
        consulta.diagnostico_preliminar = request.diagnostico_preliminar
        consulta.plan_tratamiento = request.plan_tratamiento
        consulta.requiere_seguimiento = request.requiere_seguimiento

        if consulta.fecha_inicio:
            delta = consulta.fecha_fin - consulta.fecha_inicio
            consulta.duracion_minutos = int(delta.total_seconds() / 60)
        else:
            consulta.duracion_minutos = 0

        await db.commit()
        await db.refresh(consulta)

        return {
            "id": str(consulta.id),
            "estado": consulta.estado,
            "fecha_fin": consulta.fecha_fin.isoformat() if consulta.fecha_fin else None,
            "duracion_minutos": consulta.duracion_minutos,
            "notas_medico": consulta.notas_medico,
            "diagnostico_preliminar": consulta.diagnostico_preliminar,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            detail=f"Error al finalizar consulta: {str(e)}",
        )


@router.post("/consultas/{consulta_id}/calificar")
async def calificar_consulta(
    consulta_id: UUID,
    request: CalificarConsultaRequest,
    current_user: UsuarioModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Calificar una consulta remota finalizada (solo paciente)
    """
    result = await db.execute(
        select(ConsultaRemota).where(ConsultaRemota.id == consulta_id)
    )
    consulta = result.scalar_one_or_none()

    if not consulta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Consulta no encontrada",
        )

    if consulta.estado != EstadoConsulta.FINALIZADA:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Solo se pueden calificar consultas finalizadas",
        )

    await db.execute(
        update(ConsultaRemota)
        .where(ConsultaRemota.id == consulta_id)
        .values(
            calificacion=request.calificacion,
            comentarios_paciente=request.comentarios,
        )
    )
    await db.commit()

    return {
        "message": "Calificación guardada exitosamente",
        "calificacion": request.calificacion,
    }


# ==================== CHAT ====================


@router.post("/chat/mensaje", status_code=status.HTTP_201_CREATED)
async def enviar_mensaje(
    request: EnviarMensajeRequest,
    current_user: UsuarioModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Enviar un mensaje de chat durante la consulta
    """
    try:
        # Verificar que la consulta existe
        result = await db.execute(
            select(ConsultaRemota).where(
                ConsultaRemota.id == request.consulta_remota_id
            )
        )
        consulta = result.scalar_one_or_none()
        if not consulta:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Consulta no encontrada",
            )

        emisor_tipo = (
            EmisorTipo.MEDICO
            if current_user.rol in ("medico", "admin")
            else EmisorTipo.PACIENTE
        )

        mensaje = MensajeChat(
            consulta_remota_id=request.consulta_remota_id,
            emisor_id=current_user.id,
            emisor_tipo=emisor_tipo,
            contenido=request.contenido,
            tipo_mensaje=request.tipo_mensaje,
            archivo_url=request.archivo_url,
        )

        db.add(mensaje)
        await db.commit()
        await db.refresh(mensaje)

        return {
            "id": str(mensaje.id),
            "consulta_remota_id": str(mensaje.consulta_remota_id),
            "emisor_id": str(mensaje.emisor_id),
            "emisor_tipo": mensaje.emisor_tipo,
            "contenido": mensaje.contenido,
            "tipo_mensaje": mensaje.tipo_mensaje,
            "archivo_url": mensaje.archivo_url,
            "created_at": (
                mensaje.created_at.isoformat()
                if getattr(mensaje, "created_at", None)
                else None
            ),
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al enviar mensaje: {str(e)}",
        )


@router.get("/chat/{consulta_id}/mensajes")
async def obtener_mensajes(
    consulta_id: UUID,
    current_user: UsuarioModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Obtener todos los mensajes de una consulta
    """
    try:
        result = await db.execute(
            select(MensajeChat)
            .where(MensajeChat.consulta_remota_id == consulta_id)
            .order_by(MensajeChat.created_at.asc())
        )
        mensajes = result.scalars().all()

        return [
            {
                "id": str(msg.id),
                "consulta_remota_id": str(msg.consulta_remota_id),
                "emisor_id": str(msg.emisor_id),
                "emisor_tipo": msg.emisor_tipo,
                "contenido": msg.contenido,
                "tipo_mensaje": msg.tipo_mensaje,
                "archivo_url": msg.archivo_url,
                "leido": getattr(msg, "leido", False),
                "created_at": (
                    msg.created_at.isoformat()
                    if getattr(msg, "created_at", None)
                    else None
                ),
            }
            for msg in mensajes
        ]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener mensajes: {str(e)}",
        )


# ==================== SEGUIMIENTO ====================


@router.post("/seguimientos", status_code=status.HTTP_201_CREATED)
async def crear_seguimiento(
    request: CrearSeguimientoRequest,
    current_user: UsuarioModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Crear un seguimiento post-consulta
    """
    try:
        seguimiento = SeguimientoPostConsulta(
            consulta_remota_id=request.consulta_remota_id,
            paciente_id=request.paciente_id,
            medico_id=current_user.id,
            tipo=request.tipo,
            titulo=request.titulo,
            mensaje=request.mensaje,
            fecha_programada=request.fecha_programada,
            metodo_notificacion=request.metodo_notificacion,
        )

        db.add(seguimiento)
        await db.commit()
        await db.refresh(seguimiento)

        return {
            "id": str(seguimiento.id),
            "consulta_remota_id": (
                str(seguimiento.consulta_remota_id)
                if seguimiento.consulta_remota_id
                else None
            ),
            "paciente_id": str(seguimiento.paciente_id),
            "medico_id": str(seguimiento.medico_id),
            "tipo": seguimiento.tipo,
            "titulo": seguimiento.titulo,
            "mensaje": seguimiento.mensaje,
            "fecha_programada": (
                seguimiento.fecha_programada.isoformat()
                if seguimiento.fecha_programada
                else None
            ),
            "metodo_notificacion": seguimiento.metodo_notificacion,
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear seguimiento: {str(e)}",
        )


# ==================== PRESCRIPCIONES ====================


@router.post("/prescripciones", status_code=status.HTTP_201_CREATED)
async def generar_prescripcion(
    request: GenerarPrescripcionRequest,
    current_user: UsuarioModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Generar una prescripción electrónica durante la consulta
    """
    try:
        medicamentos_dict = [med.dict() for med in request.medicamentos]
        fecha_vigencia = datetime.utcnow() + timedelta(days=30)

        prescripcion = PrescripcionElectronica(
            consulta_remota_id=request.consulta_remota_id,
            paciente_id=request.paciente_id,
            medico_id=current_user.id,
            diagnostico=request.diagnostico,
            codigo_cie10=request.codigo_cie10,
            medicamentos=medicamentos_dict,
            indicaciones_generales=request.indicaciones_generales,
            fecha_vigencia=fecha_vigencia,
        )

        db.add(prescripcion)
        await db.commit()
        await db.refresh(prescripcion)

        return {
            "id": str(prescripcion.id),
            "numero_receta": prescripcion.numero_receta,
            "consulta_remota_id": (
                str(prescripcion.consulta_remota_id)
                if prescripcion.consulta_remota_id
                else None
            ),
            "paciente_id": str(prescripcion.paciente_id),
            "medico_id": str(prescripcion.medico_id),
            "diagnostico": prescripcion.diagnostico,
            "codigo_cie10": prescripcion.codigo_cie10,
            "medicamentos": prescripcion.medicamentos,
            "indicaciones_generales": prescripcion.indicaciones_generales,
            "fecha_emision": (
                prescripcion.fecha_emision.isoformat()
                if prescripcion.fecha_emision
                else None
            ),
            "fecha_vigencia": (
                prescripcion.fecha_vigencia.isoformat()
                if prescripcion.fecha_vigencia
                else None
            ),
            "activa": getattr(prescripcion, "activa", True),
            "codigo_verificacion": getattr(prescripcion, "codigo_verificacion", None),
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al generar prescripción: {str(e)}",
        )


@router.get("/prescripciones/{prescripcion_id}")
async def obtener_prescripcion(
    prescripcion_id: UUID,
    current_user: UsuarioModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Obtener una prescripción electrónica por ID
    """
    result = await db.execute(
        select(PrescripcionElectronica).where(
            PrescripcionElectronica.id == prescripcion_id
        )
    )
    prescripcion = result.scalar_one_or_none()

    if not prescripcion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prescripción no encontrada",
        )

    return {
        "id": str(prescripcion.id),
        "numero_receta": prescripcion.numero_receta,
        "fecha_emision": (
            prescripcion.fecha_emision.isoformat()
            if prescripcion.fecha_emision
            else None
        ),
        "fecha_vigencia": (
            prescripcion.fecha_vigencia.isoformat()
            if prescripcion.fecha_vigencia
            else None
        ),
        "medicamentos": prescripcion.medicamentos,
        "diagnostico": prescripcion.diagnostico,
        "codigo_cie10": prescripcion.codigo_cie10,
        "indicaciones_generales": prescripcion.indicaciones_generales,
        "estado": getattr(prescripcion, "estado", None),
        "pdf_url": getattr(prescripcion, "pdf_url", None),
    }
