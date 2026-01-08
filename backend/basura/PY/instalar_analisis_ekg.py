"""
Script de instalación de dependencias para análisis avanzado de EKG
Instala las librerías necesarias para digitalización y análisis de señales
"""

import subprocess
import sys

def instalar_dependencias():
    """Instala las dependencias necesarias para el análisis de EKG"""
    
    dependencias = [
        'opencv-python',      # Procesamiento de imágenes
        'scipy',              # Procesamiento de señales
        'matplotlib',         # Generación de gráficas
        'numpy',              # Operaciones numéricas (ya debería estar instalado)
    ]
    
    print("=" * 60)
    print("INSTALACIÓN DE DEPENDENCIAS PARA ANÁLISIS AVANZADO DE EKG")
    print("=" * 60)
    print()
    
    for dep in dependencias:
        print(f"📦 Instalando {dep}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
            print(f"✅ {dep} instalado correctamente")
        except subprocess.CalledProcessError:
            print(f"❌ Error al instalar {dep}")
        print()
    
    print("=" * 60)
    print("INSTALACIÓN COMPLETADA")
    print("=" * 60)
    print()
    print("✅ Todas las dependencias han sido instaladas")
    print()
    print("📋 FUNCIONALIDADES DISPONIBLES:")
    print("   - Digitalización de imágenes de EKG")
    print("   - Detección automática de ondas P, Q, R, S, T")
    print("   - Cálculo de intervalos (PR, QRS, QT, QTc)")
    print("   - Diagnóstico avanzado con interpretación narrativa")
    print("   - Generación de gráficas anotadas")
    print()
    print("🚀 ENDPOINTS DISPONIBLES:")
    print("   POST /api/estudios-especiales/ekg/analizar-imagen")
    print("   POST /api/estudios-especiales/ekg/extraer-parametros")
    print("   GET  /api/estudios-especiales/ekg/{id}/interpretacion-narrativa")
    print()

if __name__ == "__main__":
    instalar_dependencias()
