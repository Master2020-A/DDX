"""
Script para actualizar las URLs de las imágenes médicas existentes
"""
import asyncio
from pathlib import Path
from sqlalchemy import text
from app.core.database import engine


async def actualizar_urls():
    """Actualizar urls de imágenes existentes"""
    
    print("="*70)
    print("ACTUALIZANDO URLs DE IMÁGENES MÉDICAS")
    print("="*70)
    
    async with engine.begin() as conn:
        # Obtener todas las imágenes sin url_archivo
        result = await conn.execute(
            text("SELECT id, ruta_archivo FROM imagenes_medicas WHERE url_archivo IS NULL")
        )
        imagenes = result.fetchall()
        
        print(f"\n📊 Imágenes a actualizar: {len(imagenes)}")
        
        if len(imagenes) == 0:
            print("\n✅ Todas las imágenes ya tienen URL asignada")
            return True
        
        actualizadas = 0
        
        for imagen in imagenes:
            try:
                imagen_id = imagen[0]  # UUID
                ruta_archivo = imagen[1]  # String
                
                # Extraer nombre del archivo de la ruta
                ruta = Path(ruta_archivo)
                nombre_archivo = ruta.name
                
                # Construir URL
                url_archivo = f"/uploads/imagenes_medicas/{nombre_archivo}"
                
                # Actualizar en BD
                await conn.execute(
                    text(
                        "UPDATE imagenes_medicas SET url_archivo = :url WHERE id = :id"
                    ),
                    {"url": url_archivo, "id": imagen_id}
                )
                
                actualizadas += 1
                print(f"  ✓ {nombre_archivo}")
                
            except Exception as e:
                print(f"  ✗ Error en imagen {imagen_id}: {e}")
        
        print(f"\n✅ ACTUALIZACIÓN COMPLETADA")
        print(f"   Imágenes actualizadas: {actualizadas}/{len(imagenes)}")
        print("="*70)
        
        return True


if __name__ == "__main__":
    asyncio.run(actualizar_urls())
