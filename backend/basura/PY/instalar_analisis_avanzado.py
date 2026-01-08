#!/usr/bin/env python3
"""
Instalador de dependencias para análisis avanzado de imágenes NIfTI
"""
import subprocess
import sys

print("="*80)
print("📦 INSTALANDO DEPENDENCIAS PARA ANÁLISIS AVANZADO")
print("="*80)
print()

# Dependencias necesarias
dependencias = [
    ("scipy", "Procesamiento científico y filtros"),
    ("scikit-image", "Análisis y segmentación de imágenes"),
]

errores = []

for paquete, descripcion in dependencias:
    print(f"📥 Instalando {paquete}...")
    print(f"   ({descripcion})")
    
    try:
        resultado = subprocess.run(
            [sys.executable, "-m", "pip", "install", paquete],
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if resultado.returncode == 0:
            print(f"   ✅ {paquete} instalado correctamente")
        else:
            print(f"   ❌ Error instalando {paquete}")
            print(f"      {resultado.stderr}")
            errores.append(paquete)
    
    except Exception as e:
        print(f"   ❌ Error: {e}")
        errores.append(paquete)
    
    print()

print("="*80)

if errores:
    print("❌ INSTALACIÓN INCOMPLETA")
    print(f"   Paquetes con errores: {', '.join(errores)}")
    print()
    print("💡 Intenta instalarlos manualmente:")
    for paquete in errores:
        print(f"   pip install {paquete}")
else:
    print("✅ INSTALACIÓN COMPLETADA")
    print()
    print("🎉 ¡Análisis avanzado listo para usar!")
    print()
    print("📋 Características habilitadas:")
    print("   • Análisis multiplanar (3 ejes)")
    print("   • Métricas cuantitativas (volumen, intensidades)")
    print("   • Detección de regiones de interés")
    print("   • Evaluación de calidad de imagen (SNR, CNR)")
    print("   • Reporte detallado en texto")
    print()
    print("🚀 Para usar:")
    print("   1. Reinicia el backend: uvicorn app.main:app --reload --port=8612")
    print("   2. Sube un archivo NIfTI")
    print("   3. Haz click en 'Analizar con IA'")
    print("   4. Verás hallazgos mucho más detallados")

print("="*80)
