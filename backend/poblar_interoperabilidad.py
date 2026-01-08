"""
Script para poblar datos de prueba del Sistema de Interoperabilidad
Crea instituciones, solicitudes, consentimientos y datos de ejemplo
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta
from uuid import uuid4

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

from app.core.config import settings
from app.models.interoperabilidad import (
    InstitucionExterna,
    SolicitudIntercambio,
    HistoriaClinicaUnificada,
    ConsentimientoIntercambio,
    LogIntercambio,
    MapeoCodigos,
    TipoIntercambio,
    EstadoIntercambio,
    ProtocoloIntercambio,
)
from app.models.paciente import Paciente
from app.models.usuario import Usuario
from app.models.institucion import Institucion


async def poblar_datos():
    """Pobla la base de datos con datos de prueba"""

    # Crear engine y session
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        print("🔄 Iniciando población de datos de interoperabilidad...")

        # Obtener institución local
        result = await session.execute(select(Institucion).limit(1))
        institucion_local = result.scalar_one_or_none()

        if not institucion_local:
            print(
                "❌ No se encontró institución local. Ejecute primero la migración de multi-tenancy."
            )
            return

        print(f"✅ Institución local: {institucion_local.nombre}")

        # Obtener primer paciente
        result = await session.execute(select(Paciente).limit(1))
        paciente = result.scalar_one_or_none()

        if not paciente:
            print(
                "❌ No se encontró ningún paciente. Cree al menos un paciente primero."
            )
            return

        print(f"✅ Paciente de prueba: {paciente.nombre} {paciente.apellido_paterno}")

        # Obtener primer usuario (médico)
        result = await session.execute(select(Usuario).limit(1))
        usuario = result.scalar_one_or_none()

        if not usuario:
            print("❌ No se encontró ningún usuario. Cree al menos un usuario primero.")
            return

        print(f"✅ Usuario de prueba: {usuario.nombre}")

        # 1. CREAR INSTITUCIONES EXTERNAS
        print("\n📋 Creando instituciones externas...")

        instituciones_data = [
            {
                "nombre": "Hospital General de México Dr. Eduardo Liceaga",
                "codigo_institucional": "HGM-001",
                "nivel_atencion": "terciario",
                "tipo_institucion": "publico",
                "pais": "México",
                "estado": "Ciudad de México",
                "ciudad": "Ciudad de México",
                "direccion": "Dr. Balmis 148, Doctores",
                "telefono": "55-2789-2000",
                "email": "contacto@hgm.salud.gob.mx",
                "url_endpoint_fhir": "https://hgm.salud.gob.mx/fhir/r4",
                "activa": True,
                "protocolos_soportados": ["FHIR_R4", "HL7V2"],
                "versiones_fhir": ["4.0.1"],
            },
            {
                "nombre": "Instituto Nacional de Cardiología Ignacio Chávez",
                "codigo_institucional": "INC-002",
                "nivel_atencion": "especializado",
                "tipo_institucion": "publico",
                "pais": "México",
                "estado": "Ciudad de México",
                "ciudad": "Ciudad de México",
                "direccion": "Juan Badiano 1, Sección XVI",
                "telefono": "55-5573-2911",
                "email": "contacto@cardiologia.org.mx",
                "url_endpoint_fhir": "https://cardiologia.org.mx/fhir/r4",
                "activa": True,
                "protocolos_soportados": ["FHIR_R4"],
                "versiones_fhir": ["4.0.1"],
            },
            {
                "nombre": "Hospital ABC Observatorio",
                "codigo_institucional": "ABC-003",
                "nivel_atencion": "terciario",
                "tipo_institucion": "privado",
                "pais": "México",
                "estado": "Ciudad de México",
                "ciudad": "Ciudad de México",
                "direccion": "Sur 136 No. 116, Las Américas",
                "telefono": "55-5230-8000",
                "email": "info@abchospital.com",
                "url_endpoint_fhir": "https://abchospital.com/api/fhir/r4",
                "activa": True,
                "protocolos_soportados": ["FHIR_R4", "FHIR_R5", "REST_API"],
                "versiones_fhir": ["4.0.1", "5.0.0"],
            },
            {
                "nombre": "Centro de Salud Comunitario Norte",
                "codigo_institucional": "CSC-004",
                "nivel_atencion": "primario",
                "tipo_institucion": "publico",
                "pais": "México",
                "estado": "Nuevo León",
                "ciudad": "Monterrey",
                "direccion": "Av. Universidad 1000",
                "telefono": "81-8329-4000",
                "email": "contacto@cscnorte.gob.mx",
                "url_endpoint_fhir": "https://cscnorte.gob.mx/fhir",
                "activa": True,
                "protocolos_soportados": ["FHIR_R4"],
                "versiones_fhir": ["4.0.1"],
            },
            {
                "nombre": "Clínica Especializada del Bajío",
                "codigo_institucional": "CEB-005",
                "nivel_atencion": "secundario",
                "tipo_institucion": "privado",
                "pais": "México",
                "estado": "Guanajuato",
                "ciudad": "León",
                "direccion": "Blvd. Adolfo López Mateos 2518",
                "telefono": "477-710-0000",
                "email": "contacto@clinicabajio.com",
                "url_endpoint_fhir": "https://clinicabajio.com/fhir",
                "activa": True,
                "protocolos_soportados": ["FHIR_R4"],
                "versiones_fhir": ["4.0.1"],
            },
        ]

        instituciones_creadas = []
        for inst_data in instituciones_data:
            # Verificar si ya existe
            result = await session.execute(
                select(InstitucionExterna).where(
                    InstitucionExterna.codigo_institucional
                    == inst_data["codigo_institucional"]
                )
            )
            inst_existente = result.scalar_one_or_none()

            if inst_existente:
                print(f"   ⚠️  Ya existe: {inst_data['nombre']}")
                instituciones_creadas.append(inst_existente)
            else:
                inst = InstitucionExterna(**inst_data)
                session.add(inst)
                await session.flush()
                instituciones_creadas.append(inst)
                print(f"   ✅ Creada: {inst_data['nombre']}")

        await session.commit()
        print(f"✅ {len(instituciones_creadas)} instituciones externas disponibles")

        # 2. CREAR CONSENTIMIENTO DEL PACIENTE
        print("\n🛡️ Creando consentimiento del paciente...")

        result = await session.execute(
            select(ConsentimientoIntercambio).where(
                ConsentimientoIntercambio.paciente_id == paciente.id
            )
        )
        consentimiento_existente = result.scalar_one_or_none()

        if not consentimiento_existente:
            consentimiento = ConsentimientoIntercambio(
                paciente_id=paciente.id,
                activo=True,
                fecha_consentimiento=datetime.utcnow(),
                fecha_expiracion=datetime.utcnow() + timedelta(days=365),
                revocado=False,
                instituciones_autorizadas=["todas"],
                tipos_datos_autorizados=[
                    "consultas",
                    "laboratorios",
                    "imagenes",
                    "recetas",
                ],
                puede_compartir_diagnosticos=True,
                puede_compartir_laboratorios=True,
                puede_compartir_imagenes=True,
                puede_compartir_recetas=True,
                proposito_uso=["atencion_medica", "continuidad_cuidado"],
            )
            session.add(consentimiento)
            await session.commit()
            print("   ✅ Consentimiento creado")
        else:
            print("   ⚠️  Consentimiento ya existe")

        # 3. CREAR SOLICITUDES DE INTERCAMBIO
        print("\n📤 Creando solicitudes de intercambio...")

        solicitudes_data = [
            {
                "tipo_intercambio": TipoIntercambio.EXPEDIENTE_COMPLETO,
                "protocolo": ProtocoloIntercambio.FHIR_R4,
                "estado": EstadoIntercambio.PENDIENTE,
                "prioridad": "alta",
                "motivo_solicitud": "Referencia a cardiología por sospecha de cardiopatía isquémica",
                "institucion_destino": instituciones_creadas[
                    1
                ],  # Instituto de Cardiología
            },
            {
                "tipo_intercambio": TipoIntercambio.LABORATORIOS,
                "protocolo": ProtocoloIntercambio.FHIR_R4,
                "estado": EstadoIntercambio.APROBADA,
                "prioridad": "normal",
                "motivo_solicitud": "Solicitud de resultados de laboratorio previos",
                "institucion_destino": instituciones_creadas[0],  # Hospital General
            },
            {
                "tipo_intercambio": TipoIntercambio.IMAGENES,
                "protocolo": ProtocoloIntercambio.FHIR_R4,
                "estado": EstadoIntercambio.COMPLETADA,
                "prioridad": "normal",
                "motivo_solicitud": "Comparación de estudios radiológicos",
                "institucion_destino": instituciones_creadas[2],  # Hospital ABC
            },
            {
                "tipo_intercambio": TipoIntercambio.CONSULTAS,
                "protocolo": ProtocoloIntercambio.FHIR_R4,
                "estado": EstadoIntercambio.EN_PROCESO,
                "prioridad": "urgente",
                "motivo_solicitud": "Urgencia médica, requiere historial de consultas",
                "institucion_destino": instituciones_creadas[3],  # Centro de Salud
            },
            {
                "tipo_intercambio": TipoIntercambio.RECETAS,
                "protocolo": ProtocoloIntercambio.REST_API,
                "estado": EstadoIntercambio.RECHAZADA,
                "prioridad": "baja",
                "motivo_solicitud": "Verificación de medicamentos actuales",
                "motivo_rechazo": "Paciente no cuenta con recetas en el período solicitado",
                "institucion_destino": instituciones_creadas[4],  # Clínica Bajío
            },
        ]

        for sol_data in solicitudes_data:
            institucion_dest = sol_data.pop("institucion_destino")
            motivo_rechazo = sol_data.pop("motivo_rechazo", None)

            solicitud = SolicitudIntercambio(
                paciente_id=paciente.id,
                institucion_origen_id=institucion_local.id,
                institucion_destino_id=institucion_dest.id,
                solicitante_id=usuario.id,
                periodo_inicio=datetime.utcnow() - timedelta(days=90),
                periodo_fin=datetime.utcnow(),
                **sol_data,
            )

            # Agregar datos según estado
            if solicitud.estado == EstadoIntercambio.APROBADA:
                solicitud.aprobador_id = usuario.id
                solicitud.fecha_aprobacion = datetime.utcnow() - timedelta(days=2)

            elif solicitud.estado == EstadoIntercambio.COMPLETADA:
                solicitud.aprobador_id = usuario.id
                solicitud.fecha_aprobacion = datetime.utcnow() - timedelta(days=5)
                solicitud.fecha_completado = datetime.utcnow() - timedelta(days=3)
                solicitud.checksum_datos = "abc123def456"

            elif solicitud.estado == EstadoIntercambio.RECHAZADA:
                solicitud.aprobador_id = usuario.id
                solicitud.motivo_rechazo = motivo_rechazo

            session.add(solicitud)
            await session.flush()

            # Crear log
            log = LogIntercambio(
                solicitud_id=solicitud.id,
                accion="SOLICITUD_CREADA",
                protocolo=solicitud.protocolo.value,
                direccion="SALIDA",
                usuario_id=usuario.id,
            )
            session.add(log)

            print(
                f"   ✅ Solicitud creada: {solicitud.tipo_intercambio.value} - {solicitud.estado.value}"
            )

        await session.commit()
        print(f"✅ {len(solicitudes_data)} solicitudes de intercambio creadas")

        # 4. CREAR HISTORIA CLÍNICA UNIFICADA
        print("\n📚 Creando historia clínica unificada...")

        result = await session.execute(
            select(HistoriaClinicaUnificada).where(
                HistoriaClinicaUnificada.paciente_id == paciente.id
            )
        )
        historia_existente = result.scalar_one_or_none()

        if not historia_existente:
            historia = HistoriaClinicaUnificada(
                paciente_id=paciente.id,
                consultas_totales=15,
                hospitalizaciones_totales=2,
                diagnosticos_activos=[
                    {
                        "codigo_cie10": "E11",
                        "descripcion": "Diabetes mellitus tipo 2",
                        "fecha_diagnostico": "2023-01-15",
                        "institucion": "Hospital General de México",
                    },
                    {
                        "codigo_cie10": "I10",
                        "descripcion": "Hipertensión esencial (primaria)",
                        "fecha_diagnostico": "2022-06-20",
                        "institucion": "Hospital ABC",
                    },
                ],
                medicamentos_actuales=[
                    {
                        "nombre": "Metformina",
                        "dosis": "850 mg",
                        "frecuencia": "Cada 12 horas",
                        "via": "Oral",
                        "institucion": "Hospital General de México",
                    },
                    {
                        "nombre": "Losartán",
                        "dosis": "50 mg",
                        "frecuencia": "Cada 24 horas",
                        "via": "Oral",
                        "institucion": "Hospital ABC",
                    },
                ],
                alergias_consolidadas=[
                    {
                        "sustancia": "Penicilina",
                        "tipo": "Medicamento",
                        "reaccion": "Urticaria",
                        "gravedad": "Moderada",
                    }
                ],
                instituciones_contribuyentes=[
                    "Hospital General de México",
                    "Hospital ABC",
                    "Instituto Nacional de Cardiología",
                ],
                ultima_actualizacion_externa=datetime.utcnow() - timedelta(days=7),
            )
            session.add(historia)
            await session.commit()
            print("   ✅ Historia clínica unificada creada")
        else:
            print("   ⚠️  Historia clínica unificada ya existe")

        # 5. CREAR MAPEOS DE CÓDIGOS
        print("\n🔄 Creando mapeos de códigos...")

        mapeos_data = [
            {
                "sistema_origen": "CIE-10",
                "codigo_origen": "E11",
                "descripcion_origen": "Diabetes mellitus tipo 2",
                "sistema_destino": "SNOMED-CT",
                "codigo_destino": "44054006",
                "descripcion_destino": "Type 2 diabetes mellitus",
                "tipo_concepto": "diagnostico",
                "equivalencia": "exacta",
                "validado": True,
            },
            {
                "sistema_origen": "CIE-10",
                "codigo_origen": "I10",
                "descripcion_origen": "Hipertensión esencial (primaria)",
                "sistema_destino": "SNOMED-CT",
                "codigo_destino": "59621000",
                "descripcion_destino": "Essential hypertension",
                "tipo_concepto": "diagnostico",
                "equivalencia": "exacta",
                "validado": True,
            },
            {
                "sistema_origen": "LOINC",
                "codigo_origen": "2345-7",
                "descripcion_origen": "Glucosa [Masa/volumen] en Suero o Plasma",
                "sistema_destino": "SNOMED-CT",
                "codigo_destino": "33747003",
                "descripcion_destino": "Glucose measurement",
                "tipo_concepto": "laboratorio",
                "equivalencia": "exacta",
                "validado": True,
            },
        ]

        mapeos_creados = 0
        for mapeo_data in mapeos_data:
            result = await session.execute(
                select(MapeoCodigos).where(
                    MapeoCodigos.sistema_origen == mapeo_data["sistema_origen"],
                    MapeoCodigos.codigo_origen == mapeo_data["codigo_origen"],
                    MapeoCodigos.sistema_destino == mapeo_data["sistema_destino"],
                )
            )
            mapeo_existente = result.scalar_one_or_none()

            if not mapeo_existente:
                mapeo = MapeoCodigos(**mapeo_data)
                if mapeo.validado:
                    mapeo.validado_por = usuario.id
                    mapeo.fecha_validacion = datetime.utcnow()
                session.add(mapeo)
                mapeos_creados += 1

        await session.commit()
        print(f"   ✅ {mapeos_creados} mapeos de códigos creados")

        print("\n" + "=" * 60)
        print("✅ POBLACIÓN DE DATOS COMPLETADA")
        print("=" * 60)
        print(f"\n📊 Resumen:")
        print(f"   • {len(instituciones_creadas)} instituciones externas")
        print(f"   • {len(solicitudes_data)} solicitudes de intercambio")
        print(f"   • 1 historia clínica unificada")
        print(f"   • 1 consentimiento de paciente")
        print(f"   • {mapeos_creados} mapeos de códigos")
        print(f"\n🌐 Accede al sistema en: http://localhost:5173/interoperabilidad")
        print("=" * 60 + "\n")


if __name__ == "__main__":
    asyncio.run(poblar_datos())
