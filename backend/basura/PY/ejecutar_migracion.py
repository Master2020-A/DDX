"""
Script para ejecutar la migración de Historia Clínica Pediátrica
"""
import asyncio
import sys
from pathlib import Path
from app.core.database import engine


async def ejecutar_migracion():
    """Ejecutar el script SQL de migración"""
    
    print("="*70)
    print("EJECUTANDO MIGRACIÓN: Imágenes Médicas con IA")
    print("="*70)
    
    # Leer el archivo SQL
    sql_file = Path(__file__).parent / "migrations" / "013_imagenes_medicas.sql"
    
    if not sql_file.exists():
        print(f"\n❌ ERROR: No se encontró el archivo de migración")
        print(f"   Ruta esperada: {sql_file}")
        return False
    
    print(f"\n📄 Leyendo migración desde: {sql_file.name}")
    
    with open(sql_file, 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    # Ejecutar la migración usando conexión raw de asyncpg
    async with engine.begin() as conn:
        try:
            print("\n🔄 Ejecutando migración...")
            print("   ⏳ Esto puede tomar unos segundos...")
            
            # Obtener la conexión raw de asyncpg para ejecutar múltiples statements
            raw_conn = await conn.get_raw_connection()
            driver_conn = raw_conn.driver_connection
            
            # Ejecutar todo el SQL (asyncpg soporta múltiples statements)
            await driver_conn.execute(sql_content)
            
            print("\n✅ MIGRACIÓN COMPLETADA EXITOSAMENTE")
            print("="*70)
            print("\n📊 Tabla creada:")
            print("   ✓ imagenes_medicas")
            print("\n🔧 Índices creados:")
            print("   ✓ idx_imagenes_paciente")
            print("   ✓ idx_imagenes_consulta")
            print("   ✓ idx_imagenes_tipo")
            print("   ✓ idx_imagenes_region")
            print("   ✓ idx_imagenes_ia")
            print("   ✓ idx_imagenes_fecha")
            print("\n🔍 Puedes verificar en:")
            print("   http://localhost:8612/docs")
            print("\n💡 Endpoints disponibles:")
            print("   POST   /api/imagenes/upload")
            print("   GET    /api/imagenes/paciente/{paciente_id}")
            print("   GET    /api/imagenes/{id}")
            print("   GET    /api/imagenes/{id}/download")
            print("   PUT    /api/imagenes/{id}")
            print("   DELETE /api/imagenes/{id}")
            print("   POST   /api/imagenes/{id}/analizar-ia")
            print("   GET    /api/imagenes/estadisticas/general")
            print("\n🤖 Características de IA:")
            print("   ✓ CheXNet (Rayos X de tórax - 14 patologías)")
            print("   ✓ MONAI (CT, MRI, US - Segmentación y clasificación)")
            print("="*70)
            
            return True
            
        except Exception as e:
            print(f"\n❌ ERROR AL EJECUTAR MIGRACIÓN:")
            print(f"   {str(e)}")
            print("\n💡 Posibles soluciones:")
            print("   1. Verifica que PostgreSQL esté corriendo")
            print("   2. Verifica la configuración en .env")
            print("   3. Verifica que la tabla 'pacientes' exista")
            print("\n📝 Detalle técnico:")
            import traceback
            traceback.print_exc()
            return False


if __name__ == "__main__":
    try:
        resultado = asyncio.run(ejecutar_migracion())
        sys.exit(0 if resultado else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Migración cancelada por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR CRÍTICO: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
