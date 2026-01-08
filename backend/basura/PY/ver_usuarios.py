"""Ver usuarios y sus roles"""
import asyncio
from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.usuario import Usuario

async def main():
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Usuario))
        usuarios = result.scalars().all()
        
        print("\n👥 USUARIOS EN EL SISTEMA:")
        print("-" * 80)
        for u in usuarios:
            print(f"  ID: {u.id}")
            print(f"  Username: {u.username}")
            print(f"  Email: {u.email}")
            print(f"  Rol: {u.rol}")
            print(f"  Activo: {u.activo}")
            print("-" * 80)
        
        print(f"\nTotal: {len(usuarios)} usuarios\n")

asyncio.run(main())
