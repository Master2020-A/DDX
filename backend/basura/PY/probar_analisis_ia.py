"""
Script para probar el análisis de IA con una imagen
"""
import asyncio
from pathlib import Path
from app.services.imagen_ia_service_real import imagen_ia_real_service


async def probar_analisis():
    """Prueba el análisis de una imagen"""
    
    print("="*70)
    print("PRUEBA DE ANÁLISIS DE IA")
    print("="*70)
    
    # Buscar una imagen en el directorio de uploads
    uploads_dir = Path("uploads/imagenes_medicas")
    
    if not uploads_dir.exists():
        print("\n❌ No existe el directorio uploads/imagenes_medicas")
        print("   Primero sube una imagen desde el frontend")
        return
    
    # Listar imágenes disponibles
    imagenes = list(uploads_dir.glob("*"))
    imagenes = [img for img in imagenes if img.suffix.lower() in ['.jpg', '.jpeg', '.png', '.bmp']]
    
    if not imagenes:
        print("\n❌ No hay imágenes en el directorio")
        print("   Sube una imagen desde el frontend primero")
        return
    
    print(f"\n📁 Imágenes disponibles: {len(imagenes)}")
    for i, img in enumerate(imagenes, 1):
        print(f"   {i}. {img.name} ({img.stat().st_size / 1024:.1f} KB)")
    
    # Usar la primera imagen
    imagen_path = str(imagenes[0])
    print(f"\n🔍 Analizando: {imagenes[0].name}")
    print("   ⏳ Procesando...")
    
    # Ejecutar análisis
    resultado = await imagen_ia_real_service.analizar_imagen_chexnet_real(
        imagen_path=imagen_path,
        umbral_confianza=0.5
    )
    
    # Mostrar resultados
    print("\n" + "="*70)
    print("RESULTADOS DEL ANÁLISIS")
    print("="*70)
    
    print(f"\n🤖 Modelo: {resultado.get('modelo', 'N/A')}")
    print(f"⏱️  Tiempo: {resultado.get('tiempo_procesamiento', 0):.2f}s")
    print(f"📊 Confianza Global: {resultado.get('confianza_global', 0):.2%}")
    
    print("\n📋 HALLAZGOS:")
    hallazgos = resultado.get('hallazgos', [])
    for hallazgo in hallazgos:
        print(f"   • {hallazgo}")
    
    print("\n📈 PREDICCIONES DETALLADAS:")
    predicciones = resultado.get('predicciones', {})
    
    # Ordenar por confianza
    predicciones_ordenadas = sorted(
        predicciones.items(),
        key=lambda x: x[1],
        reverse=True
    )
    
    for patologia, confianza in predicciones_ordenadas[:10]:  # Top 10
        barra = "█" * int(confianza * 50)
        print(f"   {patologia:25s} {confianza:6.2%} {barra}")
    
    if 'nota' in resultado:
        print(f"\n⚠️  NOTA: {resultado['nota']}")
    
    print("\n" + "="*70)
    print("✅ ANÁLISIS COMPLETADO")
    print("="*70)


if __name__ == "__main__":
    asyncio.run(probar_analisis())
