#!/usr/bin/env python3
"""
Verificar qué URLs se guardaron en la BD para el archivo más reciente
"""
import sys
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import get_db
from sqlalchemy import text
import json

async def check_latest():
    async for db in get_db():
        try:
            query = text("""
                SELECT 
                    id,
                    nombre_archivo,
                    resultados_ia::text
                FROM imagenes_medicas
                WHERE nombre_archivo LIKE '%aorta%'
                ORDER BY created_at DESC
                LIMIT 1
            """)
            
            result = await db.execute(query)
            row = result.fetchone()
            
            if row:
                print("="*80)
                print(f"Archivo: {row.nombre_archivo}")
                print(f"ID: {row.id}")
                print("\nResultados IA:")
                
                if row.resultados_ia:
                    resultados = json.loads(row.resultados_ia)
                    print(json.dumps(resultados, indent=2))
                else:
                    print("  (ninguno)")
                
                print("="*80)
            else:
                print("No se encontró el archivo")
                
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            break

if __name__ == "__main__":
    asyncio.run(check_latest())
