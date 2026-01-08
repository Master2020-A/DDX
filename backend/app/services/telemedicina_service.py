# app/services/telemedicina_service.py

from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from datetime import datetime, timedelta
from typing import Optional, List
from uuid import UUID

from app.models.telemedicina import (
    ConsultaRemota,
    MensajeChat,
    PrescripcionElectronica,
    SeguimientoPostConsulta,
    EstadoConsulta,
    EmisorTipo,
)
from app.models.usuario import Usuario
from app.models.paciente import Paciente
from app.schemas.telemedicina import (
    ConsultaRemotaCreate,
    ConsultaRemotaUpdate,
    MensajeChatCreate,
    PrescripcionCreate,
    SeguimientoCreate,
    FinalizarConsultaRequest,
)


class TelemedicinaService:
    """Servicio para manejar la lógica de telemedicina"""

    def __init__(self, db: Session):
        self.db = db

    # ========================================
    # CONSULTAS REMOTAS
    # ========================================

    def crear_consulta(
        self, data: ConsultaRemotaCreate, medico_id: UUID
    ) -> ConsultaRemota:
        """Crear una nueva consulta remota"""
        consulta = ConsultaRemota(
            paciente_id=data.paciente_id,
            medico_id=data.medico_id or medico_id,
            fecha_programada=data.fecha_programada,
            motivo_consulta=data.motivo_consulta,
            tipo=data.tipo,
            estado=EstadoConsulta.PROGRAMADA,
        )

        self.db.add(consulta)
        self.db.commit()
        self.db.refresh(consulta)

        return consulta

    def obtener_consulta(self, consulta_id: UUID) -> Optional[ConsultaRemota]:
        """Obtener una consulta por ID"""
        return (
            self.db.query(ConsultaRemota)
            .filter(ConsultaRemota.id == consulta_id)
            .first()
        )

    def listar_consultas_programadas(
        self,
        medico_id: Optional[UUID] = None,
        fecha_inicio: Optional[datetime] = None,
        fecha_fin: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> List[ConsultaRemota]:
        """Listar consultas programadas con filtros"""
        query = self.db.query(ConsultaRemota).filter(
            ConsultaRemota.estado == EstadoConsulta.PROGRAMADA
        )

        if medico_id:
            query = query.filter(ConsultaRemota.medico_id == medico_id)

        if fecha_inicio:
            query = query.filter(ConsultaRemota.fecha_programada >= fecha_inicio)

        if fecha_fin:
            query = query.filter(ConsultaRemota.fecha_programada <= fecha_fin)

        return (
            query.order_by(ConsultaRemota.fecha_programada.asc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def listar_consultas_hoy(self, medico_id: UUID) -> List[ConsultaRemota]:
        """Listar consultas de hoy"""
        hoy = datetime.now().date()
        inicio = datetime.combine(hoy, datetime.min.time())
        fin = datetime.combine(hoy, datetime.max.time())

        return (
            self.db.query(ConsultaRemota)
            .filter(
                and_(
                    ConsultaRemota.medico_id == medico_id,
                    ConsultaRemota.fecha_programada >= inicio,
                    ConsultaRemota.fecha_programada <= fin,
                    ConsultaRemota.estado.in_(
                        [EstadoConsulta.PROGRAMADA, EstadoConsulta.EN_CURSO]
                    ),
                )
            )
            .order_by(ConsultaRemota.fecha_programada.asc())
            .all()
        )

    def iniciar_consulta(self, consulta_id: UUID, medico_id: UUID) -> ConsultaRemota:
        """Iniciar una consulta programada"""
        consulta = self.obtener_consulta(consulta_id)

        if not consulta:
            raise ValueError("Consulta no encontrada")

        if consulta.medico_id != medico_id:
            raise PermissionError("No tiene permiso para iniciar esta consulta")

        if consulta.estado != EstadoConsulta.PROGRAMADA:
            raise ValueError(
                f"La consulta no puede iniciarse desde el estado: {consulta.estado}"
            )

        consulta.estado = EstadoConsulta.EN_CURSO
        consulta.fecha_inicio = datetime.utcnow()

        self.db.commit()
        self.db.refresh(consulta)

        return consulta

    def finalizar_consulta(
        self, consulta_id: UUID, medico_id: UUID, data: FinalizarConsultaRequest
    ) -> ConsultaRemota:
        """Finalizar una consulta en curso"""
        consulta = self.obtener_consulta(consulta_id)

        if not consulta:
            raise ValueError("Consulta no encontrada")

        if consulta.medico_id != medico_id:
            raise PermissionError("No tiene permiso para finalizar esta consulta")

        if consulta.estado != EstadoConsulta.EN_CURSO:
            raise ValueError(
                f"La consulta no puede finalizarse desde el estado: {consulta.estado}"
            )

        consulta.estado = EstadoConsulta.FINALIZADA
        consulta.fecha_fin = datetime.utcnow()
        consulta.notas_medico = data.notas_medico
        consulta.diagnostico_preliminar = data.diagnostico_preliminar
        consulta.plan_tratamiento = data.plan_tratamiento
        consulta.requiere_seguimiento = data.requiere_seguimiento

        # Calcular duración
        if consulta.fecha_inicio:
            delta = consulta.fecha_fin - consulta.fecha_inicio
            consulta.duracion_minutos = int(delta.total_seconds() / 60)

        self.db.commit()
        self.db.refresh(consulta)

        return consulta

    def cancelar_consulta(
        self, consulta_id: UUID, usuario_id: UUID, motivo: Optional[str] = None
    ) -> ConsultaRemota:
        """Cancelar una consulta"""
        consulta = self.obtener_consulta(consulta_id)

        if not consulta:
            raise ValueError("Consulta no encontrada")

        if consulta.estado in [EstadoConsulta.FINALIZADA, EstadoConsulta.CANCELADA]:
            raise ValueError("La consulta no puede cancelarse")

        consulta.estado = EstadoConsulta.CANCELADA
        if motivo:
            consulta.notas_medico = f"Cancelada: {motivo}"

        self.db.commit()
        self.db.refresh(consulta)

        return consulta

    # ========================================
    # CHAT
    # ========================================

    def enviar_mensaje(
        self, data: MensajeChatCreate, emisor_id: UUID, emisor_tipo: EmisorTipo
    ) -> MensajeChat:
        """Enviar un mensaje en el chat de la consulta"""
        mensaje = MensajeChat(
            consulta_remota_id=data.consulta_remota_id,
            emisor_id=emisor_id,
            emisor_tipo=emisor_tipo,
            contenido=data.contenido,
            tipo_mensaje=data.tipo_mensaje,
            archivo_url=data.archivo_url,
            archivo_nombre=data.archivo_nombre,
        )

        self.db.add(mensaje)
        self.db.commit()
        self.db.refresh(mensaje)

        return mensaje

    def obtener_mensajes(
        self, consulta_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[MensajeChat]:
        """Obtener mensajes de una consulta"""
        return (
            self.db.query(MensajeChat)
            .filter(MensajeChat.consulta_remota_id == consulta_id)
            .order_by(MensajeChat.created_at.asc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def marcar_mensajes_leidos(self, consulta_id: UUID, lector_id: UUID) -> int:
        """Marcar mensajes como leídos"""
        ahora = datetime.utcnow()

        result = (
            self.db.query(MensajeChat)
            .filter(
                and_(
                    MensajeChat.consulta_remota_id == consulta_id,
                    MensajeChat.emisor_id != lector_id,
                    MensajeChat.leido == False,
                )
            )
            .update({"leido": True, "fecha_leido": ahora})
        )

        self.db.commit()

        return result

    # ========================================
    # PRESCRIPCIONES
    # ========================================

    def crear_prescripcion(
        self, data: PrescripcionCreate, medico_id: UUID
    ) -> PrescripcionElectronica:
        """Crear una prescripción electrónica"""
        # Calcular fecha de vigencia
        fecha_vigencia = datetime.utcnow() + timedelta(days=data.dias_vigencia)

        # Convertir medicamentos a formato dict
        medicamentos_dict = [med.model_dump() for med in data.medicamentos]

        prescripcion = PrescripcionElectronica(
            consulta_remota_id=data.consulta_remota_id,
            paciente_id=data.paciente_id,
            medico_id=medico_id,
            diagnostico=data.diagnostico,
            codigo_cie10=data.codigo_cie10,
            medicamentos=medicamentos_dict,
            indicaciones_generales=data.indicaciones_generales,
            fecha_vigencia=fecha_vigencia,
        )

        self.db.add(prescripcion)
        self.db.commit()
        self.db.refresh(prescripcion)

        return prescripcion

    def obtener_prescripcion(
        self, prescripcion_id: UUID
    ) -> Optional[PrescripcionElectronica]:
        """Obtener una prescripción por ID"""
        return (
            self.db.query(PrescripcionElectronica)
            .filter(PrescripcionElectronica.id == prescripcion_id)
            .first()
        )

    def listar_prescripciones_paciente(
        self, paciente_id: UUID, solo_activas: bool = True
    ) -> List[PrescripcionElectronica]:
        """Listar prescripciones de un paciente"""
        query = self.db.query(PrescripcionElectronica).filter(
            PrescripcionElectronica.paciente_id == paciente_id
        )

        if solo_activas:
            query = query.filter(
                and_(
                    PrescripcionElectronica.activa == True,
                    PrescripcionElectronica.fecha_vigencia >= datetime.utcnow(),
                )
            )

        return query.order_by(PrescripcionElectronica.fecha_emision.desc()).all()

    # ========================================
    # SEGUIMIENTOS
    # ========================================

    def crear_seguimiento(
        self, data: SeguimientoCreate, medico_id: UUID
    ) -> SeguimientoPostConsulta:
        """Crear un seguimiento post-consulta"""
        seguimiento = SeguimientoPostConsulta(
            consulta_remota_id=data.consulta_remota_id,
            paciente_id=data.paciente_id,
            medico_id=medico_id,
            tipo=data.tipo,
            titulo=data.titulo,
            mensaje=data.mensaje,
            fecha_programada=data.fecha_programada,
            metodo_notificacion=data.metodo_notificacion,
        )

        self.db.add(seguimiento)
        self.db.commit()
        self.db.refresh(seguimiento)

        return seguimiento

    def obtener_seguimientos_pendientes(
        self, medico_id: Optional[UUID] = None
    ) -> List[SeguimientoPostConsulta]:
        """Obtener seguimientos pendientes de enviar"""
        query = self.db.query(SeguimientoPostConsulta).filter(
            and_(
                SeguimientoPostConsulta.enviado == False,
                SeguimientoPostConsulta.fecha_programada <= datetime.utcnow(),
            )
        )

        if medico_id:
            query = query.filter(SeguimientoPostConsulta.medico_id == medico_id)

        return query.order_by(SeguimientoPostConsulta.fecha_programada.asc()).all()

    # ========================================
    # ESTADÍSTICAS
    # ========================================

    def obtener_estadisticas(
        self,
        medico_id: Optional[UUID] = None,
        fecha_inicio: Optional[datetime] = None,
        fecha_fin: Optional[datetime] = None,
    ) -> dict:
        """Obtener estadísticas de telemedicina"""
        query = self.db.query(ConsultaRemota)

        if medico_id:
            query = query.filter(ConsultaRemota.medico_id == medico_id)

        if fecha_inicio:
            query = query.filter(ConsultaRemota.created_at >= fecha_inicio)

        if fecha_fin:
            query = query.filter(ConsultaRemota.created_at <= fecha_fin)

        total = query.count()
        programadas = query.filter(
            ConsultaRemota.estado == EstadoConsulta.PROGRAMADA
        ).count()
        realizadas = query.filter(
            ConsultaRemota.estado == EstadoConsulta.FINALIZADA
        ).count()
        canceladas = query.filter(
            ConsultaRemota.estado == EstadoConsulta.CANCELADA
        ).count()

        # Duración promedio
        duracion_avg = (
            self.db.query(func.avg(ConsultaRemota.duracion_minutos))
            .filter(ConsultaRemota.estado == EstadoConsulta.FINALIZADA)
            .scalar()
            or 0
        )

        # Prescripciones
        prescripciones_query = self.db.query(PrescripcionElectronica)
        if medico_id:
            prescripciones_query = prescripciones_query.filter(
                PrescripcionElectronica.medico_id == medico_id
            )
        prescripciones_count = prescripciones_query.count()

        # Seguimientos
        seguimientos_query = self.db.query(SeguimientoPostConsulta)
        if medico_id:
            seguimientos_query = seguimientos_query.filter(
                SeguimientoPostConsulta.medico_id == medico_id
            )
        seguimientos_count = seguimientos_query.count()

        return {
            "total_consultas": total,
            "consultas_programadas": programadas,
            "consultas_realizadas": realizadas,
            "consultas_canceladas": canceladas,
            "duracion_promedio_minutos": round(float(duracion_avg), 1),
            "prescripciones_emitidas": prescripciones_count,
            "seguimientos_programados": seguimientos_count,
        }
