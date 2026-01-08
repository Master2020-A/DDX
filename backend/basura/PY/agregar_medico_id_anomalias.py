"""
Script para agregar el campo medico_id a la tabla anomalias_detectadas
"""

import asyncio
from sqlalchemy import text
from app.core.database import async_session_maker


async def agregar_campo():
    print("=" * 60)
    print("AGREGANDO CAMPO medico_id A anomalias_detectadas")
    print("=" * 60)
    print()

    async with async_session_maker() as session:
        try:
            # Agregar columna medico_id
            print("1. Agregando columna medico_id...")
            await session.execute(
                text(
                    """
                ALTER TABLE anomalias_detectadas 
                ADD COLUMN IF NOT EXISTS medico_id UUID REFERENCES usuarios(id) ON DELETE CASCADE;
            """
                )
            )
            print("   ✅ Columna medico_id agregada")

            # Actualizar registros existentes (si los hay) con un médico por defecto
            print("\n2. Verificando registros existentes...")
            result = await session.execute(
                text("SELECT COUNT(*) FROM anomalias_detectadas")
            )
            count = result.scalar()

            if count > 0:
                print(f"   ⚠️  Hay {count} registros existentes")
                print(
                    "   ℹ️  Necesitas actualizar manualmente el medico_id de estos registros"
                )
            else:
                print("   ✅ No hay registros existentes")

            await session.commit()

            print()
            print("=" * 60)
            print("✅ CAMPO AGREGADO EXITOSAMENTE")
            print("=" * 60)

        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            await session.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(agregar_campo())
