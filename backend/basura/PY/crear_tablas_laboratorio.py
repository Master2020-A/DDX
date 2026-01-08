"""
Script para crear tablas de laboratorio en la base de datos
"""
import sys
import asyncio
from pathlib import Path

# Agregar el directorio backend al path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy.ext.asyncio import create_async_engine
from app.core.config import settings
from app.core.database import Base

# Importar modelos para que se registren
from app.models.laboratorio import PruebaLaboratorio, RangoReferencia
from app.models.paciente import Paciente
from app.models.consulta import Consulta


async def crear_tablas():
    """Crea las tablas de laboratorio en la base de datos"""
    print("="*80)
    print("🔬 CREACIÓN DE TABLAS DE LABORATORIO")
    print("="*80)
    print()
    
    print(f"📊 Base de datos: {settings.DATABASE_URL}")
    print()
    
    # Crear engine
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    
    try:
        print("🔧 Creando tablas...")
        print()
        
        async with engine.begin() as conn:
            # Crear solo las tablas de laboratorio
            await conn.run_sync(Base.metadata.create_all)
        
        print()
        print("="*80)
        print("✅ TABLAS CREADAS CORRECTAMENTE")
        print("="*80)
        print()
        print("📋 Tablas creadas:")
        print("  • pruebas_laboratorio")
        print("  • rangos_referencia")
        print()
        print("🚀 Próximo paso:")
        print("  Ejecuta: python inicializar_rangos_laboratorio.py")
        print()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        raise
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(crear_tablas())
