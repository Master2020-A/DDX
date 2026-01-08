"""Paso 1: Eliminar constraint UNIQUE del código postal"""
import asyncio
from sqlalchemy import text
from app.core.database import AsyncSessionLocal


async def fix():
    async with AsyncSessionLocal() as db:
        await db.execute(text('ALTER TABLE codigos_postales DROP CONSTRAINT IF EXISTS codigos_postales_codigo_postal_key'))
        await db.commit()
        print('✅ Constraint UNIQUE eliminado')


if __name__ == "__main__":
    asyncio.run(fix())
