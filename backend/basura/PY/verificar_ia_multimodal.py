"""
Script de Verificación del Sistema Multi-Modal de IA
Verifica que todas las dependencias estén instaladas correctamente
"""
import sys
from typing import Dict, List

def verificar_dependencias() -> Dict[str, bool]:
    """Verifica la disponibilidad de todas las dependencias"""
    
    resultados = {}
    
    print("=" * 70)
    print("VERIFICACIÓN DE DEPENDENCIAS - SISTEMA MULTI-MODAL IA")
    print("=" * 70)
    print()
    
    # 1. PyTorch
    print("1️⃣ Verificando PyTorch...")
    try:
        import torch
        print(f"   ✅ PyTorch {torch.__version__} instalado")
        if torch.cuda.is_available():
            print(f"   ✅ CUDA disponible - GPU: {torch.cuda.get_device_name(0)}")
        else:
            print("   ⚠️  CUDA no disponible - usando CPU")
        resultados['torch'] = True
    except ImportError:
        print("   ❌ PyTorch NO instalado")
        print("      Instalar: pip install torch torchvision")
        resultados['torch'] = False
    print()
    
    # 2. TorchXRayVision (Rayos X)
    print("2️⃣ Verificando TorchXRayVision (Rayos X Tórax)...")
    try:
        import torchxrayvision as xrv
        print(f"   ✅ TorchXRayVision instalado")
        print("   ✅ Disponible: Análisis de Rayos X de Tórax")
        print("   📋 Patologías: 18+ (Cardiomegaly, Pneumonia, etc.)")
        resultados['torchxrayvision'] = True
    except ImportError:
        print("   ❌ TorchXRayVision NO instalado")
        print("      Instalar: pip install torchxrayvision")
        resultados['torchxrayvision'] = False
    print()
    
    # 3. MONAI (CT/MRI)
    print("3️⃣ Verificando MONAI (CT/MRI)...")
    try:
        import monai
        print(f"   ✅ MONAI {monai.__version__} instalado")
        print("   ✅ Disponible: Análisis de CT y MRI")
        resultados['monai'] = True
    except ImportError:
        print("   ❌ MONAI NO instalado")
        print("      Instalar: pip install monai")
        resultados['monai'] = False
    print()
    
    # 4. PyDICOM (Procesamiento DICOM)
    print("4️⃣ Verificando PyDICOM (Formato DICOM)...")
    try:
        import pydicom
        print(f"   ✅ PyDICOM {pydicom.__version__} instalado")
        print("   ✅ Disponible: Lectura de archivos DICOM")
        resultados['pydicom'] = True
    except ImportError:
        print("   ❌ PyDICOM NO instalado")
        print("      Instalar: pip install pydicom")
        resultados['pydicom'] = False
    print()
    
    # 5. Pillow (Procesamiento de imágenes)
    print("5️⃣ Verificando Pillow (Procesamiento de imágenes)...")
    try:
        from PIL import Image
        print(f"   ✅ Pillow instalado")
        resultados['pillow'] = True
    except ImportError:
        print("   ❌ Pillow NO instalado")
        print("      Instalar: pip install pillow")
        resultados['pillow'] = False
    print()
    
    # 6. NumPy
    print("6️⃣ Verificando NumPy...")
    try:
        import numpy as np
        print(f"   ✅ NumPy {np.__version__} instalado")
        resultados['numpy'] = True
    except ImportError:
        print("   ❌ NumPy NO instalado")
        print("      Instalar: pip install numpy")
        resultados['numpy'] = False
    print()
    
    # 7. Scikit-Image
    print("7️⃣ Verificando Scikit-Image...")
    try:
        import skimage
        print(f"   ✅ Scikit-Image {skimage.__version__} instalado")
        resultados['skimage'] = True
    except ImportError:
        print("   ❌ Scikit-Image NO instalado")
        print("      Instalar: pip install scikit-image")
        resultados['skimage'] = False
    print()
    
    # 8. OpenCV
    print("8️⃣ Verificando OpenCV...")
    try:
        import cv2
        print(f"   ✅ OpenCV {cv2.__version__} instalado")
        resultados['opencv'] = True
    except ImportError:
        print("   ⚠️  OpenCV NO instalado (opcional)")
        print("      Instalar: pip install opencv-python")
        resultados['opencv'] = False
    print()
    
    return resultados


def verificar_servicio():
    """Verifica que el servicio multi-modal funcione correctamente"""
    
    print("=" * 70)
    print("VERIFICACIÓN DEL SERVICIO MULTI-MODAL")
    print("=" * 70)
    print()
    
    try:
        from app.services.imagen_ia_multimodal_service import get_servicio_multimodal
        
        print("✅ Servicio multi-modal importado correctamente")
        print()
        
        # Inicializar servicio
        servicio = get_servicio_multimodal()
        print("✅ Servicio multi-modal inicializado")
        print()
        
        # Obtener disponibilidad
        disponibilidad = servicio.obtener_disponibilidad()
        
        print("📊 DISPONIBILIDAD DE MODELOS:")
        print("-" * 70)
        
        tipos = {
            'rayos_x_torax': 'Rayos X - Tórax',
            'rayos_x_otras': 'Rayos X - Otras Regiones',
            'tomografia': 'Tomografía (CT)',
            'resonancia': 'Resonancia Magnética (MRI)',
            'ecografia': 'Ecografía (US)',
            'mamografia': 'Mamografía',
            'endoscopia': 'Endoscopia'
        }
        
        for key, nombre in tipos.items():
            estado = "✅ Disponible" if disponibilidad.get(key, False) else "⚠️  No disponible"
            print(f"  {nombre:<30} {estado}")
        
        print()
        
        # Modelos cargados
        modelos_cargados = servicio.obtener_modelos_cargados()
        if modelos_cargados:
            print("💾 MODELOS EN MEMORIA:")
            for modelo in modelos_cargados:
                print(f"  - {modelo}")
        else:
            print("💾 MODELOS EN MEMORIA: Ninguno (se cargarán al usar)")
        
        print()
        return True
        
    except Exception as e:
        print(f"❌ Error al verificar servicio: {str(e)}")
        print()
        return False


def generar_reporte(resultados: Dict[str, bool]):
    """Genera un reporte final de la verificación"""
    
    print("=" * 70)
    print("REPORTE FINAL")
    print("=" * 70)
    print()
    
    total = len(resultados)
    instalados = sum(1 for v in resultados.values() if v)
    porcentaje = (instalados / total * 100) if total > 0 else 0
    
    print(f"📊 Dependencias instaladas: {instalados}/{total} ({porcentaje:.0f}%)")
    print()
    
    if porcentaje == 100:
        print("✅ ¡SISTEMA COMPLETAMENTE FUNCIONAL!")
        print("   Todas las dependencias están instaladas correctamente.")
        print()
        print("🚀 PRÓXIMOS PASOS:")
        print("   1. Reiniciar el servidor backend")
        print("   2. Subir una imagen médica")
        print("   3. Usar el botón 'Analizar IA'")
        print("   4. Ver los resultados del análisis")
        
    elif porcentaje >= 60:
        print("⚠️  SISTEMA PARCIALMENTE FUNCIONAL")
        print("   Algunas funcionalidades están disponibles.")
        print()
        print("📋 DEPENDENCIAS FALTANTES:")
        for dep, instalado in resultados.items():
            if not instalado:
                print(f"   ❌ {dep}")
        print()
        print("💡 RECOMENDACIÓN:")
        print("   Ejecutar: pip install -r requirements_ia_multimodal.txt")
        
    else:
        print("❌ SISTEMA NO FUNCIONAL")
        print("   Muchas dependencias críticas faltan.")
        print()
        print("🔧 SOLUCIÓN:")
        print("   1. Activar entorno virtual:")
        print("      conda activate ddx")
        print()
        print("   2. Instalar todas las dependencias:")
        print("      pip install -r requirements_ia_multimodal.txt")
        print()
        print("   3. Volver a ejecutar este script:")
        print("      python verificar_ia_multimodal.py")
    
    print()
    print("=" * 70)


def main():
    """Función principal"""
    
    print()
    print("╔═══════════════════════════════════════════════════════════════════╗")
    print("║                                                                   ║")
    print("║         🧠 SISTEMA MULTI-MODAL DE IA MÉDICA - DDX                ║")
    print("║              Verificación de Instalación                         ║")
    print("║                                                                   ║")
    print("╚═══════════════════════════════════════════════════════════════════╝")
    print()
    
    # Verificar dependencias
    resultados = verificar_dependencias()
    
    # Verificar servicio
    servicio_ok = verificar_servicio()
    
    # Generar reporte
    generar_reporte(resultados)
    
    # Retornar código de salida
    if all(resultados.values()) and servicio_ok:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
