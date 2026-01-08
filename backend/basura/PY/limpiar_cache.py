import os
import shutil


def limpiar_cache():
    """Eliminar todos los archivos __pycache__ y .pyc"""
    contador = 0
    for root, dirs, files in os.walk("."):
        # Eliminar directorios __pycache__
        if "__pycache__" in dirs:
            cache_path = os.path.join(root, "__pycache__")
            try:
                shutil.rmtree(cache_path)
                print(f"Eliminado: {cache_path}")
                contador += 1
            except Exception as e:
                print(f"Error eliminando {cache_path}: {e}")

        # Eliminar archivos .pyc
        for file in files:
            if file.endswith(".pyc"):
                pyc_path = os.path.join(root, file)
                try:
                    os.remove(pyc_path)
                    print(f"Eliminado: {pyc_path}")
                    contador += 1
                except Exception as e:
                    print(f"Error eliminando {pyc_path}: {e}")

    print(f"\n✅ Cache limpiado. {contador} elementos eliminados.")


if __name__ == "__main__":
    limpiar_cache()
