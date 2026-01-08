"""
Script para corregir la base de datos ahora
"""

import asyncio
import sys
from sqlalchemy import text
from app.core.database import engine


async def fix_database():
    print("Corrigiendo base de datos...")

    async with engine.begin() as conn:
        # Agregar medico_id a anomalias_detectadas
        try:
            await conn.execute(
                text(
                    """
                ALTER TABLE anomalias_detectadas 
                ADD COLUMN IF NOT EXISTS medico_id UUID REFERENCES usuarios(id) ON DELETE CASCADE;
            """
                )
            )
            print("✅ Campo medico_id agregado")
        except Exception as e:
            print(f"⚠️  {e}")

        # Verificar columnas
        result = await conn.execute(
            text(
                """
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'anomalias_detectadas'
            ORDER BY ordinal_position
        """
            )
        )
        columnas = [row[0] for row in result.fetchall()]
        print(f"\nColumnas en anomalias_detectadas: {', '.join(columnas)}")

        if "medico_id" in columnas:
            print("✅ medico_id existe")
        else:
            print("❌ medico_id NO existe")

    print("\n✅ Corrección completada")


if __name__ == "__main__":
    asyncio.run(fix_database())
