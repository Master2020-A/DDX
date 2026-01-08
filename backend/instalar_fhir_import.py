#!/usr/bin/env python3
"""
Script de instalación para el sistema de importación FHIR
Instala las dependencias necesarias para conectar con servidores FHIR externos
"""
import subprocess
import sys


def install_package(package):
    """Instalar un paquete usando pip"""
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])


def main():
    print("=" * 60)
    print("INSTALACIÓN DE DEPENDENCIAS PARA IMPORTACIÓN FHIR")
    print("=" * 60)
    print()

    packages = [
        "httpx",  # Cliente HTTP asíncrono para conectar con servidores FHIR
    ]

    print("Instalando dependencias necesarias...")
    print()

    for package in packages:
        try:
            print(f"📦 Instalando {package}...")
            install_package(package)
            print(f"✅ {package} instalado correctamente")
            print()
        except Exception as e:
            print(f"❌ Error instalando {package}: {str(e)}")
            print()

    print("=" * 60)
    print("✅ INSTALACIÓN COMPLETADA")
    print("=" * 60)
    print()
    print("SIGUIENTE PASO:")
    print("1. Ejecutar migración de base de datos:")
    print("   psql -U ddx_user -d ddx_db -f migrations/010_add_fhir_conditions.sql")
    print()
    print("2. Reiniciar el servidor backend:")
    print("   uvicorn app.main:app --reload")
    print()
    print("3. Acceder a la interfaz de importación:")
    print("   Dashboard → Importar desde FHIR")
    print()
    print("SERVIDORES FHIR PÚBLICOS DE PRUEBA:")
    print("- HAPI FHIR R4: https://hapi.fhir.org/baseR4")
    print("- SMART Health IT: https://launch.smarthealthit.org/v/r4/fhir")
    print()


if __name__ == "__main__":
    main()
