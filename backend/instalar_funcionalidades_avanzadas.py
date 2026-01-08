"""
Script de instalación para funcionalidades avanzadas de workflows
"""

import subprocess
import sys
import os


def install_package(package):
    """Instalar un paquete de Python"""
    print(f"Instalando {package}...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✓ {package} instalado correctamente")
        return True
    except subprocess.CalledProcessError:
        print(f"✗ Error al instalar {package}")
        return False


def main():
    print("=" * 60)
    print("INSTALACIÓN DE FUNCIONALIDADES AVANZADAS DE WORKFLOWS")
    print("=" * 60)
    print()

    # Paquetes requeridos
    packages = [
        # WebSockets para colaboración
        "websockets",
        # Proveedores de LLM
        "openai",
        "anthropic",
        "google-generativeai",
        "cohere",
        # Utilidades
        "python-multipart",  # Para upload de archivos
        "aiofiles",  # Para operaciones async de archivos
    ]

    print("Instalando dependencias de Python...")
    print()

    failed = []
    for package in packages:
        if not install_package(package):
            failed.append(package)

    print()
    print("=" * 60)

    if failed:
        print("⚠ INSTALACIÓN COMPLETADA CON ERRORES")
        print()
        print("Los siguientes paquetes no se pudieron instalar:")
        for package in failed:
            print(f"  - {package}")
        print()
        print("Intenta instalarlos manualmente:")
        print(f"  pip install {' '.join(failed)}")
    else:
        print("✓ INSTALACIÓN COMPLETADA EXITOSAMENTE")
        print()
        print("Todas las dependencias se instalaron correctamente.")

    print()
    print("=" * 60)
    print("PRÓXIMOS PASOS")
    print("=" * 60)
    print()
    print("1. Configurar variables de entorno (.env):")
    print("   OPENAI_API_KEY=sk-...")
    print("   ANTHROPIC_API_KEY=sk-ant-...")
    print("   GOOGLE_API_KEY=...")
    print("   COHERE_API_KEY=...")
    print()
    print("2. Ejecutar migraciones SQL en PostgreSQL:")
    print("   psql -U postgres -d ddx -f migracion_workflows_avanzados.sql")
    print("   psql -U postgres -d ddx -f migracion_marketplace.sql")
    print("   psql -U postgres -d ddx -f migracion_colaboracion.sql")
    print()
    print("3. Actualizar main.py para registrar los nuevos routers")
    print()
    print("4. Reiniciar el servidor backend:")
    print("   python -m uvicorn app.main:app --reload --port 8612")
    print()
    print("=" * 60)


if __name__ == "__main__":
    main()
