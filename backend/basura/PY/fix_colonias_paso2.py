"""Paso 2: Eliminar CP 83288 antiguo (solo 1 colonia)"""
import asyncio
from sqlalchemy import delete
from app.core.database import AsyncSessionLocal
from app.models.catalogos import CodigoPostal


async def clean():
    async with AsyncSessionLocal() as db:
        await db.execute(delete(CodigoPostal).where(CodigoPostal.codigo_postal == '83288'))
        await db.commit()
        print('✅ CP 83288 eliminado')


if __name__ == "__main__":
    asyncio.run(clean())
