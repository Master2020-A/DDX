"""
Script para verificar que las variables de entorno se cargan correctamente
"""

import os
from pathlib import Path

# Verificar ruta del .env
env_path = Path(__file__).parent / ".env"
print(f"Buscando .env en: {env_path}")
print(f"¿Existe el archivo? {env_path.exists()}")

if env_path.exists():
    print(f"\nContenido del .env (primeras líneas):")
    with open(env_path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            if i <= 20:  # Solo primeras 20 líneas
                # Ocultar valores sensibles
                if "API_KEY" in line or "SECRET" in line or "PASSWORD" in line:
                    parts = line.split("=", 1)
                    if len(parts) == 2:
                        key = parts[0]
                        value = parts[1].strip()
                        if value:
                            masked = (
                                value[:7] + "..." + value[-4:]
                                if len(value) > 11
                                else "***"
                            )
                            print(f"{i:3}: {key}={masked}")
                        else:
                            print(f"{i:3}: {key}=(vacío)")
                else:
                    print(f"{i:3}: {line.rstrip()}")

print("\n" + "=" * 60)
print("Cargando configuración con pydantic-settings...")
print("=" * 60)

try:
    from app.core.config import settings

    print(f"\n✅ Configuración cargada exitosamente")
    print(f"\nOPENAI_API_KEY configurada: {bool(settings.OPENAI_API_KEY)}")

    if settings.OPENAI_API_KEY:
        key = settings.OPENAI_API_KEY
        masked = key[:7] + "..." + key[-4:] if len(key) > 11 else "***"
        print(f"OPENAI_API_KEY: {masked}")
        print(f"Longitud de la key: {len(key)} caracteres")
    else:
        print("❌ OPENAI_API_KEY está vacía")

    print(f"\nOPENAI_MODEL: {settings.OPENAI_MODEL}")
    print(f"DATABASE_URL: {settings.DATABASE_URL[:30]}...")

except Exception as e:
    print(f"❌ Error al cargar configuración: {e}")
    import traceback

    traceback.print_exc()

print("\n" + "=" * 60)
print("Probando cliente OpenAI...")
print("=" * 60)

try:
    from openai import OpenAI
    from app.core.config import settings

    if not settings.OPENAI_API_KEY:
        print("❌ No se puede probar: OPENAI_API_KEY vacía")
    else:
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        print("✅ Cliente OpenAI creado exitosamente")

        # Intentar una llamada simple
        print("\nProbando llamada a la API...")
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Di 'test exitoso'"}],
            max_tokens=10,
        )
        print(f"✅ API funcionando: {response.choices[0].message.content}")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback

    traceback.print_exc()
