"""Agregar columnas faltantes a interconsultas"""
import asyncio
from sqlalchemy import text
from app.core.database import AsyncSessionLocal

async def main():
    print("\n🔧 Agregando columnas faltantes a interconsultas...")
    
    columnas_agregar = [
        ("paciente_id", "UUID REFERENCES pacientes(id) ON DELETE CASCADE"),
        ("hospitalizacion_id", "UUID REFERENCES hospitalizaciones(id) ON DELETE SET NULL"),
        ("motivo_solicitud", "TEXT"),
        ("antecedentes_relevantes", "TEXT"),
        ("estudios_adjuntos", "VARCHAR[]"),
        ("fecha_aceptacion", "TIMESTAMP WITH TIME ZONE"),
        ("fecha_completada", "TIMESTAMP WITH TIME ZONE"),
        ("hallazgos", "TEXT"),
        ("plan_tratamiento", "TEXT"),
        ("requiere_seguimiento", "BOOLEAN DEFAULT FALSE"),
        ("fecha_seguimiento", "TIMESTAMP WITH TIME ZONE"),
        ("motivo_rechazo", "TEXT"),
        ("prioridad_clinica", "INTEGER DEFAULT 1"),
        ("notas_internas", "TEXT")
    ]
    
    async with AsyncSessionLocal() as db:
        for nombre, tipo in columnas_agregar:
            try:
                print(f"  Agregando {nombre}...", end=" ")
                await db.execute(text(f"ALTER TABLE interconsultas ADD COLUMN IF NOT EXISTS {nombre} {tipo}"))
                await db.commit()
                print("✓")
            except Exception as e:
                print(f"✗ ({str(e)[:50]})")
                await db.rollback()
        
        print("\n✅ Proceso completado!")
        
        # Verificar columnas finales
        result = await db.execute(text("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = 'interconsultas'
            ORDER BY ordinal_position
        """))
        columnas = [r[0] for r in result.fetchall()]
        print(f"\n📋 Total de columnas ahora: {len(columnas)}")

asyncio.run(main())
