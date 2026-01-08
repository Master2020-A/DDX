#!/usr/bin/env python3
"""
Script para corregir URLs de previews NIfTI en la base de datos
"""
import sys
import asyncio
from pathlib import Path
import json

sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import get_db
from sqlalchemy import text

async def fix_urls():
    """Corrige las URLs de los previews NIfTI existentes"""
    async for db in get_db():
        try:
            # Obtener imágenes con previews NIfTI
            query = text("""
                SELECT 
                    id,
                    nombre_archivo,
                    resultados_ia::text
                FROM imagenes_medicas
                WHERE resultados_ia::text LIKE '%nifti_previews%'
            """)
            
            result = await db.execute(query)
            rows = result.fetchall()
            
            print("="*80)
            print(f"🔧 CORRIGIENDO URLs DE {len(rows)} ARCHIVOS NIfTI")
            print("="*80)
            print()
            
            for row in rows:
                resultados = json.loads(row.resultados_ia)
                
                if 'nifti_previews' in resultados:
                    previews_old = resultados['nifti_previews']
                    previews_new = {}
                    
                    print(f"📄 {row.nombre_archivo}")
                    
                    for eje, url_old in previews_old.items():
                        # Si la URL no tiene "imagenes_medicas", agregarla
                        if '/uploads/previews/' in url_old:
                            url_new = url_old.replace('/uploads/previews/', '/uploads/imagenes_medicas/previews/')
                            previews_new[eje] = url_new
                            print(f"   {eje}:")
                            print(f"      ❌ {url_old}")
                            print(f"      ✅ {url_new}")
                        else:
                            previews_new[eje] = url_old
                            print(f"   {eje}: OK (no requiere cambio)")
                    
                    # Actualizar en BD
                    resultados['nifti_previews'] = previews_new
                    
                    update_query = text("""
                        UPDATE imagenes_medicas
                        SET resultados_ia = :resultados
                        WHERE id = :id
                    """)
                    
                    await db.execute(
                        update_query,
                        {'resultados': json.dumps(resultados), 'id': row.id}
                    )
                    
                    print()
            
            await db.commit()
            
            print("="*80)
            print("✅ URLs CORREGIDAS EXITOSAMENTE")
            print("="*80)
            print()
            print("💡 Ahora actualiza la página en el navegador (F5)")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
            await db.rollback()
        finally:
            break

if __name__ == "__main__":
    asyncio.run(fix_urls())
