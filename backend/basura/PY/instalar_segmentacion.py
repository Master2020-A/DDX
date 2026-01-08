#!/usr/bin/env python3
"""
Instalador de TotalSegmentator y dependencias para segmentación anatómica
"""
import subprocess
import sys
import platform

print("="*80)
print("🔬 INSTALANDO TOTALSEGMENTATOR Y DEPENDENCIAS")
print("="*80)
print()

# Información del sistema
print(f"💻 Sistema: {platform.system()} {platform.release()}")
print(f"🐍 Python: {sys.version.split()[0]}")
print()

# Dependencias
dependencias = [
    ("torch", "PyTorch - Framework de deep learning", "torch torchvision --index-url https://download.pytorch.org/whl/cu118"),
    ("totalsegmentator", "TotalSegmentator - Segmentación de 104 estructuras", "totalsegmentator"),
]

errores = []

for i, (paquete, descripcion, comando_install) in enumerate(dependencias, 1):
    print(f"[{i}/{len(dependencias)}] 📦 {paquete}")
    print(f"    {descripcion}")
    print()
    
    try:
        # Para PyTorch, usar comando especial con CUDA
        if paquete == "torch":
            print("    ⚠️ Instalando PyTorch con soporte CUDA...")
            print("    (Esto puede tardar varios minutos)")
            
            resultado = subprocess.run(
                [sys.executable, "-m", "pip", "install"] + comando_install.split(),
                capture_output=True,
                text=True,
                timeout=600  # 10 minutos
            )
        else:
            resultado = subprocess.run(
                [sys.executable, "-m", "pip", "install", comando_install],
                capture_output=True,
                text=True,
                timeout=300  # 5 minutos
            )
        
        if resultado.returncode == 0:
            print(f"    ✅ {paquete} instalado correctamente")
        else:
            print(f"    ❌ Error instalando {paquete}")
            if resultado.stderr:
                print(f"       {resultado.stderr[:200]}")
            errores.append(paquete)
    
    except subprocess.TimeoutExpired:
        print(f"    ⏱️ Timeout - instalación muy larga")
        print(f"    💡 Intenta manualmente: pip install {comando_install}")
        errores.append(paquete)
    
    except Exception as e:
        print(f"    ❌ Error: {e}")
        errores.append(paquete)
    
    print()

print("="*80)

if errores:
    print("⚠️ INSTALACIÓN PARCIAL")
    print(f"   Paquetes con errores: {', '.join(errores)}")
    print()
    print("💡 Instalación manual recomendada:")
    print()
    for paquete, descripcion, comando_install in dependencias:
        if paquete in errores:
            print(f"   pip install {comando_install}")
    print()
    print("📚 Para más información:")
    print("   https://github.com/wasserth/TotalSegmentator")
else:
    print("✅ INSTALACIÓN COMPLETADA")
    print()
    print("🎉 ¡TotalSegmentator instalado correctamente!")
    print()
    print("📋 CARACTERÍSTICAS DISPONIBLES:")
    print("   • Segmentación de 104 estructuras anatómicas")
    print("   • Compatible con CT y MRI")
    print("   • Máscaras 3D por órgano")
    print("   • Cálculo de volúmenes precisos")
    print("   • Visualización con colores por estructura")
    print()
    print("🚀 PRÓXIMOS PASOS:")
    print("   1. Reinicia el backend")
    print("   2. Sube un archivo NIfTI")
    print("   3. Haz click en 'Segmentar Anatomía'")
    print("   4. Espera 1-5 minutos (depende del tamaño)")
    print("   5. Explora el dashboard 3D con las estructuras")
    print()
    print("⚡ MODOS DE SEGMENTACIÓN:")
    print("   • Fast (rápido): ~1-2 minutos, estructuras principales")
    print("   • Full (completo): ~3-5 minutos, todas las estructuras")
    print()
    print("💾 REQUISITOS DE MEMORIA:")
    print("   • GPU recomendada: 8GB VRAM mínimo")
    print("   • CPU: 16GB RAM mínimo")
    print()
    print("⚠️ NOTA IMPORTANTE:")
    print("   Si no tienes GPU NVIDIA, la segmentación usará CPU")
    print("   y será más lenta (5-15 minutos)")

print("="*80)
