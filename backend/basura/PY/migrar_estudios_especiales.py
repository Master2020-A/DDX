"""
Script de migración para actualizar campos de estudios especiales
Cambia interpretacion_medica a nullable y recomendaciones a ARRAY
"""
import asyncio
from sqlalchemy import text
from app.core.database import engine

async def migrar_estudios_especiales():
    """Migrar campos de estudios especiales"""
    
    async with engine.begin() as conn:
        print("🔄 Iniciando migración de estudios especiales...")
        
        try:
            # EKG - Cambiar interpretacion_medica a nullable
            print("  📋 Migrando EstudioEKG...")
            await conn.execute(text("""
                ALTER TABLE estudios_ekg 
                ALTER COLUMN interpretacion_medica DROP NOT NULL;
            """))
            
            # EKG - Cambiar recomendaciones de Text a ARRAY
            await conn.execute(text("""
                ALTER TABLE estudios_ekg 
                ALTER COLUMN recomendaciones TYPE text[] USING 
                CASE 
                    WHEN recomendaciones IS NULL THEN NULL
                    WHEN recomendaciones = '' THEN NULL
                    ELSE ARRAY[recomendaciones]::text[]
                END;
            """))
            print("  ✅ EstudioEKG migrado")
            
            # EEG - Cambiar interpretacion_medica a nullable
            print("  📋 Migrando EstudioEEG...")
            await conn.execute(text("""
                ALTER TABLE estudios_eeg 
                ALTER COLUMN interpretacion_medica DROP NOT NULL;
            """))
            
            # EEG - Cambiar recomendaciones de Text a ARRAY
            await conn.execute(text("""
                ALTER TABLE estudios_eeg 
                ALTER COLUMN recomendaciones TYPE text[] USING 
                CASE 
                    WHEN recomendaciones IS NULL THEN NULL
                    WHEN recomendaciones = '' THEN NULL
                    ELSE ARRAY[recomendaciones]::text[]
                END;
            """))
            print("  ✅ EstudioEEG migrado")
            
            # Ecografía - Cambiar interpretacion_medica a nullable
            print("  📋 Migrando Ecografia...")
            await conn.execute(text("""
                ALTER TABLE ecografias 
                ALTER COLUMN interpretacion_medica DROP NOT NULL;
            """))
            
            # Ecografía - Cambiar recomendaciones de Text a ARRAY
            await conn.execute(text("""
                ALTER TABLE ecografias 
                ALTER COLUMN recomendaciones TYPE text[] USING 
                CASE 
                    WHEN recomendaciones IS NULL THEN NULL
                    WHEN recomendaciones = '' THEN NULL
                    ELSE ARRAY[recomendaciones]::text[]
                END;
            """))
            print("  ✅ Ecografia migrada")
            
            print("\n✅ Migración completada exitosamente!")
            print("\n📝 Cambios realizados:")
            print("  - interpretacion_medica ahora es nullable en EKG, EEG y Ecografías")
            print("  - recomendaciones ahora es ARRAY[String] en EKG, EEG y Ecografías")
            print("\n⚠️  IMPORTANTE: Reinicia el servidor backend para aplicar los cambios")
            
        except Exception as e:
            print(f"\n❌ Error durante la migración: {str(e)}")
            print("\n💡 Posibles causas:")
            print("  1. Las tablas ya fueron migradas")
            print("  2. Hay datos incompatibles en la base de datos")
            print("  3. No tienes permisos suficientes")
            raise

if __name__ == "__main__":
    print("=" * 60)
    print("MIGRACIÓN DE ESTUDIOS ESPECIALES")
    print("=" * 60)
    print()
    
    asyncio.run(migrar_estudios_especiales())
