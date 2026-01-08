#!/usr/bin/env python3
"""
Script para debuggear archivos NIfTI en la base de datos
"""
import sys
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import get_db
from sqlalchemy import text

async def debug_nifti():
    """Revisa archivos NIfTI en la base de datos"""
    async for db in get_db():
        try:
            # Buscar imágenes NIfTI recientes
            query = text("""
                SELECT 
                    id,
                    nombre_archivo,
                    url_archivo,
                    tipo_archivo,
                    resultados_ia::text
                FROM imagenes_medicas
                WHERE nombre_archivo LIKE '%.nii%'
                ORDER BY created_at DESC
                LIMIT 5
            """)
            
            result = await db.execute(query)
            rows = result.fetchall()
            
            print("="*80)
            print("🔍 ARCHIVOS NIfTI EN LA BASE DE DATOS")
            print("="*80)
            print()
            
            if not rows:
                print("❌ No se encontraron archivos NIfTI")
                return
            
            for row in rows:
                print(f"📄 Archivo: {row.nombre_archivo}")
                print(f"   ID: {row.id}")
                print(f"   URL: {row.url_archivo}")
                print(f"   Tipo: {row.tipo_archivo}")
                print(f"   Resultados IA:")
                
                if row.resultados_ia:
                    import json
                    resultados = json.loads(row.resultados_ia)
                    
                    if 'nifti_previews' in resultados:
                        print(f"      ✅ Tiene previews NIfTI:")
                        for eje, url in resultados['nifti_previews'].items():
                            print(f"         - {eje}: {url}")
                            # Verificar si el archivo existe
                            ruta_completa = Path("uploads") / url.replace('/uploads/', '')
                            if ruta_completa.exists():
                                print(f"           ✅ Archivo existe ({ruta_completa.stat().st_size} bytes)")
                            else:
                                print(f"           ❌ Archivo NO existe: {ruta_completa}")
                    else:
                        print("      ❌ NO tiene previews NIfTI")
                    
                    if 'nifti_metadatos' in resultados:
                        meta = resultados['nifti_metadatos']
                        print(f"      Metadatos:")
                        print(f"         - Dimensiones: {meta.get('dimensiones')}")
                        print(f"         - Tipo dato: {meta.get('tipo_dato')}")
                else:
                    print("      ❌ Sin resultados IA")
                
                print()
            
            print("="*80)
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            break

if __name__ == "__main__":
    asyncio.run(debug_nifti())
