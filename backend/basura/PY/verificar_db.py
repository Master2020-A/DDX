"""
Script para verificar la conexion a la base de datos y el estado de las tablas
Ejecutar: python verificar_db.py
"""
import asyncio
from sqlalchemy import text
from app.core.database import AsyncSessionLocal, engine


async def verificar_conexion():
    """Verificar conexion a PostgreSQL"""
    
    print('='*60)
    print('VERIFICANDO CONEXION A BASE DE DATOS')
    print('='*60)
    
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(text("SELECT version();"))
            version = result.scalar()
            print('[OK] Conexion exitosa a PostgreSQL')
            print(f'Version: {version}')
            return True
    except Exception as e:
        print(f'[ERROR] No se pudo conectar: {e}')
        return False


async def verificar_tablas():
    """Verificar que las tablas existan"""
    
    print('\n' + '='*60)
    print('VERIFICANDO TABLAS')
    print('='*60)
    
    tablas_esperadas = [
        'usuarios',
        'pacientes',
        'consultas',
        'expedientes_clinicos',
        'diagnosticos',
        'pruebas_medicas',
        'resultados_pruebas',
        'tratamientos',
        'prescripciones',
        'interconsultas',
        'seguimientos',
        'hospitalizaciones',
        'notas_medicas',
        'archivos_medicos',
        'auditoria'
    ]
    
    try:
        async with AsyncSessionLocal() as session:
            for tabla in tablas_esperadas:
                try:
                    result = await session.execute(
                        text(f"SELECT COUNT(*) FROM {tabla};")
                    )
                    count = result.scalar()
                    print(f'[OK] {tabla:25} - {count} registros')
                except Exception:
                    print(f'[ERROR] {tabla:25} - No existe')
        
        print('='*60)
        return True
        
    except Exception as e:
        print(f'[ERROR] Error al verificar tablas: {e}')
        return False


async def verificar_usuarios():
    """Verificar usuarios registrados"""
    
    print('\n' + '='*60)
    print('USUARIOS REGISTRADOS')
    print('='*60)
    
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                text("SELECT email, nombre_completo, rol, activo FROM usuarios;")
            )
            usuarios = result.fetchall()
            
            if not usuarios:
                print('[INFO] No hay usuarios registrados')
                print('\nEjecuta: python crear_admin.py')
            else:
                for usuario in usuarios:
                    email, nombre, rol, activo = usuario
                    estado = 'Activo' if activo else 'Inactivo'
                    print(f'\n- {nombre}')
                    print(f'  Email: {email}')
                    print(f'  Rol: {rol}')
                    print(f'  Estado: {estado}')
            
            print('='*60)
            return True
            
    except Exception as e:
        print(f'[ERROR] Error al verificar usuarios: {e}')
        return False


async def verificar_configuracion():
    """Verificar archivo de configuracion"""
    
    print('\n' + '='*60)
    print('VERIFICANDO CONFIGURACION')
    print('='*60)
    
    try:
        from app.core.config import settings
        
        print(f'[OK] Archivo .env encontrado')
        print(f'\nConfiguracion actual:')
        print(f'  APP_NAME: {settings.APP_NAME}')
        print(f'  DEBUG: {settings.DEBUG}')
        print(f'  DATABASE_URL: {settings.DATABASE_URL[:50]}...')
        print(f'  ALLOWED_ORIGINS: {settings.ALLOWED_ORIGINS}')
        print('='*60)
        return True
        
    except Exception as e:
        print(f'[ERROR] Error al leer configuracion: {e}')
        print('\nVerifica que el archivo .env exista en backend/')
        return False


async def main():
    """Ejecutar todas las verificaciones"""
    
    print('\n' + '='*60)
    print('SISTEMA DDX - VERIFICACION DE INSTALACION')
    print('='*60)
    
    # Verificar configuracion
    config_ok = await verificar_configuracion()
    if not config_ok:
        print('\n[ERROR] Configuracion invalida')
        return
    
    # Verificar conexion
    conexion_ok = await verificar_conexion()
    if not conexion_ok:
        print('\n[ERROR] No se pudo conectar a la base de datos')
        print('\nVerifica que:')
        print('1. PostgreSQL este corriendo')
        print('2. La base de datos ddx_db exista')
        print('3. El DATABASE_URL en .env sea correcto')
        return
    
    # Verificar tablas
    tablas_ok = await verificar_tablas()
    if not tablas_ok:
        print('\n[ERROR] Faltan tablas en la base de datos')
        print('\nEjecuta: psql -U postgres -d ddx_db -f database\\schema.sql')
        return
    
    # Verificar usuarios
    await verificar_usuarios()
    
    print('\n' + '='*60)
    print('[OK] VERIFICACION COMPLETADA')
    print('='*60)
    print('\nSistema listo para usar!')
    print('\nPara iniciar:')
    print('1. Backend:  uvicorn app.main:app --reload')
    print('2. Frontend: cd ../frontend && npm run dev')
    print('='*60)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('\n\n[INFO] Verificacion cancelada')
    except Exception as e:
        print(f'\n[ERROR] Error inesperado: {e}')
