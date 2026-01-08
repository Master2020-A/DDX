"""
Script definitivo para crear tablas de IA Médica
"""

import asyncio
from sqlalchemy import text
from app.core.database import async_session_maker


async def crear_tablas():
    print("=" * 60)
    print("CREANDO TABLAS DE IA MÉDICA")
    print("=" * 60)
    print()

    async with async_session_maker() as session:
        try:
            # 1. Tabla analisis_ia
            print("1. Creando tabla analisis_ia...")
            await session.execute(
                text(
                    """
                CREATE TABLE IF NOT EXISTS analisis_ia (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    paciente_id UUID NOT NULL REFERENCES pacientes(id) ON DELETE CASCADE,
                    medico_id UUID NOT NULL REFERENCES usuarios(id),
                    tipo_analisis VARCHAR(100) NOT NULL,
                    resultado JSONB NOT NULL,
                    confianza FLOAT,
                    modelo_ia VARCHAR(100),
                    version_modelo VARCHAR(50),
                    tiempo_procesamiento FLOAT,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """
                )
            )
            print("   ✅ analisis_ia creada")

            # 2. Tabla predicciones_riesgo
            print("2. Creando tabla predicciones_riesgo...")
            await session.execute(
                text(
                    """
                CREATE TABLE IF NOT EXISTS predicciones_riesgo (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    paciente_id UUID NOT NULL REFERENCES pacientes(id) ON DELETE CASCADE,
                    medico_id UUID NOT NULL REFERENCES usuarios(id),
                    tipo_riesgo VARCHAR(100) NOT NULL,
                    nivel_riesgo VARCHAR(50) NOT NULL,
                    porcentaje_riesgo FLOAT NOT NULL,
                    factores_riesgo TEXT[],
                    factores_protectores TEXT[],
                    recomendaciones TEXT[],
                    estudios_sugeridos TEXT[],
                    algoritmo VARCHAR(100),
                    datos_utilizados JSONB,
                    valido_hasta TIMESTAMP WITH TIME ZONE,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """
                )
            )
            print("   ✅ predicciones_riesgo creada")

            # 3. Tabla recomendaciones_tratamiento
            print("3. Creando tabla recomendaciones_tratamiento...")
            await session.execute(
                text(
                    """
                CREATE TABLE IF NOT EXISTS recomendaciones_tratamiento (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    paciente_id UUID NOT NULL REFERENCES pacientes(id) ON DELETE CASCADE,
                    medico_id UUID NOT NULL REFERENCES usuarios(id),
                    diagnostico_principal VARCHAR(255) NOT NULL,
                    codigo_cie10 VARCHAR(20),
                    medicamentos JSONB,
                    dosis_recomendadas JSONB,
                    duracion_tratamiento VARCHAR(100),
                    contraindicaciones TEXT[],
                    precauciones TEXT[],
                    guias_clinicas TEXT[],
                    nivel_evidencia VARCHAR(50),
                    aplicado BOOLEAN DEFAULT FALSE,
                    fecha_aplicacion TIMESTAMP WITH TIME ZONE,
                    notas_medico TEXT,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """
                )
            )
            print("   ✅ recomendaciones_tratamiento creada")

            # 4. Tabla interacciones_medicamentosas
            print("4. Creando tabla interacciones_medicamentosas...")
            await session.execute(
                text(
                    """
                CREATE TABLE IF NOT EXISTS interacciones_medicamentosas (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    paciente_id UUID NOT NULL REFERENCES pacientes(id) ON DELETE CASCADE,
                    medico_id UUID NOT NULL REFERENCES usuarios(id),
                    medicamentos TEXT[] NOT NULL,
                    interacciones JSONB NOT NULL,
                    severidad_maxima VARCHAR(50),
                    requiere_ajuste BOOLEAN DEFAULT FALSE,
                    recomendaciones TEXT[],
                    revisado_por_medico BOOLEAN DEFAULT FALSE,
                    fecha_revision TIMESTAMP WITH TIME ZONE,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """
                )
            )
            print("   ✅ interacciones_medicamentosas creada")

            # 5. Tabla anomalias_detectadas
            print("5. Creando tabla anomalias_detectadas...")
            await session.execute(
                text(
                    """
                CREATE TABLE IF NOT EXISTS anomalias_detectadas (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    paciente_id UUID NOT NULL REFERENCES pacientes(id) ON DELETE CASCADE,
                    tipo_estudio VARCHAR(100) NOT NULL,
                    estudio_id UUID,
                    tipo_anomalia VARCHAR(100) NOT NULL,
                    descripcion TEXT NOT NULL,
                    severidad VARCHAR(50) NOT NULL,
                    requiere_atencion_inmediata BOOLEAN DEFAULT FALSE,
                    valores_anormales JSONB,
                    recomendaciones TEXT[],
                    revisado_por_medico BOOLEAN DEFAULT FALSE,
                    medico_revisor_id UUID REFERENCES usuarios(id),
                    fecha_revision TIMESTAMP WITH TIME ZONE,
                    notas_revision TEXT,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """
                )
            )
            print("   ✅ anomalias_detectadas creada")

            # 6. Tabla asistente_ia
            print("6. Creando tabla asistente_ia...")
            await session.execute(
                text(
                    """
                CREATE TABLE IF NOT EXISTS asistente_ia (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    medico_id UUID NOT NULL REFERENCES usuarios(id),
                    paciente_id UUID REFERENCES pacientes(id) ON DELETE CASCADE,
                    pregunta TEXT NOT NULL,
                    respuesta TEXT NOT NULL,
                    contexto JSONB,
                    tipo_consulta VARCHAR(100),
                    modelo_ia VARCHAR(100),
                    tokens_utilizados INTEGER,
                    tiempo_respuesta FLOAT,
                    valoracion INTEGER,
                    feedback TEXT,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """
                )
            )
            print("   ✅ asistente_ia creada")

            # Crear índices
            print("\n7. Creando índices...")
            await session.execute(
                text(
                    "CREATE INDEX IF NOT EXISTS idx_analisis_ia_paciente ON analisis_ia(paciente_id);"
                )
            )
            await session.execute(
                text(
                    "CREATE INDEX IF NOT EXISTS idx_predicciones_riesgo_paciente ON predicciones_riesgo(paciente_id);"
                )
            )
            await session.execute(
                text(
                    "CREATE INDEX IF NOT EXISTS idx_recomendaciones_tratamiento_paciente ON recomendaciones_tratamiento(paciente_id);"
                )
            )
            await session.execute(
                text(
                    "CREATE INDEX IF NOT EXISTS idx_interacciones_medicamentosas_paciente ON interacciones_medicamentosas(paciente_id);"
                )
            )
            await session.execute(
                text(
                    "CREATE INDEX IF NOT EXISTS idx_anomalias_detectadas_paciente ON anomalias_detectadas(paciente_id);"
                )
            )
            await session.execute(
                text(
                    "CREATE INDEX IF NOT EXISTS idx_asistente_ia_medico ON asistente_ia(medico_id);"
                )
            )
            print("   ✅ Índices creados")

            await session.commit()

            print()
            print("=" * 60)
            print("✅ TODAS LAS TABLAS CREADAS EXITOSAMENTE")
            print("=" * 60)

        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            await session.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(crear_tablas())
