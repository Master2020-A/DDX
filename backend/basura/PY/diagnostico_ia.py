"""
Script de diagnóstico para el módulo de IA
"""

import asyncio
import sys
from sqlalchemy import text
from app.core.database import async_session_maker


async def diagnosticar():
    print("=" * 60)
    print("DIAGNÓSTICO DEL MÓDULO DE IA")
    print("=" * 60)
    print()

    async with async_session_maker() as session:
        # Verificar tablas de IA
        tablas_ia = [
            "analisis_ia",
            "predicciones_riesgo",
            "recomendaciones_tratamiento",
            "interacciones_medicamentosas",
            "anomalias_detectadas",
            "asistente_ia",
        ]

        print("1. VERIFICANDO TABLAS DE IA:")
        print("-" * 60)

        for tabla in tablas_ia:
            try:
                result = await session.execute(text(f"SELECT COUNT(*) FROM {tabla}"))
                count = result.scalar()
                print(f"✅ {tabla}: {count} registros")
            except Exception as e:
                print(f"❌ {tabla}: ERROR - {str(e)[:100]}")

        print()
        print("2. VERIFICANDO MODELO PACIENTE:")
        print("-" * 60)

        try:
            result = await session.execute(
                text(
                    "SELECT column_name FROM information_schema.columns WHERE table_name = 'pacientes'"
                )
            )
            columnas = [row[0] for row in result.fetchall()]
            print(f"✅ Columnas en pacientes: {', '.join(columnas[:10])}...")

            # Verificar columnas específicas
            columnas_requeridas = ["edad", "genero", "alergias"]
            for col in columnas_requeridas:
                if col in columnas:
                    print(f"   ✅ {col}")
                else:
                    print(f"   ❌ {col} NO EXISTE")
        except Exception as e:
            print(f"❌ ERROR: {e}")

        print()
        print("3. VERIFICANDO MODELO EXPEDIENTE_CLINICO:")
        print("-" * 60)

        try:
            result = await session.execute(
                text("SELECT COUNT(*) FROM expedientes_clinicos")
            )
            count = result.scalar()
            print(f"✅ expedientes_clinicos: {count} registros")

            result = await session.execute(
                text(
                    "SELECT column_name FROM information_schema.columns WHERE table_name = 'expedientes_clinicos'"
                )
            )
            columnas = [row[0] for row in result.fetchall()]

            if "signos_vitales" in columnas:
                print(f"   ✅ signos_vitales existe")
            else:
                print(f"   ❌ signos_vitales NO EXISTE")
        except Exception as e:
            print(f"❌ ERROR: {e}")

        print()
        print("4. VERIFICANDO MODELO CONSULTA:")
        print("-" * 60)

        try:
            result = await session.execute(
                text(
                    "SELECT column_name FROM information_schema.columns WHERE table_name = 'consultas'"
                )
            )
            columnas = [row[0] for row in result.fetchall()]

            if "fecha_hora" in columnas:
                print(f"   ✅ fecha_hora existe")
            else:
                print(f"   ❌ fecha_hora NO EXISTE")

            if "fecha" in columnas:
                print(f"   ⚠️  fecha existe (debería ser fecha_hora)")
        except Exception as e:
            print(f"❌ ERROR: {e}")

        print()
        print("5. VERIFICANDO OPENAI_API_KEY:")
        print("-" * 60)

        try:
            from app.core.config import settings

            if settings.OPENAI_API_KEY:
                key_preview = (
                    settings.OPENAI_API_KEY[:10] + "..." + settings.OPENAI_API_KEY[-4:]
                )
                print(f"✅ OPENAI_API_KEY configurada: {key_preview}")
            else:
                print(f"❌ OPENAI_API_KEY NO configurada")
        except Exception as e:
            print(f"❌ ERROR: {e}")

        print()
        print("=" * 60)
        print("DIAGNÓSTICO COMPLETADO")
        print("=" * 60)


if __name__ == "__main__":
    asyncio.run(diagnosticar())
