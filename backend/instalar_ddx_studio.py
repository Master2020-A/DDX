#!/usr/bin/env python3
"""
Script de instalación para DDX Studio
Configura el sistema de módulos personalizados no-code
"""

import os
import sys
import subprocess
from pathlib import Path


def print_header(text):
    """Imprime un encabezado formateado"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60 + "\n")


def print_step(step, text):
    """Imprime un paso numerado"""
    print(f"\n[{step}] {text}")
    print("-" * 60)


def run_command(command, description):
    """Ejecuta un comando y maneja errores"""
    print(f"\n▶ {description}...")
    try:
        result = subprocess.run(
            command, shell=True, check=True, capture_output=True, text=True
        )
        print(f"✅ {description} completado")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error en {description}")
        print(f"   Salida: {e.stdout}")
        print(f"   Error: {e.stderr}")
        return False


def main():
    print_header("🎨 INSTALACIÓN DE DDX STUDIO")
    print("Sistema de Constructor Visual No-Code para DDX Medical")

    # Verificar que estamos en el directorio correcto
    if not os.path.exists("app"):
        print("❌ Error: Este script debe ejecutarse desde el directorio 'backend'")
        sys.exit(1)

    # Paso 1: Verificar archivos
    print_step(1, "Verificando archivos del sistema")

    required_files = [
        "app/models/custom_module.py",
        "app/services/code_generator.py",
        "app/api/ddx_studio.py",
        "migrations/011_add_ddx_studio.sql",
    ]

    missing_files = []
    for file in required_files:
        if os.path.exists(file):
            print(f"  ✅ {file}")
        else:
            print(f"  ❌ {file} - NO ENCONTRADO")
            missing_files.append(file)

    if missing_files:
        print("\n❌ Faltan archivos necesarios. Por favor, verifica la instalación.")
        sys.exit(1)

    # Paso 2: Verificar dependencias Python
    print_step(2, "Verificando dependencias de Python")

    dependencies = ["jinja2"]

    for dep in dependencies:
        try:
            __import__(dep)
            print(f"  ✅ {dep} instalado")
        except ImportError:
            print(f"  ⚠️  {dep} no instalado - instalando...")
            if not run_command(f"pip install {dep}", f"Instalar {dep}"):
                print(f"\n❌ No se pudo instalar {dep}")
                sys.exit(1)

    # Paso 3: Información sobre migración de base de datos
    print_step(3, "Migración de Base de Datos")

    print(
        """
Para aplicar la migración de base de datos, ejecuta:

    psql -U ddx_user -d ddx_db -f migrations/011_add_ddx_studio.sql

O si usas otro usuario/base de datos:

    psql -U <tu_usuario> -d <tu_base_de_datos> -f migrations/011_add_ddx_studio.sql

Esto creará las siguientes tablas:
  • custom_modules       - Módulos personalizados
  • custom_models        - Modelos de datos
  • custom_endpoints     - Endpoints API
  • custom_forms         - Formularios
  • module_deployments   - Historial de despliegues
"""
    )

    response = input("\n¿Ya ejecutaste la migración de base de datos? (s/n): ").lower()
    if response != "s":
        print("\n⚠️  Por favor, ejecuta la migración antes de continuar.")
        print("   Luego vuelve a ejecutar este script.")
        sys.exit(0)

    # Paso 4: Verificar integración en main.py
    print_step(4, "Verificando integración en main.py")

    main_py_path = "app/main.py"
    with open(main_py_path, "r", encoding="utf-8") as f:
        main_content = f.read()

    if "ddx_studio" in main_content:
        print("  ✅ Router de DDX Studio registrado en main.py")
    else:
        print("  ❌ Router de DDX Studio NO encontrado en main.py")
        print("     Por favor, agrega el router manualmente.")
        sys.exit(1)

    # Paso 5: Instrucciones finales
    print_step(5, "Instalación Completada")

    print(
        """
✅ DDX Studio ha sido instalado correctamente!

📋 PRÓXIMOS PASOS:

1. Reiniciar el servidor backend:
   
   uvicorn app.main:app --reload

2. Verificar en Swagger UI:
   
   http://localhost:8612/docs
   
   Buscar sección: 🎨 DDX Studio

3. Acceder desde el frontend:
   
   http://localhost:3000/ddx-studio

4. Crear tu primer módulo personalizado!

📚 DOCUMENTACIÓN:

   Ver archivo: DDX_STUDIO_GUIA_COMPLETA.md

🎯 CASOS DE USO SUGERIDOS:

   • Módulo de Vacunación
   • Módulo de Alergias
   • Módulo de Citas Especializadas
   • Módulo de Certificados Médicos

💡 CARACTERÍSTICAS:

   ✓ Constructor visual de modelos de datos
   ✓ Constructor de endpoints API
   ✓ Generación automática de código
   ✓ Preview en tiempo real
   ✓ Despliegue con un click
   ✓ Versionamiento de módulos

¡Disfruta creando módulos sin código! 🎨
"""
    )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Instalación cancelada por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error inesperado: {e}")
        sys.exit(1)
