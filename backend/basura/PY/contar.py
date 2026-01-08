import asyncio
from app.core.database import AsyncSessionLocal
from app.models.hospitalizacion import Cama, Hospitalizacion
from app.models.interconsulta import Interconsulta
from sqlalchemy import select, func

async def main():
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(func.count(Cama.id)))
        camas = result.scalar()
        
        result = await db.execute(select(func.count(Hospitalizacion.id)))
        hosp = result.scalar()
        
        result = await db.execute(select(func.count(Interconsulta.id)))
        inter = result.scalar()
        
        print(f"Camas: {camas}")
        print(f"Hospitalizaciones: {hosp}")
        print(f"Interconsultas: {inter}")

asyncio.run(main())
