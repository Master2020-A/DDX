"""
Script para agregar columna medico_id a anomalias_detectadas
"""

import asyncio
from sqlalchemy import text
from app.core.database import engine


async def fix_anomalias():
    print("=" * 60)
    print("CORRIGIENDO TABLA anomalias_detectadas")
    print("=" * 60)

    async with engine.begin() as conn:
        # Agregar columna medico_id
        try:
            await conn.execute(
                text(
                    """
                ALTER TABLE anomalias_detectadas 
                ADD COLUMN IF NOT EXISTS medico_id UUID REFERENCES usuarios(id) ON DELETE CASCADE;
            """
                )
            )
            print("✅ Columna medico_id agregada")
        except Exception as e:
            print(f"⚠️  Error al agregar columna: {e}")

        # Verificar columnas
        result = await conn.execute(
            text(
                """
            SELECT column_name, data_type, is_nullable 
            FROM information_schema.columns 
            WHERE table_name = 'anomalias_detectadas'
            ORDER BY ordinal_position;
        """
            )
        )

        print("\n📋 Columnas en anomalias_detectadas:")
        for row in result.fetchall():
            nullable = "NULL" if row[2] == "YES" else "NOT NULL"
            print(f"  - {row[0]}: {row[1]} ({nullable})")

    print("\n✅ Corrección completada")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(fix_anomalias())
