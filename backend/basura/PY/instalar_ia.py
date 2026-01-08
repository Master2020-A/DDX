"""
Script para instalar e inicializar los modelos de IA médica
"""
import subprocess
import sys


def instalar_dependencias():
    """Instala las dependencias necesarias para análisis IA"""
    
    print("="*70)
    print("INSTALANDO DEPENDENCIAS PARA ANÁLISIS IA MÉDICA")
    print("="*70)
    
    dependencias = [
        ("torch", "PyTorch - Framework de deep learning"),
        ("torchvision", "TorchVision - Procesamiento de imágenes"),
        ("torchxrayvision", "TorchXRayVision - Análisis de rayos X"),
        ("pillow", "PIL - Procesamiento de imágenes"),
        ("scikit-image", "Scikit-Image - Procesamiento científico"),
        ("numpy", "NumPy - Cálculos numéricos"),
    ]
    
    print("\n📦 Dependencias a instalar:")
    for pkg, desc in dependencias:
        print(f"   • {pkg:20s} - {desc}")
    
    respuesta = input("\n¿Deseas continuar con la instalación? (s/n): ")
    
    if respuesta.lower() != 's':
        print("❌ Instalación cancelada")
        return False
    
    print("\n🔄 Instalando dependencias...")
    print("   (Esto puede tomar varios minutos...)\n")
    
    try:
        # Instalar desde requirements
        resultado = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", "requirements_ia.txt"],
            capture_output=True,
            text=True
        )
        
        if resultado.returncode == 0:
            print("\n✅ DEPENDENCIAS INSTALADAS CORRECTAMENTE")
            print("="*70)
            return True
        else:
            print(f"\n❌ ERROR EN INSTALACIÓN:")
            print(resultado.stderr)
            return False
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return False


def probar_modelos():
    """Prueba que los modelos se cargan correctamente"""
    
    print("\n" + "="*70)
    print("PROBANDO CARGA DE MODELOS")
    print("="*70)
    
    try:
        print("\n1️⃣  Verificando PyTorch...")
        import torch
        print(f"   ✅ PyTorch {torch.__version__} instalado")
        print(f"   📊 CUDA disponible: {torch.cuda.is_available()}")
        
        print("\n2️⃣  Verificando TorchXRayVision...")
        import torchxrayvision as xrv
        print(f"   ✅ TorchXRayVision instalado")
        
        print("\n3️⃣  Cargando modelo DenseNet121...")
        model = xrv.models.DenseNet(weights="densenet121-res224-all")
        print(f"   ✅ Modelo cargado correctamente")
        print(f"   📋 Patologías detectables: {len(model.pathologies)}")
        print(f"\n   Patologías:")
        for i, path in enumerate(model.pathologies, 1):
            print(f"      {i:2d}. {path}")
        
        print("\n" + "="*70)
        print("✅ TODOS LOS MODELOS FUNCIONAN CORRECTAMENTE")
        print("="*70)
        print("\n💡 Ahora puedes usar análisis IA REAL en el sistema")
        print("   Los resultados serán precisos y basados en modelos entrenados")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR AL PROBAR MODELOS: {e}")
        print("\n💡 Solución:")
        print("   Ejecuta: pip install -r requirements_ia.txt")
        return False


def main():
    print("\n🤖 CONFIGURACIÓN DE IA MÉDICA - DDX")
    print("="*70)
    
    # Opción 1: Instalar
    print("\nOpciones:")
    print("  1. Instalar dependencias")
    print("  2. Probar modelos (si ya instalaste)")
    print("  3. Ambas")
    
    opcion = input("\nSelecciona una opción (1/2/3): ")
    
    if opcion in ['1', '3']:
        if not instalar_dependencias():
            return
    
    if opcion in ['2', '3']:
        probar_modelos()
    
    print("\n✅ PROCESO COMPLETADO")


if __name__ == "__main__":
    main()
