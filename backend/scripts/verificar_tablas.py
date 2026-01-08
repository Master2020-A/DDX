"""
Script para verificar tablas en la base de datos
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from app.core.database import async_session_maker

async def main():
    print("\n🔍 Verificando tablas en la base de datos...\n")
    
    async with async_session_maker() as db:
        # Listar todas las tablas
        result = await db.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """))
        
        tablas = result.fetchall()
        
        print(f"📊 Total de tablas encontradas: {len(tablas)}\n")
        
        tablas_hospitalizacion = ['camas', 'hospitalizaciones', 'notas_evolucion', 'indicaciones_medicas', 'notas_alta']
        tablas_interconsultas = ['interconsultas', 'notificaciones_interconsulta', 'mensajes_interconsulta', 'seguimientos_interconsulta']
        
        print("✅ Tablas existentes:")
        for tabla in tablas:
            print(f"   • {tabla[0]}")
        
        print("\n🏥 Verificando tablas de Hospitalización:")
        for tabla in tablas_hospitalizacion:
            existe = any(t[0] == tabla for t in tablas)
            print(f"   {'✅' if existe else '❌'} {tabla}")
        
        print("\n🔄 Verificando tablas de Interconsultas:")
        for tabla in tablas_interconsultas:
            existe = any(t[0] == tabla for t in tablas)
            print(f"   {'✅' if existe else '❌'} {tabla}")
        
        # Verificar versión de Alembic
        try:
            result = await db.execute(text("SELECT version_num FROM alembic_version"))
            version = result.scalar()
            print(f"\n📌 Versión actual de Alembic: {version}")
        except:
            print("\n⚠️  Tabla alembic_version no encontrada")

if __name__ == "__main__":
    asyncio.run(main())
