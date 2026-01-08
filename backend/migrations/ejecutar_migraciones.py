"""
Script para ejecutar migraciones SQL en orden
"""
import asyncio
import os
import sys
from pathlib import Path

# Agregar el directorio backend al path para poder importar app
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import text
from app.core.database import AsyncSessionLocal


# Tabla para rastrear migraciones ejecutadas
CREATE_MIGRATIONS_TABLE = """
CREATE TABLE IF NOT EXISTS schema_migrations (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255) UNIQUE NOT NULL,
    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""


async def ejecutar_migracion(db, filepath: Path):
    """Ejecutar un archivo SQL de migración"""
    filename = filepath.name
    
    # Verificar si ya fue ejecutada
    result = await db.execute(
        text("SELECT filename FROM schema_migrations WHERE filename = :filename"),
        {"filename": filename}
    )
    if result.scalar_one_or_none():
        print(f"⏭️  {filename} - Ya ejecutada (omitiendo)")
        return False
    
    # Leer el archivo SQL
    print(f"📄 Ejecutando: {filename}")
    with open(filepath, 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    try:
        # Dividir el SQL en comandos individuales
        # Dividir por punto y coma, pero ignorar los que están en comentarios
        comandos = []
        sql_temp = ""
        
        for linea in sql_content.split('\n'):
            # Ignorar líneas de comentarios
            if linea.strip().startswith('--'):
                continue
            
            sql_temp += linea + '\n'
            
            # Si la línea termina con punto y coma, es el final de un comando
            if linea.strip().endswith(';'):
                comando = sql_temp.strip()
                if comando:
                    comandos.append(comando)
                sql_temp = ""
        
        # Agregar el último comando si existe
        if sql_temp.strip():
            comandos.append(sql_temp.strip())
        
        # Ejecutar cada comando individualmente
        for i, comando in enumerate(comandos, 1):
            if comando.strip():
                try:
                    await db.execute(text(comando))
                except Exception as e:
                    print(f"   ❌ Error en comando {i}: {str(e)[:100]}")
                    raise
        
        # Registrar como ejecutada
        await db.execute(
            text("INSERT INTO schema_migrations (filename) VALUES (:filename)"),
            {"filename": filename}
        )
        await db.commit()
        
        print(f"✅ {filename} - Ejecutada exitosamente ({len(comandos)} comandos)")
        return True
        
    except Exception as e:
        await db.rollback()
        print(f"❌ {filename} - ERROR: {e}")
        raise


async def ejecutar_todas_migraciones():
    """Ejecutar todas las migraciones SQL pendientes"""
    print("="*70)
    print("EJECUTANDO MIGRACIONES SQL")
    print("="*70)
    print()
    
    migrations_dir = Path(__file__).parent
    
    async with AsyncSessionLocal() as db:
        try:
            # Crear tabla de migraciones si no existe
            await db.execute(text(CREATE_MIGRATIONS_TABLE))
            await db.commit()
            
            # Obtener todos los archivos .sql
            sql_files = sorted(migrations_dir.glob("*.sql"))
            
            if not sql_files:
                print("⚠️  No se encontraron archivos de migración (.sql)")
                return
            
            print(f"📋 Encontrados {len(sql_files)} archivos de migración\n")
            
            ejecutadas = 0
            omitidas = 0
            
            for sql_file in sql_files:
                try:
                    if await ejecutar_migracion(db, sql_file):
                        ejecutadas += 1
                    else:
                        omitidas += 1
                except Exception as e:
                    print(f"\n❌ ERROR CRÍTICO ejecutando {sql_file.name}")
                    print(f"   {e}")
                    print("\n⚠️  Las migraciones restantes no se ejecutarán")
                    return
            
            print()
            print("="*70)
            print(f"✅ COMPLETADO")
            print(f"   Ejecutadas: {ejecutadas}")
            print(f"   Omitidas: {omitidas} (ya ejecutadas anteriormente)")
            print("="*70)
            
        except Exception as e:
            print(f"\n❌ ERROR FATAL: {e}")
            await db.rollback()
            raise


if __name__ == "__main__":
    try:
        asyncio.run(ejecutar_todas_migraciones())
    except KeyboardInterrupt:
        print("\n\n⚠️  Operación cancelada por el usuario")
    except Exception as e:
        print(f"\n❌ ERROR CRÍTICO: {e}")
        import traceback
        traceback.print_exc()
