"""
Script para verificar y corregir la tabla anomalias_detectadas
"""

import asyncio
from sqlalchemy import text
from app.core.database import async_session_maker


async def verificar_y_corregir():
    print("=" * 60)
    print("VERIFICANDO Y CORRIGIENDO anomalias_detectadas")
    print("=" * 60)
    print()

    async with async_session_maker() as session:
        try:
            # Verificar columnas actuales
            print("1. Verificando columnas actuales...")
            result = await session.execute(
                text(
                    """
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'anomalias_detectadas'
                ORDER BY ordinal_position
            """
                )
            )
            columnas = result.fetchall()

            print(f"   Columnas encontradas: {len(columnas)}")
            for col in columnas:
                print(f"   - {col[0]}: {col[1]}")

            # Verificar si existe medico_id
            columnas_nombres = [col[0] for col in columnas]

            if "medico_id" not in columnas_nombres:
                print("\n2. ❌ Campo medico_id NO existe - Agregándolo...")
                await session.execute(
                    text(
                        """
                    ALTER TABLE anomalias_detectadas 
                    ADD COLUMN medico_id UUID REFERENCES usuarios(id) ON DELETE CASCADE;
                """
                    )
                )
                await session.commit()
                print("   ✅ Campo medico_id agregado exitosamente")
            else:
                print("\n2. ✅ Campo medico_id ya existe")

            print()
            print("=" * 60)
            print("✅ VERIFICACIÓN COMPLETADA")
            print("=" * 60)

        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            import traceback

            traceback.print_exc()
            await session.rollback()


if __name__ == "__main__":
    asyncio.run(verificar_y_corregir())
