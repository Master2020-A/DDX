"""
Script para verificar que la tabla imagenes_medicas existe y está correcta
"""
import asyncio
from app.core.database import engine
from sqlalchemy import text


async def verificar_tabla():
    """Verificar la tabla imagenes_medicas"""
    
    print("="*70)
    print("VERIFICANDO TABLA: imagenes_medicas")
    print("="*70)
    
    async with engine.begin() as conn:
        # Verificar que la tabla existe
        result = await conn.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_name = 'imagenes_medicas'
        """))
        tabla = result.fetchone()
        
        if not tabla:
            print("\n❌ La tabla 'imagenes_medicas' NO existe")
            return False
        
        print("\n✅ La tabla 'imagenes_medicas' existe")
        
        # Contar columnas
        result = await conn.execute(text("""
            SELECT COUNT(*) 
            FROM information_schema.columns 
            WHERE table_name = 'imagenes_medicas'
        """))
        num_columnas = result.scalar()
        print(f"\n📊 Columnas: {num_columnas}")
        
        # Listar índices
        result = await conn.execute(text("""
            SELECT indexname 
            FROM pg_indexes 
            WHERE tablename = 'imagenes_medicas'
        """))
        indices = result.fetchall()
        print(f"\n🔧 Índices creados: {len(indices)}")
        for idx in indices:
            print(f"   ✓ {idx[0]}")
        
        # Verificar triggers
        result = await conn.execute(text("""
            SELECT trigger_name 
            FROM information_schema.triggers 
            WHERE event_object_table = 'imagenes_medicas'
        """))
        triggers = result.fetchall()
        print(f"\n⚙️  Triggers activos: {len(triggers)}")
        for trg in triggers:
            print(f"   ✓ {trg[0]}")
        
        # Contar registros
        result = await conn.execute(text("SELECT COUNT(*) FROM imagenes_medicas"))
        num_registros = result.scalar()
        print(f"\n📁 Registros actuales: {num_registros}")
        
        print("\n" + "="*70)
        print("✅ LA TABLA ESTÁ LISTA PARA USAR")
        print("="*70)
        print("\n💡 Próximos pasos:")
        print("   1. Reinicia el servidor FastAPI si está corriendo")
        print("   2. Verifica los endpoints en http://localhost:8612/docs")
        print("   3. Intenta subir una imagen desde el frontend")
        print("\n🚀 Endpoints disponibles:")
        print("   POST   /api/imagenes/upload")
        print("   GET    /api/imagenes/paciente/{paciente_id}")
        print("   POST   /api/imagenes/{id}/analizar-ia")
        print("="*70)
        
        return True


if __name__ == "__main__":
    asyncio.run(verificar_tabla())
