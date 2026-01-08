"""
Script de instalación de dependencias para procesador de archivos médicos
Incluye soporte para .ecg, .mat, PDF e imágenes
"""
import subprocess
import sys

def instalar_dependencias():
    """Instala las dependencias necesarias"""
    
    print("=" * 70)
    print("INSTALACIÓN - Procesador de Archivos Médicos")
    print("=" * 70)
    print()
    
    dependencias = [
        'scipy',           # Para archivos .mat
        'numpy',           # Procesamiento numérico
        'pytesseract',     # OCR
        'Pillow',          # Imágenes
        'PyPDF2',          # PDFs
        'pdf2image'        # PDF a imagen
    ]
    
    print("📦 Instalando dependencias de Python...")
    print()
    
    for dep in dependencias:
        print(f"Instalando {dep}...")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', dep])
            print(f"✅ {dep} instalado correctamente")
        except subprocess.CalledProcessError:
            print(f"❌ Error instalando {dep}")
        print()
    
    print("=" * 70)
    print("✅ DEPENDENCIAS DE PYTHON INSTALADAS")
    print("=" * 70)
    print()
    
    print("⚠️  IMPORTANTE: También necesitas instalar Tesseract OCR")
    print()
    print("Windows:")
    print("  1. Descarga: https://github.com/UB-Mannheim/tesseract/wiki")
    print("  2. Ejecuta el instalador")
    print("  3. Agrega al PATH del sistema")
    print()
    print("Linux (Ubuntu/Debian):")
    print("  sudo apt-get install tesseract-ocr tesseract-ocr-spa")
    print()
    print("macOS:")
    print("  brew install tesseract tesseract-lang")
    print()
    print("=" * 70)
    print("Para verificar: tesseract --version")
    print("=" * 70)
    print()
    print("🎉 ¡Instalación completada!")
    print()
    print("Ahora puedes procesar:")
    print("  ✅ Archivos ECG (.ecg)")
    print("  ✅ Archivos MATLAB (.mat)")
    print("  ✅ PDFs con OCR")
    print("  ✅ Imágenes (JPG, PNG, etc.)")
    print()

if __name__ == "__main__":
    instalar_dependencias()
