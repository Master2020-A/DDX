"""
Script de instalación de todas las dependencias del backend DDX
Incluye dependencias base, análisis de EKG, OCR, y más
"""

import subprocess
import sys

def instalar_dependencias():
    """Instala todas las dependencias necesarias"""
    
    dependencias = [
        # Base de datos
        'asyncpg',              # Driver async para PostgreSQL
        'psycopg2-binary',      # Driver sync para PostgreSQL
        'sqlalchemy',           # ORM
        'alembic',              # Migraciones
        
        # Framework web
        'fastapi',              # Framework web
        'uvicorn[standard]',    # Servidor ASGI
        'python-multipart',     # Para archivos
        'python-jose[cryptography]',  # JWT
        'passlib[bcrypt]',      # Hashing de contraseñas
        
        # Procesamiento de datos
        'numpy',                # Operaciones numéricas
        'pandas',               # Análisis de datos
        
        # Análisis de EKG (nuevo)
        'opencv-python',        # Procesamiento de imágenes
        'scipy',                # Procesamiento de señales
        'matplotlib',           # Generación de gráficas
        
        # OCR para laboratorios
        'pytesseract',          # OCR
        'Pillow',               # Procesamiento de imágenes
        'PyPDF2',               # Lectura de PDFs
        'pdf2image',            # Conversión PDF a imagen
        
        # IA y análisis
        'groq',                 # IA para interpretación (gratis)
        'google-generativeai',  # Gemini Vision (gratis)
        'reportlab',            # Generación de PDFs
        
        # Análisis de imágenes médicas
        'nibabel',              # Archivos NIfTI
        'scikit-image',         # Procesamiento de imágenes
        
        # Utilidades
        'python-dotenv',        # Variables de entorno
        'pydantic',             # Validación de datos
        'pydantic-settings',    # Configuración
        'email-validator',      # Validación de emails
    ]
    
    print("=" * 70)
    print("INSTALACIÓN DE DEPENDENCIAS COMPLETAS PARA DDX BACKEND")
    print("=" * 70)
    print()
    print(f"Se instalarán {len(dependencias)} paquetes...")
    print()
    
    errores = []
    
    for i, dep in enumerate(dependencias, 1):
        print(f"[{i}/{len(dependencias)}] 📦 Instalando {dep}...")
        try:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", dep],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE
            )
            print(f"[{i}/{len(dependencias)}] ✅ {dep} instalado correctamente")
        except subprocess.CalledProcessError as e:
            print(f"[{i}/{len(dependencias)}] ❌ Error al instalar {dep}")
            errores.append(dep)
        print()
    
    print("=" * 70)
    print("RESUMEN DE INSTALACIÓN")
    print("=" * 70)
    print()
    
    if errores:
        print(f"⚠️  {len(errores)} paquete(s) con errores:")
        for dep in errores:
            print(f"   - {dep}")
        print()
        print("💡 Intenta instalarlos manualmente:")
        for dep in errores:
            print(f"   pip install {dep}")
    else:
        print("✅ Todas las dependencias instaladas correctamente")
    
    print()
    print("=" * 70)
    print("DEPENDENCIAS EXTERNAS REQUERIDAS")
    print("=" * 70)
    print()
    print("⚠️  TESSERACT OCR (para extracción de laboratorios):")
    print("   Windows: https://github.com/UB-Mannheim/tesseract/wiki")
    print("   Descargar e instalar tesseract-ocr-w64-setup-v5.x.x.exe")
    print()
    print("=" * 70)
    print("SIGUIENTE PASO")
    print("=" * 70)
    print()
    print("🚀 Inicia el servidor con:")
    print("   cd backend")
    print("   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
    print()

if __name__ == "__main__":
    instalar_dependencias()
