#!/usr/bin/env python3
"""
Ver contenido de un PNG generado
"""
from PIL import Image
from pathlib import Path
import numpy as np

# Verificar el PNG más reciente
png_file = Path("uploads/imagenes_medicas/previews/e0c451e4-ec10-41aa-a8a3-114a8945c76c/6e715fd3-0370-4b25-8f83-5f79492a4617_20251203_015536_aorta_axial.png")

print("="*80)
print("🔍 VERIFICANDO CONTENIDO DEL PNG")
print("="*80)
print()

if not png_file.exists():
    print(f"❌ Archivo no encontrado: {png_file}")
else:
    print(f"📄 Archivo: {png_file.name}")
    print(f"📊 Tamaño: {png_file.stat().st_size} bytes")
    print()
    
    try:
        # Intentar abrir como imagen
        img = Image.open(png_file)
        print(f"✅ Archivo PNG válido")
        print(f"   Dimensiones: {img.size}")
        print(f"   Modo: {img.mode}")
        
        # Convertir a array numpy
        arr = np.array(img)
        print(f"   Array shape: {arr.shape}")
        print(f"   Valores min/max: {arr.min()}/{arr.max()}")
        print(f"   Valores únicos: {len(np.unique(arr))}")
        
        if len(np.unique(arr)) == 1:
            print()
            print("⚠️ LA IMAGEN ESTÁ COMPLETAMENTE NEGRA O BLANCA")
            print("   Todos los píxeles tienen el mismo valor")
        
    except Exception as e:
        print(f"❌ Error abriendo PNG: {e}")

print()
print("="*80)
print("🔍 VERIFICANDO ARCHIVO NIFTI ORIGINAL")
print("="*80)
print()

nifti_file = Path("uploads/imagenes_medicas/6e715fd3-0370-4b25-8f83-5f79492a4617_20251203_015536_aorta.nii")

if not nifti_file.exists():
    print(f"❌ Archivo NIfTI no encontrado: {nifti_file}")
else:
    print(f"📄 Archivo: {nifti_file.name}")
    print(f"📊 Tamaño: {nifti_file.stat().st_size:,} bytes")
    print()
    
    try:
        import nibabel as nib
        
        print("📥 Cargando archivo NIfTI...")
        img = nib.load(str(nifti_file))
        data = img.get_fdata()
        
        print(f"✅ Archivo NIfTI válido")
        print(f"   Dimensiones: {data.shape}")
        print(f"   Tipo de dato: {data.dtype}")
        print(f"   Valores min/max: {data.min()}/{data.max()}")
        print(f"   Media: {data.mean()}")
        print(f"   Valores únicos: {len(np.unique(data))}")
        
        if len(np.unique(data)) == 1:
            print()
            print("⚠️ EL ARCHIVO NIFTI ESTÁ VACÍO")
            print("   Todos los voxels tienen el mismo valor")
        else:
            # Mostrar estadísticas de un corte central
            slice_idx = data.shape[2] // 2
            slice_2d = data[:, :, slice_idx]
            print()
            print(f"📊 Estadísticas corte axial central (slice {slice_idx}):")
            print(f"   Min/Max: {slice_2d.min()}/{slice_2d.max()}")
            print(f"   Media: {slice_2d.mean()}")
            print(f"   Desv. std: {slice_2d.std()}")
        
    except Exception as e:
        print(f"❌ Error procesando NIfTI: {e}")
        import traceback
        traceback.print_exc()

print()
print("="*80)
