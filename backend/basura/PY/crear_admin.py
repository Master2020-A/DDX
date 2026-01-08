"""
Script para crear usuario administrador por defecto
Ejecutar: python crear_admin.py
"""
import asyncio
from app.core.database import AsyncSessionLocal
from app.models.usuario import Usuario
from app.core.security import get_password_hash


async def create_admin():
    """Crear usuario administrador por defecto"""
    
    print('='*60)
    print('CREANDO USUARIO ADMINISTRADOR')
    print('='*60)
    
    async with AsyncSessionLocal() as session:
        # Verificar si ya existe un admin
        from sqlalchemy import select
        result = await session.execute(
            select(Usuario).where(Usuario.email == 'admin@ddx.com')
        )
        existing_admin = result.scalar_one_or_none()
        
        if existing_admin:
            print('[INFO] El usuario admin@ddx.com ya existe')
            print('='*60)
            return
        
        # Crear usuario admin
        admin = Usuario(
            email='admin@ddx.com',
            password_hash=get_password_hash('Admin123!'),
            nombre_completo='Administrador del Sistema',
            rol='admin',
            activo=True
        )
        
        session.add(admin)
        await session.commit()
        
        print('[OK] Usuario administrador creado exitosamente')
        print('='*60)
        print('Email:    admin@ddx.com')
        print('Password: Admin123!')
        print('='*60)
        print('\n[IMPORTANTE] Cambia la contrasena despues del primer login')
        print('='*60)


if __name__ == "__main__":
    try:
        asyncio.run(create_admin())
    except Exception as e:
        print(f'\n[ERROR] No se pudo crear el usuario: {e}')
        print('\nVerifica que:')
        print('1. PostgreSQL este corriendo')
        print('2. La base de datos ddx_db exista')
        print('3. El archivo .env este configurado correctamente')
        print('4. Las tablas esten creadas (ejecuta schema.sql)')
