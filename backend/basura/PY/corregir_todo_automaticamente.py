#!/usr/bin/env python3
"""
Script de Corrección Completa - Sistema DDX
Corrige NumPy y reinstala todos los modelos automáticamente
"""
import subprocess
import sys
import time

def print_header(text):
    print("\n" + "=" * 80)
    print(text)
    print("=" * 80 + "\n")

def run_pip_command(command, description):
    """Ejecuta comando pip con feedback"""
    print(f"📦 {description}...")
    try:
        result = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True
        )
        print(f"   ✅ {description} - Completado")
        return True
    except subprocess.CalledProcessError as e:
        print(f"   ⚠️ {description} - Error (puede ser normal si no estaba instalado)")
        return False

def main():
    print_header("🔧 CORRECCIÓN COMPLETA Y AUTOMÁTICA - SISTEMA DDX")
    
    print("Este script:")
    print("   1. Downgrade NumPy a versión 1.x")
    print("   2. Reinstala TODOS los modelos de segmentación")
    print("   3. Verifica la instalación")
    print()
    print("⏱️  Tiempo estimado: 15-20 minutos")
    print("📦 Se reinstalarán: LungMask, TorchIO, TotalSegmentator, nnU-Net, MONAI, PaddleSeg")
    print()
    
    respuesta = input("¿Continuar? (S/n): ").strip().lower()
    if respuesta and respuesta not in ['s', 'si', 'y', 'yes']:
        print("\n❌ Cancelado por el usuario")
        return
    
    # PASO 1: Downgrade NumPy
    print_header("PASO 1/7: Downgrade NumPy")
    print("📦 Instalando NumPy 1.x...")
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "numpy<2.0", "--force-reinstall"],
        check=False
    )
    print("✅ NumPy downgradeado")
    
    # PASO 2-7: Reinstalar modelos
    modelos = [
        ("lungmask", "LungMask"),
        ("torchio", "TorchIO"),
        ("totalsegmentator", "TotalSegmentator"),
        ("nnunetv2", "nnU-Net"),
        ("monai[all]", "MONAI"),
        ("paddlepaddle paddleseg", "PaddlePaddle + PaddleSeg")
    ]
    
    for i, (paquete, nombre) in enumerate(modelos, 2):
        print_header(f"PASO {i}/7: {nombre}")
        
        # Desinstalar
        paquetes_desinstalar = paquete.replace("[all]", "").split()
        for pkg in paquetes_desinstalar:
            run_pip_command(
                [sys.executable, "-m", "pip", "uninstall", pkg, "-y"],
                f"Desinstalando {pkg}"
            )
        
        # Instalar
        print(f"\n📦 Instalando {nombre}...")
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install"] + paquete.split(),
                check=True,
                capture_output=False
            )
            print(f"✅ {nombre} instalado correctamente\n")
        except Exception as e:
            print(f"⚠️ Error instalando {nombre}: {e}\n")
    
    # Verificación final
    print_header("VERIFICACIÓN FINAL")
    print("Ejecutando verificación de modelos...\n")
    time.sleep(2)
    
    try:
        subprocess.run([sys.executable, "verificar_modelos_segmentacion.py"])
    except Exception as e:
        print(f"Error ejecutando verificación: {e}")
    
    print_header("✅ PROCESO COMPLETADO")
    print("\nPróximos pasos:")
    print("   1. Revisar el resultado de la verificación arriba")
    print("   2. Reiniciar servidor: uvicorn app.main:app --reload --port 8612")
    print("   3. Probar endpoints de segmentación")

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
