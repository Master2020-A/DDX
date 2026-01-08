"""
Script de diagnostico completo para identificar problemas de conexion
Ejecutar: python diagnosticar.py
"""
import asyncio
import os
import sys


def verificar_archivo_env():
    """Verificar que el archivo .env exista"""
    print('='*60)
    print('1. VERIFICANDO ARCHIVO .ENV')
    print('='*60)
    
    if not os.path.exists('.env'):
        print('[ERROR] Archivo .env NO encontrado')
        print('\nCrea el archivo .env en backend/ con este contenido:')
        print('-'*60)
        print('DATABASE_URL=postgresql+asyncpg://postgres:tu_password@localhost:5432/ddx_db')
        print('SECRET_KEY=cambiar-por-clave-segura')
        print('ALGORITHM=HS256')
        print('ACCESS_TOKEN_EXPIRE_MINUTES=30')
        print('DEBUG=True')
        print('ALLOWED_ORIGINS=http://localhost:3000')
        print('-'*60)
        return False
    
    print('[OK] Archivo .env encontrado')
    
    # Leer y verificar contenido
    with open('.env', 'r') as f:
        content = f.read()
        
    if 'DATABASE_URL' not in content:
        print('[ERROR] Falta DATABASE_URL en .env')
        return False
    
    print('[OK] DATABASE_URL encontrado en .env')
    
    # Extraer DATABASE_URL sin mostrar password completo
    for line in content.split('\n'):
        if line.startswith('DATABASE_URL'):
            # Ocultar password
            url = line.split('=')[1]
            if '@' in url:
                parts = url.split('@')
                user_pass = parts[0].split('//')[-1]
                host_db = parts[1]
                user = user_pass.split(':')[0] if ':' in user_pass else user_pass
                print(f'Usuario DB: {user}')
                print(f'Host: {host_db}')
    
    return True


def verificar_postgresql_corriendo():
    """Verificar que PostgreSQL este corriendo"""
    print('\n' + '='*60)
    print('2. VERIFICANDO POSTGRESQL')
    print('='*60)
    
    import subprocess
    
    try:
        # Intentar conectar con psql
        result = subprocess.run(
            ['psql', '--version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            print(f'[OK] PostgreSQL instalado: {result.stdout.strip()}')
        else:
            print('[ERROR] PostgreSQL no encontrado en PATH')
            return False
        
        # Verificar si el servicio esta corriendo (cualquier version)
        # Buscar servicios que contengan "postgresql"
        result = subprocess.run(
            ['sc', 'query', 'state=', 'all'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        # Buscar servicios de PostgreSQL que estén corriendo
        lines = result.stdout.lower().split('\n')
        pg_service = None
        pg_running = False
        
        for i, line in enumerate(lines):
            if 'postgresql' in line and 'service_name' in line:
                # Encontró un servicio de PostgreSQL
                pg_service = line.split(':')[-1].strip()
                # Buscar el estado en las siguientes líneas
                for j in range(i, min(i+10, len(lines))):
                    if 'running' in lines[j]:
                        pg_running = True
                        break
                break
        
        if pg_running:
            print(f'[OK] Servicio PostgreSQL esta corriendo ({pg_service})')
            return True
        elif pg_service:
            print(f'[ERROR] Servicio PostgreSQL encontrado pero NO esta corriendo: {pg_service}')
            print(f'\nPara iniciar el servicio:')
            print(f'  net start {pg_service}')
            print('\nO desde Servicios de Windows (services.msc)')
            return False
        else:
            # Intentar conectar directamente como fallback
            print('[INFO] No se pudo verificar servicio, intentando conexion directa...')
            return True  # Continuar con la prueba de conexión
            
    except Exception as e:
        print(f'[ERROR] No se pudo verificar PostgreSQL: {e}')
        return False


async def verificar_conexion_db():
    """Intentar conectar a la base de datos"""
    print('\n' + '='*60)
    print('3. VERIFICANDO CONEXION A BASE DE DATOS')
    print('='*60)
    
    try:
        from app.core.config import settings
        print(f'[OK] Configuracion cargada desde .env')
        
        # Mostrar DATABASE_URL ofuscado
        db_url = settings.DATABASE_URL
        if '@' in db_url:
            parts = db_url.split('@')
            print(f'[INFO] Conectando a: ...@{parts[1]}')
        
    except Exception as e:
        print(f'[ERROR] No se pudo cargar configuracion: {e}')
        return False
    
    try:
        from app.core.database import engine
        from sqlalchemy import text
        
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            result.scalar()
        
        print('[OK] Conexion exitosa a PostgreSQL')
        return True
        
    except Exception as e:
        error_msg = str(e)
        print(f'[ERROR] No se pudo conectar: {error_msg}')
        
        if 'password authentication failed' in error_msg:
            print('\n[PROBLEMA] Password incorrecto en DATABASE_URL')
            print('Edita backend/.env y corrige el password')
            
        elif 'database "ddx_db" does not exist' in error_msg:
            print('\n[PROBLEMA] La base de datos ddx_db no existe')
            print('Ejecuta: psql -U postgres -c "CREATE DATABASE ddx_db;"')
            
        elif 'could not connect to server' in error_msg:
            print('\n[PROBLEMA] PostgreSQL no esta corriendo')
            print('Ejecuta: net start postgresql-x64-15')
            
        elif 'Connection refused' in error_msg:
            print('\n[PROBLEMA] PostgreSQL rechaza conexiones')
            print('Verifica que PostgreSQL este corriendo en el puerto 5432')
        
        return False


async def verificar_tablas():
    """Verificar que las tablas existan"""
    print('\n' + '='*60)
    print('4. VERIFICANDO TABLAS')
    print('='*60)
    
    try:
        from app.core.database import AsyncSessionLocal
        from sqlalchemy import text
        
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                text("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public'")
            )
            count = result.scalar()
            
            if count == 0:
                print('[ERROR] No hay tablas en la base de datos')
                print('\nEjecuta: psql -U postgres -d ddx_db -f database\\schema.sql')
                return False
            
            print(f'[OK] {count} tablas encontradas')
            
            # Verificar tabla usuarios
            result = await session.execute(
                text("SELECT COUNT(*) FROM usuarios")
            )
            usuarios = result.scalar()
            print(f'[INFO] {usuarios} usuarios registrados')
            
            return True
            
    except Exception as e:
        error_msg = str(e)
        
        if 'relation "usuarios" does not exist' in error_msg:
            print('[ERROR] Tabla "usuarios" no existe')
            print('\nEjecuta: psql -U postgres -d ddx_db -f database\\schema.sql')
        else:
            print(f'[ERROR] Error al verificar tablas: {error_msg}')
        
        return False


async def main():
    """Ejecutar diagnostico completo"""
    
    print('\n' + '='*60)
    print('DIAGNOSTICO COMPLETO - Sistema DDX')
    print('='*60)
    
    # 1. Verificar .env
    env_ok = verificar_archivo_env()
    if not env_ok:
        print('\n[RESULTADO] Crea el archivo .env primero')
        return
    
    # 2. Verificar PostgreSQL
    pg_ok = verificar_postgresql_corriendo()
    if not pg_ok:
        print('\n[RESULTADO] Inicia PostgreSQL primero')
        return
    
    # 3. Verificar conexion
    conn_ok = await verificar_conexion_db()
    if not conn_ok:
        print('\n[RESULTADO] Soluciona el problema de conexion')
        return
    
    # 4. Verificar tablas
    tablas_ok = await verificar_tablas()
    if not tablas_ok:
        print('\n[RESULTADO] Crea las tablas ejecutando schema.sql')
        return
    
    print('\n' + '='*60)
    print('[OK] DIAGNOSTICO COMPLETADO - TODO CORRECTO')
    print('='*60)
    print('\nAhora puedes:')
    print('1. Crear admin: python crear_admin.py')
    print('2. Crear usuarios: python crear_usuario.py')
    print('='*60)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('\n\n[INFO] Diagnostico cancelado')
    except Exception as e:
        print(f'\n[ERROR] Error inesperado: {e}')
        import traceback
        traceback.print_exc()
