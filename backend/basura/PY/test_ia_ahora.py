"""
Script para probar el módulo de IA y ver qué está fallando
"""

import asyncio
import sys
from sqlalchemy import text
from app.core.database import engine


async def test_sistema():
    print("=" * 60)
    print("DIAGNÓSTICO DEL MÓDULO DE IA")
    print("=" * 60)

    try:
        # 1. Verificar conexión a BD
        print("\n1. Verificando conexión a base de datos...")
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT 1"))
            print("   ✅ Conexión a BD exitosa")

        # 2. Verificar tablas de IA
        print("\n2. Verificando tablas de IA...")
        async with engine.begin() as conn:
            tablas = [
                "analisis_ia",
                "predicciones_riesgo",
                "recomendaciones_tratamiento",
                "interacciones_medicamentosas",
                "anomalias_detectadas",
                "asistente_ia",
            ]
            for tabla in tablas:
                result = await conn.execute(
                    text(
                        f"""
                    SELECT COUNT(*) FROM information_schema.tables 
                    WHERE table_name = '{tabla}'
                """
                    )
                )
                existe = result.scalar()
                if existe:
                    print(f"   ✅ {tabla}")
                else:
                    print(f"   ❌ {tabla} NO EXISTE")

        # 3. Verificar columnas de anomalias_detectadas
        print("\n3. Verificando columnas de anomalias_detectadas...")
        async with engine.begin() as conn:
            result = await conn.execute(
                text(
                    """
                SELECT column_name FROM information_schema.columns 
                WHERE table_name = 'anomalias_detectadas'
                ORDER BY ordinal_position
            """
                )
            )
            columnas = [row[0] for row in result.fetchall()]
            print(f"   Columnas: {', '.join(columnas)}")
            if "medico_id" in columnas:
                print("   ✅ medico_id existe en BD")
            else:
                print(
                    "   ⚠️  medico_id NO existe en BD (esperado - está comentado en el modelo)"
                )

        # 4. Probar importación del cliente de IA
        print("\n4. Probando cliente de IA...")
        try:
            from app.services.openai_client import (
                chat_completion,
                AI_PROVIDER,
                DEFAULT_MODEL,
            )

            print(f"   ✅ Cliente importado correctamente")
            print(f"   Proveedor: {AI_PROVIDER}")
            print(f"   Modelo: {DEFAULT_MODEL}")
        except Exception as e:
            print(f"   ❌ Error al importar cliente: {e}")

        # 5. Probar servicios de IA
        print("\n5. Probando servicios de IA...")
        try:
            from app.services.prediccion_riesgo_service import PrediccionRiesgoService
            from app.services.asistente_ia_service import AsistenteIAService

            print("   ✅ Servicios importados correctamente")
        except Exception as e:
            print(f"   ❌ Error al importar servicios: {e}")

        # 6. Probar modelos
        print("\n6. Probando modelos de IA...")
        try:
            from app.models.ia_medica import (
                AnalisisIA,
                PrediccionRiesgo,
                RecomendacionTratamiento,
                InteraccionMedicamentosa,
                AnomaliaDetectada,
                AsistenteIA,
            )

            print("   ✅ Modelos importados correctamente")
        except Exception as e:
            print(f"   ❌ Error al importar modelos: {e}")
            import traceback

            traceback.print_exc()

        print("\n" + "=" * 60)
        print("DIAGNÓSTICO COMPLETADO")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ ERROR CRÍTICO: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_sistema())
