"""
Script para verificar y corregir la base de datos
"""

import asyncio
from sqlalchemy import text
from app.core.database import engine


async def main():
    async with engine.begin() as conn:
        # Verificar columnas actuales
        print("\n📋 Columnas actuales en anomalias_detectadas:")
        result = await conn.execute(
            text(
                """
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'anomalias_detectadas'
            ORDER BY ordinal_position;
        """
            )
        )
        columnas = [row[0] for row in result.fetchall()]
        for col in columnas:
            print(f"  - {col}")

        # Agregar medico_id si no existe
        if "medico_id" not in columnas:
            print("\n⚠️  Columna medico_id NO existe, agregando...")
            await conn.execute(
                text(
                    """
                ALTER TABLE anomalias_detectadas 
                ADD COLUMN medico_id UUID REFERENCES usuarios(id) ON DELETE CASCADE;
            """
                )
            )
            print("✅ Columna medico_id agregada")
        else:
            print("\n✅ Columna medico_id ya existe")


asyncio.run(main())
