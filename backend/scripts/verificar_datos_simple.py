"""Verificar datos simple con output directo"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

async def main():
    from sqlalchemy import select, func
    from app.core.database import AsyncSessionLocal
    from app.models.hospitalizacion import Cama, Hospitalizacion
    from app.models.interconsulta import Interconsulta
    
    async with AsyncSessionLocal() as db:
        # Contar camas
        result = await db.execute(select(func.count(Cama.id)))
        camas = result.scalar()
        
        # Contar hospitalizaciones
        result = await db.execute(select(func.count(Hospitalizacion.id)))
        hosp = result.scalar()
        
        # Contar interconsultas
        result = await db.execute(select(func.count(Interconsulta.id)))
        inter = result.scalar()
        
        # Escribir a archivo
        with open('verificacion.txt', 'w') as f:
            f.write(f"Camas: {camas}\n")
            f.write(f"Hospitalizaciones: {hosp}\n")
            f.write(f"Interconsultas: {inter}\n")
        
        print(f"Camas: {camas}")
        print(f"Hospitalizaciones: {hosp}")
        print(f"Interconsultas: {inter}")

if __name__ == "__main__":
    asyncio.run(main())
