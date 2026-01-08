#!/usr/bin/env python3
"""Test de carga de variables de entorno"""
import os
from pathlib import Path

print("=" * 60)
print("TEST DE VARIABLES DE ENTORNO")
print("=" * 60)

# Cargar .env manualmente
env_path = Path(__file__).parent / '.env'
print(f"\n📁 Archivo .env: {env_path}")
print(f"   ¿Existe? {env_path.exists()}")

if env_path.exists():
    print(f"\n📄 Contenido del .env:")
    with open(env_path, 'r') as f:
        lines = f.readlines()
        for i, line in enumerate(lines[:10], 1):  # Primeras 10 líneas
            if 'OPENAI_API_KEY' in line:
                # Mostrar solo inicio de la key
                if '=' in line:
                    key_part = line.split('=')[1].strip()[:20]
                    print(f"   Línea {i}: OPENAI_API_KEY={key_part}...")
            elif line.strip() and not line.startswith('#'):
                print(f"   Línea {i}: {line.strip()[:50]}")

# Intentar cargar con python-dotenv
print("\n" + "=" * 60)
print("CARGANDO CON python-dotenv")
print("=" * 60)

try:
    from dotenv import load_dotenv
    print("\n✅ python-dotenv disponible")
    
    # Cargar .env
    load_dotenv(env_path)
    print("✅ .env cargado")
    
    # Verificar API key
    api_key = os.getenv('OPENAI_API_KEY')
    if api_key:
        print(f"\n✅ OPENAI_API_KEY encontrada (longitud: {len(api_key)})")
        print(f"   Primeros 20 caracteres: {api_key[:20]}...")
    else:
        print("\n❌ OPENAI_API_KEY NO encontrada después de cargar .env")
        
except ImportError:
    print("\n⚠️ python-dotenv NO está instalado")
    print("   Instala con: pip install python-dotenv")

print("\n" + "=" * 60)
