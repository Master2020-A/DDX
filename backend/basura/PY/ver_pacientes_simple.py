"""Ver pacientes en la base de datos"""
import asyncio
from sqlalchemy import select, text
from app.core.database import AsyncSessionLocal
from app.models.paciente import Paciente

async def main():
    async with AsyncSessionLocal() as db:
        # Contar pacientes
        result = await db.execute(text("SELECT COUNT(*) FROM pacientes"))
        count = result.scalar()
        print(f"\n📊 Total de pacientes: {count}\n")
        
        if count > 0:
            # Mostrar primeros 5
            result = await db.execute(
                select(Paciente).limit(5)
            )
            pacientes = result.scalars().all()
            
            print("👥 PRIMEROS 5 PACIENTES:")
            print("-" * 80)
            for p in pacientes:
                print(f"  ID: {p.id}")
                print(f"  Nombre: {p.nombre_completo}")
                print(f"  Expediente: {p.numero_expediente}")
                print("-" * 80)

asyncio.run(main())
