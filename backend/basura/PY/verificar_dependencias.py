#!/usr/bin/env python3
"""Verificar versiones de dependencias críticas"""
import sys

print("=" * 60)
print("VERIFICACIÓN DE DEPENDENCIAS")
print("=" * 60)

# OpenAI
try:
    import openai
    print(f"\n✅ OpenAI: {openai.__version__}")
    print(f"   Ubicación: {openai.__file__}")
except Exception as e:
    print(f"\n❌ OpenAI: {e}")

# httpx
try:
    import httpx
    print(f"\n✅ httpx: {httpx.__version__}")
    print(f"   Ubicación: {httpx.__file__}")
except Exception as e:
    print(f"\n❌ httpx: {e}")

# httpcore
try:
    import httpcore
    print(f"\n✅ httpcore: {httpcore.__version__}")
    print(f"   Ubicación: {httpcore.__file__}")
except Exception as e:
    print(f"\n❌ httpcore: {e}")

# Probar crear cliente OpenAI
print("\n" + "=" * 60)
print("PRUEBA DE INICIALIZACIÓN")
print("=" * 60)

try:
    import os
    api_key = os.getenv('OPENAI_API_KEY')
    if api_key:
        print(f"\n✅ API Key encontrada (longitud: {len(api_key)})")
        print("\n🔧 Intentando crear cliente OpenAI...")
        client = openai.OpenAI(api_key=api_key)
        print("✅ Cliente creado exitosamente")
    else:
        print("\n⚠️ API Key no encontrada")
except Exception as e:
    print(f"\n❌ Error creando cliente: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
