#!/usr/bin/env python3
"""Test de importación del procesador y analizador IA"""
import sys
sys.path.insert(0, r'C:\Users\Master\Documents\DDX\backend')

print("=" * 60)
print("TEST DE IMPORTACIONES")
print("=" * 60)

# Test 1: Procesador
try:
    print("\n1. Importando ProcesadorArchivosMedicos...")
    from app.services.procesador_archivos_medicos import ProcesadorArchivosMedicos
    print("   ✅ ProcesadorArchivosMedicos importado")
except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()

# Test 2: Analizador IA
try:
    print("\n2. Importando AnalizadorECGIA...")
    from app.services.analizador_ecg_ia import AnalizadorECGIA
    print("   ✅ AnalizadorECGIA importado")
except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()

# Test 3: Crear instancia
try:
    print("\n3. Creando instancia de AnalizadorECGIA...")
    import os
    api_key = os.getenv('OPENAI_API_KEY')
    if api_key:
        print(f"   ✅ API Key encontrada (longitud: {len(api_key)})")
        analizador = AnalizadorECGIA(api_key=api_key)
        print("   ✅ Instancia creada exitosamente")
    else:
        print("   ⚠️ API Key no encontrada en entorno")
except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("TEST COMPLETADO")
print("=" * 60)
