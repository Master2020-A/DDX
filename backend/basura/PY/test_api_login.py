"""
Script para probar el endpoint de login directamente
Ejecutar: python test_api_login.py
NOTA: El backend debe estar corriendo en http://localhost:8000
"""
import requests
import json


def test_login_endpoint():
    """Probar el endpoint POST /api/auth/login"""
    
    print('='*60)
    print('TEST DEL ENDPOINT DE LOGIN')
    print('='*60)
    
    url = 'http://localhost:8000/api/auth/login'
    
    credentials = {
        'email': 'admin@ddx.com',
        'password': 'Admin123!'
    }
    
    print(f'\n[1] URL: {url}')
    print(f'[2] Credenciales: {credentials["email"]}')
    print(f'[3] Enviando peticion...\n')
    
    try:
        response = requests.post(url, json=credentials, timeout=10)
        
        print(f'Status Code: {response.status_code}')
        print(f'Headers: {dict(response.headers)}')
        print(f'\nRespuesta:')
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        
        if response.status_code == 200:
            print('\n' + '='*60)
            print('[EXITO] Login correcto!')
            print('='*60)
            data = response.json()
            print(f'\nToken: {data.get("access_token", "")[:50]}...')
            print(f'Usuario: {data.get("user", {}).get("email")}')
            return True
        else:
            print('\n' + '='*60)
            print('[FALLO] Login incorrecto')
            print('='*60)
            return False
            
    except requests.exceptions.ConnectionError:
        print('\n[ERROR] No se pudo conectar al backend')
        print('Asegurate de que el backend este corriendo:')
        print('  cd backend')
        print('  call ddx\\Scripts\\activate.bat')
        print('  uvicorn app.main:app --reload')
        return False
        
    except Exception as e:
        print(f'\n[ERROR] {e}')
        return False


def test_register_and_login():
    """Probar registro y login de un nuevo usuario"""
    
    print('\n\n' + '='*60)
    print('TEST DE REGISTRO Y LOGIN')
    print('='*60)
    
    base_url = 'http://localhost:8000/api/auth'
    
    # Datos del nuevo usuario
    new_user = {
        'email': 'test@test.com',
        'password': 'Test123!',
        'nombre_completo': 'Usuario de Prueba',
        'rol': 'medico'
    }
    
    # 1. Intentar registrar
    print('\n[1] Registrando usuario de prueba...')
    try:
        response = requests.post(f'{base_url}/register', json=new_user, timeout=10)
        print(f'Status: {response.status_code}')
        
        if response.status_code == 201:
            print('[OK] Usuario creado')
        elif response.status_code == 400:
            print('[INFO] Usuario ya existe (esperado si ya se ejecuto antes)')
        else:
            print(f'[ERROR] {response.json()}')
    except Exception as e:
        print(f'[ERROR] {e}')
    
    # 2. Intentar login
    print('\n[2] Haciendo login con usuario de prueba...')
    login_data = {
        'email': new_user['email'],
        'password': new_user['password']
    }
    
    try:
        response = requests.post(f'{base_url}/login', json=login_data, timeout=10)
        print(f'Status: {response.status_code}')
        
        if response.status_code == 200:
            print('[EXITO] Login correcto con usuario de prueba')
            return True
        else:
            print(f'[FALLO] {response.json()}')
            return False
            
    except Exception as e:
        print(f'[ERROR] {e}')
        return False


if __name__ == "__main__":
    print('Asegurate de que el backend este corriendo en http://localhost:8000\n')
    input('Presiona Enter para continuar...')
    
    # Test 1: Login con admin
    success1 = test_login_endpoint()
    
    # Test 2: Registro y login
    success2 = test_register_and_login()
    
    print('\n\n' + '='*60)
    print('RESUMEN')
    print('='*60)
    print(f'Login admin: {"OK" if success1 else "FALLO"}')
    print(f'Registro y login: {"OK" if success2 else "FALLO"}')
    print('='*60)
    
    if success1 and success2:
        print('\n[RESULTADO] El backend funciona correctamente')
        print('Si no puedes hacer login desde el frontend, revisa:')
        print('1. URL del backend en frontend (http://localhost:8000)')
        print('2. CORS configurado en .env: ALLOWED_ORIGINS=http://localhost:3000')
        print('3. Consola del navegador (F12) para ver errores')
    else:
        print('\n[RESULTADO] Hay problemas con el backend')
        print('Ejecuta: python test_login.py')
    
    print('\n')
