#!/usr/bin/env python3
"""
Script de Solución de Problemas - Sistema DDX
Detecta y corrige automáticamente problemas comunes
"""
import subprocess
import sys
import os
from pathlib import Path

def print_header(text):
    print("\n" + "=" * 80)
    print(text)
    print("=" * 80 + "\n")

def check_numpy_version():
    """Verifica versión de NumPy y corrige si es necesario"""
    print("🔍 Verificando versión de NumPy...")
    try:
        import numpy as np
        version = np.__version__
        major_version = int(version.split('.')[0])
        
        print(f"   NumPy versión actual: {version}")
        
        if major_version >= 2:
            print("   ⚠️ NumPy 2.x detectado - Incompatible con PaddlePaddle")
            print("   🔧 Corrigiendo: Instalando NumPy 1.x...")
            
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "numpy<2.0", "--force-reinstall"],
                check=True
            )
            
            print("   ✅ NumPy downgradeado correctamente")
            return True
        else:
            print("   ✅ NumPy versión compatible")
            return True
    except Exception as e:
        print(f"   ❌ Error verificando NumPy: {e}")
        return False

def configure_nnunet_paths():
    """Configura variables de entorno para nnU-Net"""
    print("🔍 Configurando nnU-Net...")
    
    # Verificar si ya están configuradas
    raw = os.environ.get('nnUNet_raw')
    preprocessed = os.environ.get('nnUNet_preprocessed')
    results = os.environ.get('nnUNet_results')
    
    if raw and preprocessed and results:
        print("   ✅ Variables de nnU-Net ya configuradas")
        return True
    
    # Crear directorios
    base_path = Path.home() / "nnUNet_data"
    raw_path = base_path / "nnUNet_raw"
    preprocessed_path = base_path / "nnUNet_preprocessed"
    results_path = base_path / "nnUNet_results"
    
    print(f"   📁 Creando directorios en: {base_path}")
    raw_path.mkdir(parents=True, exist_ok=True)
    preprocessed_path.mkdir(parents=True, exist_ok=True)
    results_path.mkdir(parents=True, exist_ok=True)
    
    # Configurar variables de entorno para esta sesión
    os.environ['nnUNet_raw'] = str(raw_path)
    os.environ['nnUNet_preprocessed'] = str(preprocessed_path)
    os.environ['nnUNet_results'] = str(results_path)
    
    print("   ✅ Variables configuradas temporalmente para esta sesión")
    print(f"      nnUNet_raw={raw_path}")
    print(f"      nnUNet_preprocessed={preprocessed_path}")
    print(f"      nnUNet_results={results_path}")
    print()
    print("   ⚠️ NOTA: Para hacer permanente, ejecuta:")
    print("      configurar_nnunet.bat")
    
    return True

def test_imports():
    """Prueba importar todos los modelos"""
    print("🔍 Probando importaciones de modelos...")
    
    models = {
        'lungmask': 'import lungmask',
        'totalsegmentator': 'from totalsegmentator.python_api import totalsegmentator',
        'nnunetv2': 'from nnunetv2.inference.predict_from_raw_data import nnUNetPredictor',
        'torchio': 'import torchio',
        'monai': 'from monai.networks.nets import SwinUNETR',
    }
    
    results = {}
    for name, import_cmd in models.items():
        try:
            exec(import_cmd)
            print(f"   ✅ {name}")
            results[name] = True
        except ImportError as e:
            print(f"   ❌ {name} - No instalado")
            results[name] = False
        except Exception as e:
            print(f"   ⚠️ {name} - Error: {str(e)[:50]}")
            results[name] = False
    
    return results

def main():
    print_header("🔧 SOLUCIÓN AUTOMÁTICA DE PROBLEMAS - SISTEMA DDX")
    
    print("Este script detectará y corregirá automáticamente:")
    print("   1. Incompatibilidad de versión de NumPy")
    print("   2. Variables de entorno faltantes de nnU-Net")
    print("   3. Verificará importaciones de modelos")
    print()
    
    input("Presiona Enter para continuar...")
    
    # Problema 1: NumPy
    print_header("PROBLEMA 1: Versión de NumPy")
    check_numpy_version()
    
    # Problema 2: nnU-Net
    print_header("PROBLEMA 2: Variables de nnU-Net")
    configure_nnunet_paths()
    
    # Verificación de modelos
    print_header("VERIFICACIÓN: Importaciones de Modelos")
    results = test_imports()
    
    # Resumen
    print_header("📊 RESUMEN")
    
    installed = sum(1 for v in results.values() if v)
    total = len(results)
    
    print(f"Modelos disponibles: {installed}/{total}")
    print()
    
    if installed == total:
        print("✅ Todos los modelos están disponibles")
    elif installed > 0:
        print(f"⚠️ {total - installed} modelo(s) no disponible(s)")
        print("\nPara instalar los faltantes:")
        for name, available in results.items():
            if not available:
                print(f"   pip install {name}")
    else:
        print("❌ No hay modelos disponibles")
        print("\nEjecuta: pip install -r requirements_segmentacion_avanzada.txt")
    
    print("\n" + "=" * 80)
    print("Ahora ejecuta: python verificar_modelos_segmentacion.py")
    print("=" * 80)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Interrumpido por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
