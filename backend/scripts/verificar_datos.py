"""Script simple para verificar datos"""
import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select, func
from app.core.database import AsyncSessionLocal
from app.models.hospitalizacion import Cama, Hospitalizacion
from app.models.interconsulta import Interconsulta

async def main():
    async with AsyncSessionLocal() as db:
        # Contar camas
        result = await db.execute(select(func.count(Cama.id)))
        camas = result.scalar()
        print(f"Camas: {camas}")
        
        # Contar hospitalizaciones
        result = await db.execute(select(func.count(Hospitalizacion.id)))
        hosp = result.scalar()
        print(f"Hospitalizaciones: {hosp}")
        
        # Contar interconsultas
        result = await db.execute(select(func.count(Interconsulta.id)))
        inter = result.scalar()
        print(f"Interconsultas: {inter}")

if __name__ == "__main__":
    asyncio.run(main())
