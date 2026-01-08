"""
Script para crear tablas directamente con SQLAlchemy
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import engine, Base
from app.models import hospitalizacion, interconsulta

async def main():
    print("\n" + "="*60)
    print("🔧 CREANDO TABLAS DIRECTAMENTE")
    print("="*60 + "\n")
    
    try:
        async with engine.begin() as conn:
            print("📋 Creando tablas de Hospitalización e Interconsultas...")
            await conn.run_sync(Base.metadata.create_all)
            print("✅ Tablas creadas exitosamente!\n")
            
        print("="*60)
        print("✅ PROCESO COMPLETADO")
        print("="*60)
        print("\n💡 Ahora puedes ejecutar el script de datos:")
        print("   python -m scripts.poblar_hospitalizacion_interconsultas\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
