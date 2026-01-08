from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc
from sqlalchemy.orm import selectinload
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import hashlib
import json
from uuid import UUID

from app.models.cumplimiento import (
    ConfiguracionCumplimiento,
    FirmaElectronica,
    ConsentimientoInformado,
    LogAccesoSensible,
    SolicitudDatosPersonales,
    AuditoriaHIPAA,
    TipoNormativa,
    TipoConsentimiento,
    EstadoConsentimiento,
    TipoAccesoSensible,
)
from app.models.usuario import Usuario
from app.models.paciente import Paciente


class CumplimientoService:
    def __init__(self, db: AsyncSession):
        self.db = db

    # ==================== CONFIGURACIÓN ====================

    async def get_configuracion(
        self, normativa: TipoNormativa
    ) -> Optional[ConfiguracionCumplimiento]:
        """Obtiene la configuración de una normativa específica"""
        result = await self.db.execute(
            select(ConfiguracionCumplimiento).where(
                ConfiguracionCumplimiento.normativa == normativa
            )
        )
        return result.scalar_one_or_none()

    async def create_configuracion(
        self, normativa: TipoNormativa, configuracion: Dict[str, Any], **kwargs
    ) -> ConfiguracionCumplimiento:
        """Crea o actualiza la configuración de una normativa"""
        config = await self.get_configuracion(normativa)

        if config:
            # Actualizar existente
            config.configuracion = configuracion
            for key, value in kwargs.items():
                if hasattr(config, key):
                    setattr(config, key, value)
            config.updated_at = datetime.utcnow()
        else:
            # Crear nueva
            config = ConfiguracionCumplimiento(
                normativa=normativa, configuracion=configuracion, **kwargs
            )
            self.db.add(config)

        await self.db.commit()
        await self.db.refresh(config)
        return config

    async def list_configuraciones(self) -> List[ConfiguracionCumplimiento]:
        """Lista todas las configuraciones de normativas"""
        result = await self.db.execute(
            select(ConfiguracionCumplimiento).order_by(
                ConfiguracionCumplimiento.normativa
            )
        )
        return result.scalars().all()

    # ==================== FIRMA ELECTRÓNICA ====================

    def generar_firma_digital(self, contenido: str, usuario_id: str) -> str:
        """Genera una firma digital usando SHA-256"""
        timestamp = datetime.utcnow().isoformat()
        data = f"{contenido}|{usuario_id}|{timestamp}"
        return hashlib.sha256(data.encode()).hexdigest()

    async def crear_firma_electronica(
        self,
        usuario_id: UUID,
        recurso_tipo: str,
        recurso_id: UUID,
        contenido: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        ubicacion: Optional[Dict] = None,
    ) -> FirmaElectronica:
        """Crea una firma electrónica para un documento"""
        firma_digital = self.generar_firma_digital(contenido, str(usuario_id))

        firma = FirmaElectronica(
            usuario_id=usuario_id,
            recurso_tipo=recurso_tipo,
            recurso_id=recurso_id,
            firma_digital=firma_digital,
            ip_address=ip_address,
            user_agent=user_agent,
            ubicacion=ubicacion,
        )

        self.db.add(firma)
        await self.db.commit()
        await self.db.refresh(firma)
        return firma

    async def validar_firma(self, firma_id: UUID, contenido: str) -> bool:
        """Valida una firma electrónica"""
        result = await self.db.execute(
            select(FirmaElectronica).where(FirmaElectronica.id == firma_id)
        )
        firma = result.scalar_one_or_none()

        if not firma or not firma.valida:
            return False

        firma_esperada = self.generar_firma_digital(contenido, str(firma.usuario_id))
        return firma.firma_digital == firma_esperada

    async def invalidar_firma(self, firma_id: UUID, motivo: str) -> FirmaElectronica:
        """Invalida una firma electrónica"""
        result = await self.db.execute(
            select(FirmaElectronica).where(FirmaElectronica.id == firma_id)
        )
        firma = result.scalar_one_or_none()

        if firma:
            firma.valida = False
            firma.fecha_validacion = datetime.utcnow()
            firma.motivo_invalidacion = motivo
            await self.db.commit()
            await self.db.refresh(firma)

        return firma

    # ==================== CONSENTIMIENTO INFORMADO ====================

    async def crear_consentimiento(
        self,
        paciente_id: UUID,
        medico_id: UUID,
        tipo: TipoConsentimiento,
        titulo: str,
        descripcion: str,
        riesgos: Optional[List[str]] = None,
        beneficios: Optional[List[str]] = None,
        alternativas: Optional[List[str]] = None,
        consulta_id: Optional[UUID] = None,
    ) -> ConsentimientoInformado:
        """Crea un consentimiento informado"""
        consentimiento = ConsentimientoInformado(
            paciente_id=paciente_id,
            medico_id=medico_id,
            tipo=tipo,
            titulo=titulo,
            descripcion=descripcion,
            riesgos=riesgos,
            beneficios=beneficios,
            alternativas=alternativas,
            consulta_id=consulta_id,
        )

        self.db.add(consentimiento)
        await self.db.commit()
        await self.db.refresh(consentimiento)
        return consentimiento

    async def firmar_consentimiento_paciente(
        self,
        consentimiento_id: UUID,
        contenido: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> ConsentimientoInformado:
        """Firma un consentimiento por parte del paciente"""
        result = await self.db.execute(
            select(ConsentimientoInformado)
            .options(selectinload(ConsentimientoInformado.paciente))
            .where(ConsentimientoInformado.id == consentimiento_id)
        )
        consentimiento = result.scalar_one_or_none()

        if not consentimiento:
            raise ValueError("Consentimiento no encontrado")

        # Crear firma electrónica
        firma = await self.crear_firma_electronica(
            usuario_id=consentimiento.paciente_id,
            recurso_tipo="consentimiento_informado",
            recurso_id=consentimiento_id,
            contenido=contenido,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        # Actualizar consentimiento
        consentimiento.firma_paciente_id = firma.id
        consentimiento.fecha_firma_paciente = datetime.utcnow()
        consentimiento.estado = EstadoConsentimiento.ACEPTADO
        consentimiento.ip_address = ip_address

        await self.db.commit()
        await self.db.refresh(consentimiento)
        return consentimiento

    async def firmar_consentimiento_medico(
        self,
        consentimiento_id: UUID,
        contenido: str,
        ip_address: Optional[str] = None,
    ) -> ConsentimientoInformado:
        """Firma un consentimiento por parte del médico"""
        result = await self.db.execute(
            select(ConsentimientoInformado).where(
                ConsentimientoInformado.id == consentimiento_id
            )
        )
        consentimiento = result.scalar_one_or_none()

        if not consentimiento:
            raise ValueError("Consentimiento no encontrado")

        # Crear firma electrónica
        firma = await self.crear_firma_electronica(
            usuario_id=consentimiento.medico_id,
            recurso_tipo="consentimiento_informado",
            recurso_id=consentimiento_id,
            contenido=contenido,
            ip_address=ip_address,
        )

        # Actualizar consentimiento
        consentimiento.firma_medico_id = firma.id
        consentimiento.fecha_firma_medico = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(consentimiento)
        return consentimiento

    async def revocar_consentimiento(
        self, consentimiento_id: UUID, motivo: str
    ) -> ConsentimientoInformado:
        """Revoca un consentimiento informado"""
        result = await self.db.execute(
            select(ConsentimientoInformado).where(
                ConsentimientoInformado.id == consentimiento_id
            )
        )
        consentimiento = result.scalar_one_or_none()

        if consentimiento:
            consentimiento.estado = EstadoConsentimiento.REVOCADO
            consentimiento.fecha_revocacion = datetime.utcnow()
            consentimiento.motivo_revocacion = motivo
            await self.db.commit()
            await self.db.refresh(consentimiento)

        return consentimiento

    async def get_consentimientos_paciente(
        self,
        paciente_id: UUID,
        tipo: Optional[TipoConsentimiento] = None,
    ) -> List[ConsentimientoInformado]:
        """Obtiene los consentimientos de un paciente"""
        query = select(ConsentimientoInformado).where(
            ConsentimientoInformado.paciente_id == paciente_id
        )

        if tipo:
            query = query.where(ConsentimientoInformado.tipo == tipo)

        query = query.order_by(desc(ConsentimientoInformado.created_at))

        result = await self.db.execute(query)
        return result.scalars().all()

    # ==================== LOGS DE ACCESO SENSIBLE ====================

    async def registrar_acceso_sensible(
        self,
        usuario_id: UUID,
        recurso_tipo: str,
        recurso_id: UUID,
        tipo_acceso: TipoAccesoSensible,
        accion: str,
        paciente_id: Optional[UUID] = None,
        descripcion: Optional[str] = None,
        datos_accedidos: Optional[Dict] = None,
        justificacion: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        endpoint: Optional[str] = None,
        metodo_http: Optional[str] = None,
        normativa_aplicable: Optional[TipoNormativa] = None,
    ) -> LogAccesoSensible:
        """Registra un acceso a información sensible (HIPAA compliance)"""
        log = LogAccesoSensible(
            usuario_id=usuario_id,
            recurso_tipo=recurso_tipo,
            recurso_id=recurso_id,
            paciente_id=paciente_id,
            tipo_acceso=tipo_acceso,
            accion=accion,
            descripcion=descripcion,
            datos_accedidos=datos_accedidos,
            justificacion=justificacion,
            ip_address=ip_address,
            user_agent=user_agent,
            endpoint=endpoint,
            metodo_http=metodo_http,
            normativa_aplicable=normativa_aplicable,
        )

        self.db.add(log)
        await self.db.commit()
        await self.db.refresh(log)
        return log

    async def get_logs_acceso_paciente(
        self,
        paciente_id: UUID,
        fecha_inicio: Optional[datetime] = None,
        fecha_fin: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[LogAccesoSensible]:
        """Obtiene los logs de acceso a información de un paciente"""
        query = select(LogAccesoSensible).where(
            LogAccesoSensible.paciente_id == paciente_id
        )

        if fecha_inicio:
            query = query.where(LogAccesoSensible.created_at >= fecha_inicio)
        if fecha_fin:
            query = query.where(LogAccesoSensible.created_at <= fecha_fin)

        query = query.order_by(desc(LogAccesoSensible.created_at)).limit(limit)

        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_logs_acceso_usuario(
        self,
        usuario_id: UUID,
        limit: int = 100,
    ) -> List[LogAccesoSensible]:
        """Obtiene los logs de acceso de un usuario"""
        result = await self.db.execute(
            select(LogAccesoSensible)
            .where(LogAccesoSensible.usuario_id == usuario_id)
            .order_by(desc(LogAccesoSensible.created_at))
            .limit(limit)
        )
        return result.scalars().all()

    # ==================== SOLICITUDES DATOS PERSONALES (GDPR) ====================

    async def crear_solicitud_datos(
        self,
        paciente_id: UUID,
        tipo_solicitud: str,
        descripcion: str,
        datos_solicitados: Optional[List[str]] = None,
        dias_limite: int = 30,
    ) -> SolicitudDatosPersonales:
        """Crea una solicitud de datos personales (GDPR)"""
        fecha_limite = datetime.utcnow() + timedelta(days=dias_limite)

        solicitud = SolicitudDatosPersonales(
            paciente_id=paciente_id,
            tipo_solicitud=tipo_solicitud,
            descripcion=descripcion,
            datos_solicitados=datos_solicitados,
            fecha_limite=fecha_limite,
        )

        self.db.add(solicitud)
        await self.db.commit()
        await self.db.refresh(solicitud)
        return solicitud

    async def procesar_solicitud_datos(
        self,
        solicitud_id: UUID,
        procesado_por_id: UUID,
        respuesta: str,
        archivo_respuesta_url: Optional[str] = None,
    ) -> SolicitudDatosPersonales:
        """Procesa una solicitud de datos personales"""
        result = await self.db.execute(
            select(SolicitudDatosPersonales).where(
                SolicitudDatosPersonales.id == solicitud_id
            )
        )
        solicitud = result.scalar_one_or_none()

        if solicitud:
            solicitud.estado = "COMPLETADA"
            solicitud.fecha_respuesta = datetime.utcnow()
            solicitud.respuesta = respuesta
            solicitud.archivo_respuesta_url = archivo_respuesta_url
            solicitud.procesado_por_id = procesado_por_id
            await self.db.commit()
            await self.db.refresh(solicitud)

        return solicitud

    async def get_solicitudes_pendientes(self) -> List[SolicitudDatosPersonales]:
        """Obtiene solicitudes pendientes de procesar"""
        result = await self.db.execute(
            select(SolicitudDatosPersonales)
            .where(SolicitudDatosPersonales.estado == "PENDIENTE")
            .order_by(SolicitudDatosPersonales.fecha_limite)
        )
        return result.scalars().all()

    # ==================== AUDITORÍA HIPAA ====================

    async def crear_auditoria_hipaa(
        self,
        auditor_id: UUID,
        fecha_inicio: datetime,
        fecha_fin: datetime,
    ) -> AuditoriaHIPAA:
        """Crea una auditoría HIPAA"""
        # Contar accesos en el período
        result = await self.db.execute(
            select(func.count(LogAccesoSensible.id)).where(
                and_(
                    LogAccesoSensible.created_at >= fecha_inicio,
                    LogAccesoSensible.created_at <= fecha_fin,
                )
            )
        )
        total_accesos = result.scalar() or 0

        # Contar accesos autorizados
        result = await self.db.execute(
            select(func.count(LogAccesoSensible.id)).where(
                and_(
                    LogAccesoSensible.created_at >= fecha_inicio,
                    LogAccesoSensible.created_at <= fecha_fin,
                    LogAccesoSensible.autorizado == True,
                )
            )
        )
        accesos_autorizados = result.scalar() or 0

        # Contar accesos no autorizados
        result = await self.db.execute(
            select(func.count(LogAccesoSensible.id)).where(
                and_(
                    LogAccesoSensible.created_at >= fecha_inicio,
                    LogAccesoSensible.created_at <= fecha_fin,
                    LogAccesoSensible.autorizado == False,
                )
            )
        )
        accesos_no_autorizados = result.scalar() or 0

        # Calcular nivel de cumplimiento
        nivel_cumplimiento = 0
        if total_accesos > 0:
            nivel_cumplimiento = int((accesos_autorizados / total_accesos) * 100)

        auditoria = AuditoriaHIPAA(
            auditor_id=auditor_id,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            total_accesos=total_accesos,
            accesos_autorizados=accesos_autorizados,
            accesos_no_autorizados=accesos_no_autorizados,
            nivel_cumplimiento=nivel_cumplimiento,
            cumple_normativa=(nivel_cumplimiento >= 95),
        )

        self.db.add(auditoria)
        await self.db.commit()
        await self.db.refresh(auditoria)
        return auditoria

    async def get_auditorias_recientes(self, limit: int = 10) -> List[AuditoriaHIPAA]:
        """Obtiene las auditorías más recientes"""
        result = await self.db.execute(
            select(AuditoriaHIPAA)
            .order_by(desc(AuditoriaHIPAA.created_at))
            .limit(limit)
        )
        return result.scalars().all()

    # ==================== ESTADÍSTICAS ====================

    async def get_estadisticas_cumplimiento(self) -> Dict[str, Any]:
        """Obtiene estadísticas generales de cumplimiento"""
        # Total de consentimientos
        result = await self.db.execute(select(func.count(ConsentimientoInformado.id)))
        total_consentimientos = result.scalar() or 0

        # Consentimientos activos
        result = await self.db.execute(
            select(func.count(ConsentimientoInformado.id)).where(
                ConsentimientoInformado.estado == EstadoConsentimiento.ACEPTADO
            )
        )
        consentimientos_activos = result.scalar() or 0

        # Total de firmas electrónicas
        result = await self.db.execute(select(func.count(FirmaElectronica.id)))
        total_firmas = result.scalar() or 0

        # Firmas válidas
        result = await self.db.execute(
            select(func.count(FirmaElectronica.id)).where(
                FirmaElectronica.valida == True
            )
        )
        firmas_validas = result.scalar() or 0

        # Logs de acceso (últimos 30 días)
        fecha_inicio = datetime.utcnow() - timedelta(days=30)
        result = await self.db.execute(
            select(func.count(LogAccesoSensible.id)).where(
                LogAccesoSensible.created_at >= fecha_inicio
            )
        )
        logs_ultimo_mes = result.scalar() or 0

        # Solicitudes GDPR pendientes
        result = await self.db.execute(
            select(func.count(SolicitudDatosPersonales.id)).where(
                SolicitudDatosPersonales.estado == "PENDIENTE"
            )
        )
        solicitudes_pendientes = result.scalar() or 0

        return {
            "total_consentimientos": total_consentimientos,
            "consentimientos_activos": consentimientos_activos,
            "total_firmas": total_firmas,
            "firmas_validas": firmas_validas,
            "logs_acceso_ultimo_mes": logs_ultimo_mes,
            "solicitudes_gdpr_pendientes": solicitudes_pendientes,
        }
