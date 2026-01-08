#!/usr/bin/env python3
"""
Verificar que los archivos PNG realmente existen
"""
from pathlib import Path
import os

print("="*80)
print("🔍 VERIFICANDO ARCHIVOS PNG GENERADOS")
print("="*80)
print()

# Buscar todos los archivos PNG en previews
preview_dir = Path("uploads/imagenes_medicas/previews")

if not preview_dir.exists():
    print(f"❌ Directorio de previews no existe: {preview_dir}")
else:
    print(f"✅ Directorio de previews existe: {preview_dir.absolute()}")
    print()
    
    # Listar todos los archivos
    png_files = list(preview_dir.rglob("*.png"))
    
    print(f"📊 Encontrados {len(png_files)} archivos PNG")
    print()
    
    for png_file in png_files:
        print(f"📄 {png_file.name}")
        print(f"   Ruta completa: {png_file.absolute()}")
        print(f"   Tamaño: {png_file.stat().st_size:,} bytes")
        print(f"   Ruta relativa: {png_file.relative_to('uploads')}")
        print(f"   URL esperada: /uploads/{png_file.relative_to('uploads').as_posix()}")
        print()

print("="*80)
