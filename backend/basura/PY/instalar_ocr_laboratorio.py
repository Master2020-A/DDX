"""
Script para instalar dependencias de OCR para extracción de laboratorios
"""
import subprocess
import sys
import platform

def instalar_dependencias():
    """Instala las dependencias necesarias para OCR"""
    print("=" * 60)
    print("INSTALACIÓN DE DEPENDENCIAS PARA EXTRACCIÓN DE LABORATORIOS")
    print("=" * 60)
    print()
    
    # Dependencias Python
    dependencias = [
        'pytesseract',
        'Pillow',
        'PyPDF2',
        'pdf2image'
    ]
    
    print("📦 Instalando dependencias de Python...")
    for dep in dependencias:
        print(f"  - Instalando {dep}...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', dep])
    
    print()
    print("✅ Dependencias de Python instaladas correctamente")
    print()
    
    # Instrucciones para Tesseract
    sistema = platform.system()
    
    print("=" * 60)
    print("INSTALACIÓN DE TESSERACT OCR")
    print("=" * 60)
    print()
    
    if sistema == "Windows":
        print("🪟 WINDOWS:")
        print()
        print("1. Descarga el instalador de Tesseract:")
        print("   https://github.com/UB-Mannheim/tesseract/wiki")
        print()
        print("2. Ejecuta el instalador (tesseract-ocr-w64-setup-*.exe)")
        print()
        print("3. Durante la instalación, selecciona:")
        print("   - Idioma: Spanish (spa)")
        print("   - Ruta recomendada: C:\\Program Files\\Tesseract-OCR")
        print()
        print("4. Agrega Tesseract al PATH del sistema:")
        print("   - Panel de Control → Sistema → Configuración avanzada")
        print("   - Variables de entorno → Path → Editar")
        print("   - Agregar: C:\\Program Files\\Tesseract-OCR")
        print()
        print("5. Reinicia la terminal/IDE")
        print()
        
    elif sistema == "Linux":
        print("🐧 LINUX:")
        print()
        print("Ubuntu/Debian:")
        print("  sudo apt-get update")
        print("  sudo apt-get install tesseract-ocr")
        print("  sudo apt-get install tesseract-ocr-spa")
        print("  sudo apt-get install poppler-utils")
        print()
        print("Fedora/CentOS:")
        print("  sudo dnf install tesseract")
        print("  sudo dnf install tesseract-langpack-spa")
        print("  sudo dnf install poppler-utils")
        print()
        
    elif sistema == "Darwin":
        print("🍎 macOS:")
        print()
        print("Usando Homebrew:")
        print("  brew install tesseract")
        print("  brew install tesseract-lang")
        print("  brew install poppler")
        print()
    
    print("=" * 60)
    print("VERIFICACIÓN")
    print("=" * 60)
    print()
    print("Para verificar que Tesseract está instalado correctamente:")
    print()
    print("  tesseract --version")
    print()
    print("Debería mostrar la versión instalada.")
    print()
    
    print("=" * 60)
    print("✅ INSTALACIÓN COMPLETADA")
    print("=" * 60)
    print()
    print("Ahora puedes usar la extracción automática de laboratorios desde:")
    print("  - Archivos PDF")
    print("  - Imágenes (JPG, PNG, TIFF, etc.)")
    print()
    print("Endpoints disponibles:")
    print("  POST /api/laboratorio/extraer-desde-archivo/")
    print("  POST /api/laboratorio/extraer-y-crear-desde-archivo/")
    print()

if __name__ == "__main__":
    try:
        instalar_dependencias()
    except Exception as e:
        print(f"❌ Error durante la instalación: {e}")
        sys.exit(1)
