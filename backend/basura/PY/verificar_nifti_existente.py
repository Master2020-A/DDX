#!/usr/bin/env python3
"""
Verificar el archivo NIfTI que SÍ existe
"""
from PIL import Image
from pathlib import Path
import numpy as np

nifti_file = Path("uploads/imagenes_medicas/6e715fd3-0370-4b25-8f83-5f79492a4617_20251203_021222_aorta.nii")

print("="*80)
print("🔍 VERIFICANDO ARCHIVO NIFTI EXISTENTE")
print("="*80)
print()

if not nifti_file.exists():
    print(f"❌ Archivo no encontrado: {nifti_file}")
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
        print(f"   Valores min/max: {data.min():.2f}/{data.max():.2f}")
        print(f"   Media: {data.mean():.2f}")
        print(f"   Valores únicos: {len(np.unique(data))}")
        print()
        
        if data.max() == 0:
            print("❌ ARCHIVO VACÍO - Todos los valores son 0")
        else:
            # Mostrar estadísticas de cortes
            for axis_name, axis_idx, slice_func in [
                ('axial', 2, lambda d, i: d[:, :, i]),
                ('sagital', 0, lambda d, i: d[i, :, :]),
                ('coronal', 1, lambda d, i: d[:, i, :])
            ]:
                slice_idx = data.shape[axis_idx] // 2
                slice_2d = slice_func(data, slice_idx)
                
                print(f"📊 Corte {axis_name} central (slice {slice_idx}/{data.shape[axis_idx]}):")
                print(f"   Shape: {slice_2d.shape}")
                print(f"   Min/Max: {slice_2d.min():.2f}/{slice_2d.max():.2f}")
                print(f"   Media: {slice_2d.mean():.2f}")
                print(f"   Desv. std: {slice_2d.std():.2f}")
                print(f"   Valores no-cero: {np.count_nonzero(slice_2d)}/{slice_2d.size}")
                print()
            
            # Intentar generar preview
            print("🖼️ GENERANDO PREVIEW DE PRUEBA...")
            slice_idx = data.shape[2] // 2
            slice_2d = data[:, :, slice_idx]
            
            # Normalizar
            slice_2d = slice_2d.astype(float)
            slice_min = np.min(slice_2d)
            slice_max = np.max(slice_2d)
            
            print(f"   Valores pre-normalización: min={slice_min:.2f}, max={slice_max:.2f}")
            
            if slice_max > slice_min:
                slice_norm = ((slice_2d - slice_min) / (slice_max - slice_min) * 255).astype(np.uint8)
                print(f"   Valores post-normalización: min={slice_norm.min()}, max={slice_norm.max()}")
                
                # Rotar
                slice_norm = np.rot90(slice_norm)
                
                # Convertir a imagen
                pil_img = Image.fromarray(slice_norm, mode='L')
                
                # Guardar para verificación
                test_path = Path("test_preview.png")
                pil_img.save(test_path)
                
                print(f"   ✅ Preview guardado en: {test_path}")
                print(f"   📊 Tamaño del archivo: {test_path.stat().st_size:,} bytes")
            else:
                print(f"   ❌ slice_min == slice_max, imagen sería completamente negra")
        
    except Exception as e:
        print(f"❌ Error procesando NIfTI: {e}")
        import traceback
        traceback.print_exc()

print()
print("="*80)
