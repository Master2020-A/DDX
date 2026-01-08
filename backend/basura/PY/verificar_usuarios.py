"""
Script para verificar qué usuarios existen en la base de datos
"""
import asyncio
from app.core.database import AsyncSessionLocal
from app.models.usuario import Usuario
from sqlalchemy import select


async def listar_usuarios():
    """Listar todos los usuarios en la base de datos"""
    
    print('='*60)
    print('USUARIOS EN LA BASE DE DATOS')
    print('='*60)
    
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Usuario))
        usuarios = result.scalars().all()
        
        if not usuarios:
            print('\n[INFO] No hay usuarios en la base de datos')
            print('\nPara crear el usuario admin ejecuta:')
            print('  python crear_admin.py')
        else:
            print(f'\nTotal de usuarios: {len(usuarios)}\n')
            for user in usuarios:
                print(f'ID: {user.id}')
                print(f'Email: {user.email}')
                print(f'Nombre: {user.nombre_completo}')
                print(f'Rol: {user.rol}')
                print(f'Activo: {user.activo}')
                print(f'Password Hash: {user.password_hash[:30]}...')
                print('-'*60)
    
    print('='*60)


if __name__ == "__main__":
    try:
        asyncio.run(listar_usuarios())
    except Exception as e:
        print(f'\n[ERROR] {e}')
        import traceback
        traceback.print_exc()
