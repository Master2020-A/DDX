"""Script final para setup con output a archivo"""
import asyncio
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

# Redirigir output a archivo
log_file = Path(__file__).parent.parent / "setup_log.txt"
original_stdout = sys.stdout
sys.stdout = open(log_file, 'w', encoding='utf-8')

try:
    print(f"=== SETUP INICIADO: {datetime.now()} ===\n")
    
    # Importar después de configurar stdout
    from sqlalchemy import select, func, text
    from app.core.database import AsyncSessionLocal, engine, Base
    from app.models import hospitalizacion, interconsulta
    from app.models.hospitalizacion import Cama, Hospitalizacion
    from app.models.interconsulta import Interconsulta
    from app.models.paciente import Paciente
    from app.models.usuario import Usuario
    
    async def setup():
        print("1. Creando tablas...")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("✅ Tablas creadas\n")
        
        print("2. Verificando datos existentes...")
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(func.count(Cama.id)))
            camas_count = result.scalar()
            print(f"   Camas existentes: {camas_count}")
            
            if camas_count > 0:
                print("⚠️  Ya existen datos. Saltando población.\n")
                return
        
        print("\n3. Poblando datos de prueba...")
        from scripts.poblar_hospitalizacion_interconsultas import main as poblar
        await poblar()
        
        print("\n4. Verificación final...")
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(func.count(Cama.id)))
            print(f"   Camas: {result.scalar()}")
            
            result = await db.execute(select(func.count(Hospitalizacion.id)))
            print(f"   Hospitalizaciones: {result.scalar()}")
            
            result = await db.execute(select(func.count(Interconsulta.id)))
            print(f"   Interconsultas: {result.scalar()}")
        
        print(f"\n=== SETUP COMPLETADO: {datetime.now()} ===")
    
    asyncio.run(setup())
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
finally:
    sys.stdout.close()
    sys.stdout = original_stdout
    print(f"\n✅ Log guardado en: {log_file}")
    print("Lee el archivo setup_log.txt para ver los detalles")
