#!/usr/bin/env python3
"""
Verificar TODAS las imágenes en la base de datos
"""
import sys
import asyncio
from pathlib import Path
import json

sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import get_db
from sqlalchemy import text

async def check_all():
    async for db in get_db():
        try:
            query = text("""
                SELECT 
                    id,
                    nombre_archivo,
                    tipo_archivo,
                    resultados_ia::text,
                    created_at
                FROM imagenes_medicas
                ORDER BY created_at DESC
                LIMIT 10
            """)
            
            result = await db.execute(query)
            rows = result.fetchall()
            
            print("="*80)
            print(f"📋 ÚLTIMAS {len(rows)} IMÁGENES EN LA BASE DE DATOS")
            print("="*80)
            print()
            
            for i, row in enumerate(rows, 1):
                print(f"{i}. {row.nombre_archivo}")
                print(f"   Tipo: {row.tipo_archivo}")
                print(f"   Fecha: {row.created_at}")
                print(f"   ID: {row.id}")
                
                if row.resultados_ia:
                    try:
                        resultados = json.loads(row.resultados_ia)
                        if 'nifti_previews' in resultados:
                            print(f"   ✅ Tiene previews NIfTI:")
                            for eje, url in resultados['nifti_previews'].items():
                                print(f"      - {eje}: {url}")
                        elif 'nifti_metadatos' in resultados:
                            print(f"   ⚠️ Tiene metadatos NIfTI pero NO previews")
                            if 'error' in resultados.get('nifti_metadatos', {}):
                                print(f"      Error: {resultados['nifti_metadatos']['error']}")
                        else:
                            print(f"   📊 Tiene otros resultados IA (no NIfTI)")
                    except:
                        print(f"   ⚠️ Error parseando resultados_ia")
                else:
                    print(f"   ❌ Sin resultados_ia")
                
                print()
            
            print("="*80)
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            break

if __name__ == "__main__":
    asyncio.run(check_all())
