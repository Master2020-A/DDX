"""
Script para forzar recarga completa del backend
Elimina todos los archivos .pyc y directorios __pycache__
"""

import os
import shutil
import sys


def limpiar_cache():
    contador = 0
    for root, dirs, files in os.walk("."):
        if "__pycache__" in dirs:
            cache_path = os.path.join(root, "__pycache__")
            try:
                shutil.rmtree(cache_path)
                print(f"✓ Eliminado: {cache_path}")
                contador += 1
            except Exception as e:
                print(f"✗ Error: {cache_path} - {e}")

        for file in files:
            if file.endswith(".pyc"):
                pyc_path = os.path.join(root, file)
                try:
                    os.remove(pyc_path)
                    print(f"✓ Eliminado: {pyc_path}")
                    contador += 1
                except Exception as e:
                    print(f"✗ Error: {pyc_path} - {e}")

    print(f"\n{'='*60}")
    print(f"✅ Limpieza completada: {contador} archivos eliminados")
    print(f"{'='*60}\n")
    print("AHORA EJECUTA:")
    print("  python -B -m uvicorn app.main:app --reload --port 8612")
    print("\nEl flag -B evita crear nuevos archivos .pyc")


if __name__ == "__main__":
    print(f"\n{'='*60}")
    print("LIMPIANDO CACHÉ DE PYTHON")
    print(f"{'='*60}\n")
    limpiar_cache()
