"""
Script para probar el login y verificar passwords
Ejecutar: python test_login.py
"""
import asyncio
from app.core.database import AsyncSessionLocal
from app.models.usuario import Usuario
from app.core.security import verify_password, get_password_hash
from sqlalchemy import select


async def test_password():
    """Probar si los passwords funcionan correctamente"""
    
    print('='*60)
    print('TEST DE VERIFICACION DE PASSWORD')
    print('='*60)
    
    # 1. Probar hash y verificacion directa
    print('\n[1] Probando hash y verificacion directa...')
    test_password = 'Admin123!'
    hashed = get_password_hash(test_password)
    print(f'Password original: {test_password}')
    print(f'Hash generado: {hashed[:50]}...')
    
    is_valid = verify_password(test_password, hashed)
    print(f'Verificacion directa: {"OK" if is_valid else "FALLO"}')
    
    # 2. Verificar password del admin en la DB
    print('\n[2] Verificando admin@ddx.com en base de datos...')
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Usuario).where(Usuario.email == 'admin@ddx.com')
        )
        admin = result.scalar_one_or_none()
        
        if not admin:
            print('[ERROR] Usuario admin@ddx.com no encontrado')
            return
        
        print(f'Usuario encontrado: {admin.email}')
        print(f'Nombre: {admin.nombre_completo}')
        print(f'Activo: {admin.activo}')
        print(f'Password hash: {admin.password_hash[:50]}...')
        
        # Probar password
        passwords_to_test = ['Admin123!', 'admin123!', 'Admin123']
        
        print('\n[3] Probando diferentes passwords...')
        for pwd in passwords_to_test:
            try:
                is_valid = verify_password(pwd, admin.password_hash)
                print(f'  "{pwd}": {"OK ✓" if is_valid else "FALLO ✗"}')
            except Exception as e:
                print(f'  "{pwd}": ERROR - {e}')
        
        # 4. Verificar longitud del password hash
        print(f'\n[4] Longitud del hash: {len(admin.password_hash)} caracteres')
        print(f'Formato bcrypt: {"OK" if admin.password_hash.startswith("$2b$") else "FALLO"}')
    
    print('\n' + '='*60)


async def simulate_login():
    """Simular el proceso de login"""
    
    print('\n' + '='*60)
    print('SIMULACION DE LOGIN')
    print('='*60)
    
    email = 'admin@ddx.com'
    password = 'Admin123!'
    
    async with AsyncSessionLocal() as session:
        # Buscar usuario
        result = await session.execute(
            select(Usuario).where(Usuario.email == email)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            print(f'[FALLO] Usuario {email} no encontrado')
            return False
        
        print(f'[1] Usuario encontrado: {user.email}')
        
        # Verificar password
        try:
            is_valid = verify_password(password, user.password_hash)
            print(f'[2] Password valido: {is_valid}')
            
            if not is_valid:
                print('[FALLO] Password incorrecto')
                return False
        except Exception as e:
            print(f'[ERROR] Error al verificar password: {e}')
            return False
        
        # Verificar activo
        if not user.activo:
            print('[FALLO] Usuario inactivo')
            return False
        
        print(f'[3] Usuario activo: {user.activo}')
        
        # Crear token
        from app.core.security import create_access_token
        token = create_access_token(data={"sub": str(user.id)})
        print(f'[4] Token creado: {token[:50]}...')
        
        print('\n[EXITO] Login completado correctamente')
        return True


async def main():
    """Ejecutar todas las pruebas"""
    
    try:
        await test_password()
        success = await simulate_login()
        
        print('\n' + '='*60)
        if success:
            print('[RESULTADO] El sistema de login funciona correctamente')
            print('='*60)
            print('\nSi aun no puedes hacer login desde el frontend, verifica:')
            print('1. El backend esta corriendo (http://localhost:8000)')
            print('2. El frontend esta corriendo (http://localhost:3000)')
            print('3. CORS esta configurado correctamente en backend/.env')
            print('4. Usa las credenciales exactas:')
            print('   Email: admin@ddx.com')
            print('   Password: Admin123!')
        else:
            print('[RESULTADO] HAY PROBLEMAS con el login')
            print('='*60)
            print('\nPosibles soluciones:')
            print('1. Reinstalar bcrypt: pip uninstall bcrypt -y && pip install bcrypt==4.1.2')
            print('2. Recrear usuario admin: python crear_admin.py')
        print('='*60)
        
    except Exception as e:
        print(f'\n[ERROR CRITICO] {e}')
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
