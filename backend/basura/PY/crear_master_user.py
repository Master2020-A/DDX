"""
Script para crear usuario master@master.com
"""
import asyncio
from app.core.database import AsyncSessionLocal
from app.models.usuario import Usuario
from app.core.security import get_password_hash
from sqlalchemy import select


async def create_master_user():
    print('='*70)
    print('CREANDO USUARIO master@master.com')
    print('='*70)
    
    async with AsyncSessionLocal() as session:
        try:
            # Verificar si ya existe
            result = await session.execute(
                select(Usuario).where(Usuario.email == 'master@master.com')
            )
            existing = result.scalar_one_or_none()
            
            if existing:
                print('\n✅ El usuario master@master.com YA EXISTE')
                print(f'   Nombre: {existing.nombre_completo}')
                print(f'   Rol: {existing.rol}')
                print(f'   Activo: {existing.activo}')
                print('\n💡 Puedes usar estas credenciales para entrar:')
                print('   Email: master@master.com')
                print('   Password: Master123!')
                print('='*70)
                return
            
            # Crear usuario master
            master = Usuario(
                email='master@master.com',
                password_hash=get_password_hash('Master123!'),
                nombre_completo='Master Usuario',
                rol='admin',
                activo=True
            )
            
            session.add(master)
            await session.commit()
            
            print('\n✅ Usuario creado exitosamente!')
            print('='*70)
            print('📧 Email:    master@master.com')
            print('🔑 Password: Master123!')
            print('👤 Rol:      admin')
            print('='*70)
            print('\n💡 Ahora puedes hacer login con estas credenciales')
            print('='*70)
            
        except Exception as e:
            print(f'\n❌ ERROR: {e}')
            print('\nVerifica que:')
            print('1. PostgreSQL esté corriendo')
            print('2. La base de datos ddx_db exista')
            print('3. Las tablas estén creadas')


if __name__ == "__main__":
    asyncio.run(create_master_user())
