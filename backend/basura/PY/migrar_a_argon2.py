"""
Script para migrar usuarios de bcrypt a argon2
Ejecutar: python migrar_a_argon2.py
"""
import asyncio
from app.core.database import AsyncSessionLocal
from app.models.usuario import Usuario
from app.core.security import get_password_hash
from sqlalchemy import select, update


async def migrar_usuarios():
    """Actualizar hashes de contraseñas de bcrypt a argon2"""
    
    print('='*60)
    print('MIGRANDO USUARIOS A ARGON2')
    print('='*60)
    
    # Contraseñas por defecto para usuarios conocidos
    usuarios_default = {
        'admin@ddx.com': 'Admin123!',
    }
    
    async with AsyncSessionLocal() as session:
        # Obtener todos los usuarios
        result = await session.execute(select(Usuario))
        usuarios = result.scalars().all()
        
        if not usuarios:
            print('[INFO] No hay usuarios en la base de datos')
            print('='*60)
            return
        
        print(f'[INFO] Encontrados {len(usuarios)} usuarios')
        print()
        
        actualizados = 0
        for usuario in usuarios:
            # Si es un usuario conocido, actualizar con contraseña por defecto
            if usuario.email in usuarios_default:
                nueva_password = usuarios_default[usuario.email]
                nuevo_hash = get_password_hash(nueva_password)
                
                usuario.password_hash = nuevo_hash
                actualizados += 1
                
                print(f'✓ {usuario.email} - Actualizado con contraseña por defecto')
            else:
                # Para otros usuarios, generar contraseña temporal
                password_temporal = f'Temporal123!_{usuario.id}'
                nuevo_hash = get_password_hash(password_temporal)
                
                usuario.password_hash = nuevo_hash
                actualizados += 1
                
                print(f'✓ {usuario.email} - Contraseña temporal: {password_temporal}')
        
        await session.commit()
        
        print()
        print('='*60)
        print(f'[OK] {actualizados} usuarios actualizados a argon2')
        print('='*60)
        print()
        print('CREDENCIALES DE ACCESO:')
        print('-' * 60)
        print('Email:    admin@ddx.com')
        print('Password: Admin123!')
        print('-' * 60)
        print()
        print('[IMPORTANTE] Los usuarios deben cambiar sus contraseñas')
        print('='*60)


if __name__ == "__main__":
    try:
        asyncio.run(migrar_usuarios())
    except Exception as e:
        print(f'\n[ERROR] No se pudo migrar usuarios: {e}')
        print('\nVerifica que:')
        print('1. PostgreSQL esté corriendo')
        print('2. La base de datos ddx_db exista')
        print('3. El archivo .env esté configurado correctamente')
        print('4. argon2-cffi esté instalado: pip install argon2-cffi')
