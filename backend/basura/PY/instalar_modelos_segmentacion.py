#!/usr/bin/env python3
"""
Script de Instalación Automática de Modelos de Segmentación
Sistema DDX - Diagnóstico Diferencial Inteligente
"""
import subprocess
import sys
import time

def print_header(text):
    print("\n" + "=" * 80)
    print(text)
    print("=" * 80 + "\n")

def install_package(package_name, display_name, size_info):
    """Instala un paquete con feedback visual"""
    print(f"📦 Instalando {display_name}...")
    print(f"   Tamaño aproximado: {size_info}")
    print(f"   Comando: pip install {package_name}")
    print()
    
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", package_name],
            capture_output=False,
            text=True
        )
        
        if result.returncode == 0:
            print(f"   ✅ {display_name} instalado correctamente\n")
            return True
        else:
            print(f"   ❌ Error instalando {display_name}\n")
            return False
    except Exception as e:
        print(f"   ❌ Excepción durante instalación: {e}\n")
        return False

def main():
    print_header("🚀 INSTALACIÓN DE MODELOS DE SEGMENTACIÓN AVANZADA - SISTEMA DDX")
    
    print("Este script instalará los siguientes modelos:")
    print("   1. LungMask - Segmentación pulmonar (~100MB)")
    print("   2. TotalSegmentator - 104 estructuras (~1.5GB)")
    print("   3. nnU-Net - Framework universal (variable)")
    print("   4. PaddleSeg - Framework Baidu (~500MB)")
    print()
    print("⏱️  Tiempo estimado: 10-20 minutos")
    print("💾 Espacio requerido: ~3GB + modelos descargados al primer uso")
    print()
    
    respuesta = input("¿Continuar con la instalación? (S/n): ").strip().lower()
    if respuesta and respuesta != 's' and respuesta != 'si':
        print("\n❌ Instalación cancelada por el usuario")
        return
    
    # Contador de éxitos
    instalados = 0
    total = 4
    
    print_header("PASO 1/4: LungMask")
    if install_package("lungmask", "LungMask", "~100MB"):
        instalados += 1
    
    print_header("PASO 2/4: TotalSegmentator")
    if install_package("totalsegmentator", "TotalSegmentator", "~1.5GB (modelos se descargan al primer uso)"):
        instalados += 1
    
    print_header("PASO 3/4: nnU-Net")
    if install_package("nnunetv2", "nnU-Net", "Variable según modelos"):
        instalados += 1
    
    print_header("PASO 4/4: PaddlePaddle y PaddleSeg")
    print("📦 Instalando PaddlePaddle...")
    print("   Nota: PaddlePaddle puede tardar varios minutos")
    print()
    
    # Intentar instalar PaddlePaddle
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "paddlepaddle"],
            capture_output=False
        )
        
        # Luego PaddleSeg
        if install_package("paddleseg", "PaddleSeg", "~500MB"):
            instalados += 1
    except Exception as e:
        print(f"   ⚠️ Advertencia con PaddlePaddle/PaddleSeg: {e}")
        print("   Puedes continuar sin este modelo")
    
    # Resumen final
    print_header("📊 RESUMEN DE INSTALACIÓN")
    print(f"✅ Modelos instalados exitosamente: {instalados}/{total}")
    
    if instalados == total:
        print("\n🎉 ¡INSTALACIÓN COMPLETADA CON ÉXITO!")
    elif instalados > 0:
        print(f"\n⚠️ Instalación parcial: {instalados}/{total} modelos instalados")
    else:
        print("\n❌ No se pudo instalar ningún modelo")
        return
    
    print("\n📋 PRÓXIMOS PASOS:")
    print("   1. Verificar instalación:")
    print("      python verificar_modelos_segmentacion.py")
    print()
    print("   2. Reiniciar servidor backend:")
    print("      uvicorn app.main:app --reload --port 8612")
    print()
    print("   3. (OPCIONAL) Instalar GPU CUDA para mejor rendimiento:")
    print("      pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118")
    print()
    
    # Preguntar si verificar
    verificar = input("\n¿Ejecutar verificación de modelos ahora? (S/n): ").strip().lower()
    if not verificar or verificar == 's' or verificar == 'si':
        print("\n" + "=" * 80)
        print("Ejecutando verificación...")
        print("=" * 80 + "\n")
        time.sleep(1)
        
        try:
            subprocess.run([sys.executable, "verificar_modelos_segmentacion.py"])
        except Exception as e:
            print(f"Error ejecutando verificación: {e}")
    
    print("\n" + "=" * 80)
    print("✅ PROCESO COMPLETADO")
    print("=" * 80)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Instalación interrumpida por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
