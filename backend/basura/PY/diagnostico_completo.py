"""
Diagnóstico completo del sistema de login
"""
import asyncio
import requests
from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.usuario import Usuario
from app.core.security import verify_password


async def diagnostico():
    print('\n' + '='*70)
    print('🔍 DIAGNÓSTICO COMPLETO DEL SISTEMA DE LOGIN')
    print('='*70)
    
    # 1. Verificar base de datos
    print('\n[1] Verificando base de datos...')
    async with AsyncSessionLocal() as session:
        try:
            result = await session.execute(select(Usuario))
            usuarios = result.scalars().all()
            
            if not usuarios:
                print('❌ NO HAY USUARIOS en la base de datos')
                print('\n💡 SOLUCIÓN: Ejecuta uno de estos comandos:')
                print('   python crear_admin.py')
                print('   python crear_master_user.py')
                return False
            
            print(f'✅ Hay {len(usuarios)} usuario(s) en la base de datos:\n')
            
            for u in usuarios:
                print(f'   📧 {u.email}')
                print(f'      Nombre: {u.nombre_completo}')
                print(f'      Rol: {u.rol}')
                print(f'      Activo: {"✅" if u.activo else "❌"}')
                
                # Verificar password
                passwords_test = ['Admin123!', 'Master123!', 'admin123']
                for pwd in passwords_test:
                    if verify_password(pwd, u.password_hash):
                        print(f'      🔑 Password válido: {pwd}')
                        break
                print()
            
        except Exception as e:
            print(f'❌ Error conectando a DB: {e}')
            return False
    
    # 2. Verificar backend
    print('[2] Verificando backend (http://localhost:8612)...')
    try:
        r = requests.get('http://localhost:8612/', timeout=3)
        print(f'✅ Backend respondiendo (status {r.status_code})')
    except Exception as e:
        print(f'❌ Backend NO responde: {e}')
        print('\n💡 SOLUCIÓN: Inicia el backend con:')
        print('   uvicorn app.main:app --reload --port=8612')
        return False
    
    # 3. Probar login endpoint
    print('\n[3] Probando endpoint de login...')
    
    # Probar con cada usuario encontrado
    test_credentials = [
        ('admin@ddx.com', 'Admin123!'),
        ('master@master.com', 'Master123!'),
    ]
    
    for email, password in test_credentials:
        try:
            r = requests.post('http://localhost:8612/api/auth/login',
                            json={'email': email, 'password': password},
                            timeout=5)
            if r.status_code == 200:
                print(f'✅ Login EXITOSO con {email}')
                print(f'   Token generado correctamente')
                print(f'\n🎉 USA ESTAS CREDENCIALES EN EL FRONTEND:')
                print(f'   📧 Email: {email}')
                print(f'   🔑 Password: {password}')
                return True
            else:
                print(f'❌ Login falló con {email}: {r.json().get("detail")}')
        except Exception as e:
            print(f'⚠️  Error probando {email}: {e}')
    
    print('\n❌ Ningún login funcionó')
    print('\n💡 SOLUCIÓN: Crea un usuario con:')
    print('   python crear_admin.py')
    return False


if __name__ == "__main__":
    print('\n🚀 Iniciando diagnóstico...')
    try:
        result = asyncio.run(diagnostico())
        
        print('\n' + '='*70)
        if result:
            print('✅ SISTEMA FUNCIONANDO CORRECTAMENTE')
            print('\nPuedes hacer login en: http://localhost:3000')
        else:
            print('❌ HAY PROBLEMAS QUE RESOLVER')
            print('\nSigue las instrucciones arriba ☝️')
        print('='*70 + '\n')
        
    except Exception as e:
        print(f'\n❌ ERROR CRÍTICO: {e}')
        import traceback
        traceback.print_exc()
