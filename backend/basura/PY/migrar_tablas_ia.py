"""
Script directo para crear tablas de IA Médica
"""

import asyncio
import sys
from pathlib import Path

# Agregar directorio al path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import text
from app.core.database import engine


async def crear_tablas():
    """Crear todas las tablas de IA Médica"""

    # SQL directo para crear las tablas
    statements = [
        # Tabla analisis_ia
        """
        CREATE TABLE IF NOT EXISTS analisis_ia (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            paciente_id UUID NOT NULL REFERENCES pacientes(id) ON DELETE CASCADE,
            medico_id UUID NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
            tipo_analisis VARCHAR(100) NOT NULL,
            contexto JSONB,
            resultado JSONB,
            confianza FLOAT,
            modelo_ia VARCHAR(100),
            version_modelo VARCHAR(50),
            tokens_utilizados INTEGER,
            tiempo_procesamiento FLOAT,
            validado_por_medico BOOLEAN DEFAULT FALSE,
            fecha_validacion TIMESTAMP,
            notas_medico TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        "CREATE INDEX IF NOT EXISTS idx_analisis_ia_paciente ON analisis_ia(paciente_id)",
        "CREATE INDEX IF NOT EXISTS idx_analisis_ia_medico ON analisis_ia(medico_id)",
        "CREATE INDEX IF NOT EXISTS idx_analisis_ia_tipo ON analisis_ia(tipo_analisis)",
        "CREATE INDEX IF NOT EXISTS idx_analisis_ia_fecha ON analisis_ia(created_at)",
        # Tabla predicciones_riesgo
        """
        CREATE TABLE IF NOT EXISTS predicciones_riesgo (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            paciente_id UUID NOT NULL REFERENCES pacientes(id) ON DELETE CASCADE,
            medico_id UUID NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
            tipo_riesgo VARCHAR(100) NOT NULL,
            nivel_riesgo VARCHAR(50),
            porcentaje_riesgo FLOAT,
            factores_riesgo TEXT[],
            factores_protectores TEXT[],
            recomendaciones TEXT[],
            estudios_sugeridos TEXT[],
            datos_utilizados JSONB,
            algoritmo VARCHAR(100),
            valido_hasta TIMESTAMP,
            validado_por_medico BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        "CREATE INDEX IF NOT EXISTS idx_predicciones_riesgo_paciente ON predicciones_riesgo(paciente_id)",
        "CREATE INDEX IF NOT EXISTS idx_predicciones_riesgo_tipo ON predicciones_riesgo(tipo_riesgo)",
        # Tabla recomendaciones_tratamiento
        """
        CREATE TABLE IF NOT EXISTS recomendaciones_tratamiento (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            paciente_id UUID NOT NULL REFERENCES pacientes(id) ON DELETE CASCADE,
            medico_id UUID NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
            diagnostico_principal VARCHAR(200) NOT NULL,
            codigo_cie10 VARCHAR(20),
            sintomas TEXT[],
            comorbilidades TEXT[],
            medicamentos_sugeridos JSONB,
            terapias_no_farmacologicas TEXT[],
            cambios_estilo_vida TEXT[],
            contraindicaciones TEXT[],
            precauciones TEXT[],
            guias_clinicas TEXT[],
            nivel_evidencia VARCHAR(10),
            prioridad VARCHAR(50),
            validado_por_medico BOOLEAN DEFAULT FALSE,
            aplicado BOOLEAN DEFAULT FALSE,
            fecha_aplicacion TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        "CREATE INDEX IF NOT EXISTS idx_recomendaciones_tratamiento_paciente ON recomendaciones_tratamiento(paciente_id)",
        "CREATE INDEX IF NOT EXISTS idx_recomendaciones_tratamiento_diagnostico ON recomendaciones_tratamiento(diagnostico_principal)",
        # Tabla interacciones_medicamentosas
        """
        CREATE TABLE IF NOT EXISTS interacciones_medicamentosas (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            paciente_id UUID NOT NULL REFERENCES pacientes(id) ON DELETE CASCADE,
            medico_id UUID NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
            medicamentos_analizados TEXT[],
            interacciones_encontradas JSONB,
            severidad_maxima VARCHAR(50),
            alertas_criticas TEXT[],
            recomendaciones_ajuste TEXT[],
            alergias_consideradas TEXT[],
            condiciones_consideradas TEXT[],
            validado_por_medico BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        "CREATE INDEX IF NOT EXISTS idx_interacciones_medicamentosas_paciente ON interacciones_medicamentosas(paciente_id)",
        "CREATE INDEX IF NOT EXISTS idx_interacciones_medicamentosas_severidad ON interacciones_medicamentosas(severidad_maxima)",
        # Tabla anomalias_detectadas
        """
        CREATE TABLE IF NOT EXISTS anomalias_detectadas (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            paciente_id UUID NOT NULL REFERENCES pacientes(id) ON DELETE CASCADE,
            tipo_estudio VARCHAR(100) NOT NULL,
            estudio_id UUID,
            tipo_anomalia VARCHAR(100),
            severidad VARCHAR(50),
            descripcion TEXT,
            localizacion VARCHAR(200),
            valores_anormales JSONB,
            patron_detectado VARCHAR(200),
            confianza_deteccion FLOAT,
            requiere_atencion_inmediata BOOLEAN DEFAULT FALSE,
            recomendaciones TEXT[],
            estudios_adicionales TEXT[],
            revisado_por_medico BOOLEAN DEFAULT FALSE,
            medico_revisor_id UUID REFERENCES usuarios(id),
            fecha_revision TIMESTAMP,
            notas_revision TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        "CREATE INDEX IF NOT EXISTS idx_anomalias_detectadas_paciente ON anomalias_detectadas(paciente_id)",
        "CREATE INDEX IF NOT EXISTS idx_anomalias_detectadas_tipo_estudio ON anomalias_detectadas(tipo_estudio)",
        "CREATE INDEX IF NOT EXISTS idx_anomalias_detectadas_severidad ON anomalias_detectadas(severidad)",
        "CREATE INDEX IF NOT EXISTS idx_anomalias_detectadas_revisado ON anomalias_detectadas(revisado_por_medico)",
        # Tabla asistente_ia
        """
        CREATE TABLE IF NOT EXISTS asistente_ia (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            medico_id UUID NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
            paciente_id UUID REFERENCES pacientes(id) ON DELETE CASCADE,
            pregunta TEXT NOT NULL,
            respuesta TEXT NOT NULL,
            contexto_utilizado JSONB,
            tipo_consulta VARCHAR(100),
            referencias TEXT[],
            tokens_utilizados INTEGER,
            tiempo_respuesta FLOAT,
            valoracion_medico INTEGER,
            util BOOLEAN,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        "CREATE INDEX IF NOT EXISTS idx_asistente_ia_medico ON asistente_ia(medico_id)",
        "CREATE INDEX IF NOT EXISTS idx_asistente_ia_paciente ON asistente_ia(paciente_id)",
        "CREATE INDEX IF NOT EXISTS idx_asistente_ia_tipo ON asistente_ia(tipo_consulta)",
        "CREATE INDEX IF NOT EXISTS idx_asistente_ia_fecha ON asistente_ia(created_at)",
    ]

    print("🤖 Creando tablas de IA Médica...")
    print(f"📊 Total de statements: {len(statements)}\n")

    async with engine.begin() as conn:
        for i, stmt in enumerate(statements, 1):
            try:
                await conn.execute(text(stmt))
                # Determinar qué se está creando
                if "CREATE TABLE" in stmt:
                    table_name = (
                        stmt.split("CREATE TABLE IF NOT EXISTS")[1]
                        .split("(")[0]
                        .strip()
                    )
                    print(f"✅ [{i:2d}/{len(statements)}] Tabla: {table_name}")
                elif "CREATE INDEX" in stmt:
                    index_name = (
                        stmt.split("CREATE INDEX IF NOT EXISTS")[1]
                        .split("ON")[0]
                        .strip()
                    )
                    print(f"✅ [{i:2d}/{len(statements)}] Índice: {index_name}")
            except Exception as e:
                print(f"⚠️  [{i:2d}/{len(statements)}] Error: {str(e)[:80]}")

    print("\n" + "=" * 60)
    print("✅ MIGRACIÓN COMPLETADA EXITOSAMENTE")
    print("=" * 60)
    print("\n📋 Tablas creadas:")
    print("   1. analisis_ia")
    print("   2. predicciones_riesgo")
    print("   3. recomendaciones_tratamiento")
    print("   4. interacciones_medicamentosas")
    print("   5. anomalias_detectadas")
    print("   6. asistente_ia")
    print("\n🔄 El servidor backend se reiniciará automáticamente")
    print("🌐 Verifica en: http://localhost:8612/docs")


if __name__ == "__main__":
    try:
        asyncio.run(crear_tablas())
    except KeyboardInterrupt:
        print("\n⚠️  Migración cancelada por el usuario")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
