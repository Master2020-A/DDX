#!/usr/bin/env python3
"""
Verificar estado del procesador NIfTI en el backend
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

print("="*80)
print("🔍 VERIFICACIÓN: Procesador NIfTI en Backend")
print("="*80)
print()

# 1. Verificar importación de nibabel
print("1️⃣ Verificando nibabel...")
try:
    import nibabel as nib
    print(f"   ✅ nibabel importado correctamente (versión: {nib.__version__})")
except ImportError as e:
    print(f"   ❌ Error importando nibabel: {e}")
    print("   💡 Solución: pip install nibabel")
    sys.exit(1)

print()

# 2. Verificar procesador NIfTI
print("2️⃣ Verificando procesador NIfTI...")
try:
    from app.services.nifti_processor import get_nifti_processor
    processor = get_nifti_processor()
    print("   ✅ Procesador NIfTI disponible")
except Exception as e:
    print(f"   ❌ Error cargando procesador: {e}")
    sys.exit(1)

print()

# 3. Probar con archivo de prueba
print("3️⃣ Probando con archivo NIfTI...")
test_file = r"C:\Users\Master\Documents\DDX\TotalsegmentatorMRI_dataset_v200\s0298\segmentations\aorta.nii"

if Path(test_file).exists():
    print(f"   📁 Archivo encontrado: {test_file}")
    print(f"   📊 Tamaño: {Path(test_file).stat().st_size / 1024 / 1024:.2f} MB")
    
    try:
        # Intentar cargar
        print("   📥 Cargando archivo...")
        img = nib.load(test_file)
        print(f"   ✅ Archivo cargado exitosamente")
        
        # Obtener información
        data = img.get_fdata()
        print(f"   📐 Dimensiones: {data.shape}")
        print(f"   🔢 Tipo de dato: {data.dtype}")
        
        # Extraer metadatos
        print("   📋 Extrayendo metadatos...")
        metadatos = processor.extraer_metadatos(test_file)
        if 'error' not in metadatos:
            print("   ✅ Metadatos extraídos correctamente")
            print(f"      - Dimensiones: {metadatos.get('dimensiones')}")
            print(f"      - Es 3D: {metadatos.get('es_3d')}")
            print(f"      - Voxel dims: {metadatos.get('voxel_dims')}")
        else:
            print(f"   ⚠️ Error en metadatos: {metadatos['error']}")
        
        # Generar preview
        print("   🖼️ Generando preview...")
        preview = processor.generar_preview_2d(test_file, eje='axial')
        if preview:
            print(f"   ✅ Preview generado ({len(preview)} bytes)")
        else:
            print("   ⚠️ No se pudo generar preview")
            
    except Exception as e:
        print(f"   ❌ Error procesando archivo: {e}")
        import traceback
        traceback.print_exc()
else:
    print(f"   ❌ Archivo no encontrado: {test_file}")
    print("   💡 Verifica la ruta del archivo")

print()
print("="*80)
print("✅ VERIFICACIÓN COMPLETADA")
print("="*80)
print()
print("📌 CONCLUSIÓN:")
print("   Si todos los pasos anteriores están ✅, el backend debería funcionar.")
print("   Si hay ❌, revisa los errores específicos arriba.")
print()
print("🔍 PARA VER LOGS DEL BACKEND:")
print("   Revisa la terminal donde está corriendo uvicorn")
print("   Busca mensajes de error después de intentar subir")
print()
