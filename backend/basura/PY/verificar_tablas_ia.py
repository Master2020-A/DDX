"""
Verificar que todas las tablas de IA existan
"""

import asyncio
from sqlalchemy import text, inspect
from app.core.database import engine


async def verificar_tablas():
    print("\n" + "=" * 60)
    print("VERIFICANDO TABLAS DE IA")
    print("=" * 60)

    tablas_requeridas = [
        "analisis_ia",
        "predicciones_riesgo",
        "recomendaciones_tratamiento",
        "interacciones_medicamentosas",
        "anomalias_detectadas",
        "asistente_ia",
    ]

    async with engine.begin() as conn:
        for tabla in tablas_requeridas:
            result = await conn.execute(
                text(
                    f"""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = '{tabla}'
                );
            """
                )
            )
            existe = result.scalar()

            if existe:
                # Contar registros
                result = await conn.execute(text(f"SELECT COUNT(*) FROM {tabla}"))
                count = result.scalar()
                print(f"✅ {tabla}: {count} registros")
            else:
                print(f"❌ {tabla}: NO EXISTE")

    print("=" * 60 + "\n")


if __name__ == "__main__":
    asyncio.run(verificar_tablas())
