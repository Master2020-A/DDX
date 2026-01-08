"""
Script alternativo para crear usuario admin sin problemas de bcrypt
Ejecutar: python crear_admin_fix.py
"""
import asyncio
from app.core.database import AsyncSessionLocal
from app.models.usuario import Usuario


def hash_password_simple(password: str) -> str:
    """Hash de password usando bcrypt directamente"""
    import bcrypt
    # Asegurar que el password no sea muy largo
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
    
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


async def create_admin():
    """Crear usuario administrador"""
    
    print('='*60)
    print('CREANDO USUARIO ADMINISTRADOR (VERSION FIX)')
    print('='*60)
    
    async with AsyncSessionLocal() as session:
        # Verificar si ya existe
        from sqlalchemy import select
        result = await session.execute(
            select(Usuario).where(Usuario.email == 'admin@ddx.com')
        )
        existing_admin = result.scalar_one_or_none()
        
        if existing_admin:
            print('[INFO] El usuario admin@ddx.com ya existe')
            print('='*60)
            return
        
        # Hash del password
        try:
            password_hash = hash_password_simple('Admin123!')
        except Exception as e:
            print(f'[ERROR] Error al hashear password: {e}')
            return
        
        # Crear usuario admin
        admin = Usuario(
            email='admin@ddx.com',
            password_hash=password_hash,
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
        import traceback
        traceback.print_exc()
