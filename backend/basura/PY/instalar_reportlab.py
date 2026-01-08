"""
Script para instalar ReportLab (generación de PDFs)
"""
import subprocess
import sys

def instalar_reportlab():
    """Instalar ReportLab para generación de PDFs"""
    print("=" * 60)
    print("INSTALACIÓN DE REPORTLAB PARA GENERACIÓN DE PDFs")
    print("=" * 60)
    print()
    
    try:
        # Verificar si ya está instalado
        import reportlab
        print("✅ ReportLab ya está instalado")
        print(f"   Versión: {reportlab.Version}")
        return True
    except ImportError:
        print("⚠️  ReportLab no está instalado")
        print()
    
    # Instalar ReportLab
    print("📦 Instalando ReportLab...")
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "reportlab"
        ])
        print("✅ ReportLab instalado correctamente")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error al instalar ReportLab: {e}")
        return False

if __name__ == "__main__":
    exito = instalar_reportlab()
    
    if exito:
        print()
        print("=" * 60)
        print("✅ INSTALACIÓN COMPLETADA")
        print("=" * 60)
        print()
        print("Ahora puedes generar PDFs de estudios especiales.")
    else:
        print()
        print("=" * 60)
        print("❌ INSTALACIÓN FALLIDA")
        print("=" * 60)
        print()
        print("Por favor, instala manualmente con:")
        print("  pip install reportlab")
