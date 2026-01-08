#!/usr/bin/env python3
"""
Reprocesar archivos NIfTI existentes para generar previews
"""
import sys
import asyncio
from pathlib import Path
import json

sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import get_db
from sqlalchemy import text
from app.services.nifti_processor import get_nifti_processor

async def reprocesar():
    """Reprocesa archivos NIfTI que no tienen previews"""
    
    processor = get_nifti_processor()
    
    async for db in get_db():
        try:
            # Buscar archivos .nii que no tienen previews
            query = text("""
                SELECT 
                    id,
                    nombre_archivo,
                    ruta_archivo,
                    resultados_ia::text
                FROM imagenes_medicas
                WHERE nombre_archivo LIKE '%.nii%'
                ORDER BY created_at DESC
            """)
            
            result = await db.execute(query)
            rows = result.fetchall()
            
            print("="*80)
            print(f"🔄 REPROCESANDO {len(rows)} ARCHIVOS NIfTI")
            print("="*80)
            print()
            
            for row in rows:
                print(f"📄 {row.nombre_archivo}")
                print(f"   Ruta: {row.ruta_archivo}")
                
                # Verificar si el archivo existe
                if not Path(row.ruta_archivo).exists():
                    print(f"   ❌ Archivo no existe en disco")
                    print()
                    continue
                
                # Verificar si ya tiene previews
                tiene_previews = False
                if row.resultados_ia:
                    resultados = json.loads(row.resultados_ia)
                    if 'nifti_previews' in resultados:
                        tiene_previews = True
                        print(f"   ℹ️ Ya tiene previews, regenerando...")
                
                try:
                    # Extraer metadatos
                    print(f"   📋 Extrayendo metadatos...")
                    metadatos = processor.extraer_metadatos(row.ruta_archivo)
                    
                    if 'error' in metadatos:
                        print(f"   ❌ Error en metadatos: {metadatos['error']}")
                        continue
                    
                    print(f"   ✅ Metadatos OK - Dimensiones: {metadatos.get('dimensiones')}")
                    
                    # Generar previews
                    print(f"   🖼️ Generando previews...")
                    preview_dir = Path("uploads/imagenes_medicas/previews") / str(row.id)
                    preview_dir.mkdir(parents=True, exist_ok=True)
                    
                    resultado_proceso = processor.procesar_para_visualizacion(
                        row.ruta_archivo,
                        preview_dir
                    )
                    
                    # Convertir rutas a URLs
                    previews_urls = {}
                    for eje, ruta_absoluta in resultado_proceso.get('previews', {}).items():
                        ruta_path = Path(ruta_absoluta)
                        ruta_relativa = ruta_path.relative_to(Path("uploads"))
                        preview_url = f"/uploads/{ruta_relativa.as_posix()}"
                        previews_urls[eje] = preview_url
                        print(f"      ✅ {eje}: {preview_url}")
                    
                    # Actualizar en BD
                    nuevos_resultados = {
                        'nifti_metadatos': metadatos,
                        'nifti_previews': previews_urls,
                        'procesado_nifti': True
                    }
                    
                    update_query = text("""
                        UPDATE imagenes_medicas
                        SET resultados_ia = :resultados
                        WHERE id = :id
                    """)
                    
                    await db.execute(
                        update_query,
                        {'resultados': json.dumps(nuevos_resultados), 'id': row.id}
                    )
                    
                    print(f"   ✅ Archivo procesado y actualizado en BD")
                    
                except Exception as e:
                    print(f"   ❌ Error procesando: {e}")
                    import traceback
                    traceback.print_exc()
                
                print()
            
            await db.commit()
            
            print("="*80)
            print("✅ REPROCESAMIENTO COMPLETADO")
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
    asyncio.run(reprocesar())
