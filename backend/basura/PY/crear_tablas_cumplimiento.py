"""
Script para crear las tablas del módulo de Cumplimiento Normativo en la base de datos.

Ejecutar:
    python crear_tablas_cumplimiento.py
"""

import asyncio
import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import text
from app.core.database import engine, Base
from app.models import (
    ConfiguracionCumplimiento,
    FirmaElectronica,
    ConsentimientoInformado,
    LogAccesoSensible,
    SolicitudDatosPersonales,
    AuditoriaHIPAA,
)


async def crear_tablas():
    """Crea las tablas del módulo de cumplimiento normativo"""

    print("🔧 Creando tablas del módulo de Cumplimiento Normativo...")

    async with engine.begin() as conn:
        # Crear las tablas
        await conn.run_sync(Base.metadata.create_all)

        print("✅ Tablas creadas exitosamente:")
        print("   - configuracion_cumplimiento")
        print("   - firmas_electronicas")
        print("   - consentimientos_informados")
        print("   - logs_acceso_sensible")
        print("   - solicitudes_datos_personales")
        print("   - auditoria_hipaa")


async def poblar_configuraciones_iniciales():
    """Crea las configuraciones iniciales para cada normativa"""
    from sqlalchemy.ext.asyncio import AsyncSession
    from app.core.database import async_session_maker
    from app.models.cumplimiento import TipoNormativa

    print("\n📋 Poblando configuraciones iniciales...")

    async with async_session_maker() as session:
        # Configuración HIPAA (EE.UU.)
        config_hipaa = ConfiguracionCumplimiento(
            normativa=TipoNormativa.HIPAA,
            habilitado=True,
            requiere_autorizacion_acceso=True,
            requiere_log_acceso=True,
            dias_retencion_logs=2555,  # 7 años
            requiere_firma_electronica=True,
            requiere_expediente_electronico=True,
            requiere_respaldo_informacion=True,
            notas="Health Insurance Portability and Accountability Act - Protección de información médica en EE.UU.",
            configuracion={
                "descripcion": "HIPAA establece estándares nacionales para proteger la información médica sensible",
                "requisitos_principales": [
                    "Protección de PHI (Protected Health Information)",
                    "Control de acceso a registros médicos",
                    "Auditoría de accesos",
                    "Encriptación de datos en tránsito y reposo",
                    "Capacitación del personal",
                    "Plan de respuesta a incidentes",
                ],
                "sanciones": "Multas de $100 a $50,000 por violación, hasta $1.5M por año",
            },
        )
        session.add(config_hipaa)

        # Configuración GDPR (Europa)
        config_gdpr = ConfiguracionCumplimiento(
            normativa=TipoNormativa.GDPR,
            habilitado=True,
            requiere_consentimiento_explicito=True,
            permite_portabilidad_datos=True,
            permite_derecho_olvido=True,
            dias_respuesta_solicitud=30,
            requiere_log_acceso=True,
            dias_retencion_logs=2555,
            notas="General Data Protection Regulation - Protección de datos personales en la UE",
            configuracion={
                "descripcion": "GDPR regula el procesamiento de datos personales en la Unión Europea",
                "derechos_individuos": [
                    "Derecho de acceso",
                    "Derecho de rectificación",
                    "Derecho al olvido",
                    "Derecho a la portabilidad",
                    "Derecho de oposición",
                    "Derecho a no ser objeto de decisiones automatizadas",
                ],
                "principios": [
                    "Licitud, lealtad y transparencia",
                    "Limitación de la finalidad",
                    "Minimización de datos",
                    "Exactitud",
                    "Limitación del plazo de conservación",
                    "Integridad y confidencialidad",
                ],
                "sanciones": "Hasta €20M o 4% del volumen de negocio anual global",
            },
        )
        session.add(config_gdpr)

        # Configuración NOM-004-SSA3-2012 (México)
        config_nom = ConfiguracionCumplimiento(
            normativa=TipoNormativa.NOM_004,
            habilitado=True,
            requiere_firma_electronica=True,
            requiere_expediente_electronico=True,
            requiere_respaldo_informacion=True,
            requiere_autorizacion_acceso=True,
            requiere_log_acceso=True,
            dias_retencion_logs=1825,  # 5 años mínimo
            notas="Norma Oficial Mexicana del Expediente Clínico Electrónico",
            configuracion={
                "descripcion": "Establece los criterios científicos, éticos, tecnológicos y administrativos del expediente clínico electrónico",
                "requisitos_principales": [
                    "Expediente clínico electrónico único por paciente",
                    "Firma electrónica avanzada del personal médico",
                    "Integridad de la información",
                    "Confidencialidad y privacidad",
                    "Disponibilidad de la información",
                    "Respaldo y recuperación de información",
                    "Interoperabilidad entre sistemas",
                ],
                "contenido_minimo": [
                    "Datos de identificación del paciente",
                    "Historia clínica",
                    "Notas de evolución",
                    "Resultados de estudios",
                    "Tratamientos y prescripciones",
                    "Consentimientos informados",
                ],
                "tiempo_conservacion": "Mínimo 5 años después del último acto médico",
            },
        )
        session.add(config_nom)

        await session.commit()

        print("✅ Configuraciones iniciales creadas:")
        print("   - HIPAA (Health Insurance Portability and Accountability Act)")
        print("   - GDPR (General Data Protection Regulation)")
        print("   - NOM-004-SSA3-2012 (Expediente Clínico Electrónico)")


async def main():
    """Función principal"""
    try:
        await crear_tablas()
        await poblar_configuraciones_iniciales()

        print("\n" + "=" * 60)
        print("✅ Módulo de Cumplimiento Normativo configurado exitosamente")
        print("=" * 60)
        print("\n📚 Normativas soportadas:")
        print("   1. HIPAA - Protección de información médica (EE.UU.)")
        print("   2. GDPR - Protección de datos personales (Europa)")
        print("   3. NOM-004-SSA3-2012 - Expediente clínico electrónico (México)")
        print("\n🔐 Funcionalidades disponibles:")
        print("   ✓ Firma electrónica avanzada")
        print("   ✓ Consentimiento informado digital")
        print("   ✓ Logs de acceso a información sensible")
        print("   ✓ Solicitudes de datos personales (GDPR)")
        print("   ✓ Auditorías HIPAA")
        print("   ✓ Configuración por normativa")
        print("\n🌐 Endpoints API disponibles en:")
        print("   http://localhost:8612/docs#/Cumplimiento%20Normativo")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
