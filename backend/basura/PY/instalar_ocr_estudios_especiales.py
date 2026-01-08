"""
Script de instalación de dependencias para extracción OCR de estudios especiales
"""
import subprocess
import sys

def instalar_dependencias():
    """Instala las dependencias necesarias para OCR"""
    
    print("=" * 70)
    print("INSTALACIÓN DE DEPENDENCIAS - Extracción OCR Estudios Especiales")
    print("=" * 70)
    print()
    
    dependencias = [
        'pytesseract',
        'Pillow',
        'PyPDF2',
        'pdf2image'
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
    print("  1. Descarga el instalador desde:")
    print("     https://github.com/UB-Mannheim/tesseract/wiki")
    print("  2. Ejecuta el instalador")
    print("  3. Agrega Tesseract al PATH del sistema")
    print()
    print("Linux (Ubuntu/Debian):")
    print("  sudo apt-get install tesseract-ocr")
    print("  sudo apt-get install tesseract-ocr-spa  # Para español")
    print()
    print("macOS:")
    print("  brew install tesseract")
    print("  brew install tesseract-lang  # Para español")
    print()
    print("=" * 70)
    print("Para verificar la instalación, ejecuta:")
    print("  tesseract --version")
    print("=" * 70)

if __name__ == "__main__":
    instalar_dependencias()
