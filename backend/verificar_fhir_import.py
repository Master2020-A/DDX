#!/usr/bin/env python3
"""
Script de verificación para el sistema de importación FHIR
Verifica que todos los componentes estén correctamente instalados
"""
import sys
import importlib


def check_module(module_name, description):
    """Verificar si un módulo se puede importar"""
    try:
        importlib.import_module(module_name)
        print(f"✅ {description}: OK")
        return True
    except ImportError as e:
        print(f"❌ {description}: ERROR - {str(e)}")
        return False
    except Exception as e:
        print(f"⚠️  {description}: WARNING - {str(e)}")
        return False


def main():
    print("=" * 60)
    print("VERIFICACIÓN DEL SISTEMA DE IMPORTACIÓN FHIR")
    print("=" * 60)
    print()

    all_ok = True

    # Verificar dependencias
    print("1. Verificando dependencias...")
    all_ok &= check_module("httpx", "httpx (Cliente HTTP)")
    print()

    # Verificar modelos
    print("2. Verificando modelos...")
    all_ok &= check_module("app.models.fhir_condition", "Modelo FHIRCondition")
    print()

    # Verificar servicios
    print("3. Verificando servicios...")
    all_ok &= check_module("app.services.fhir_client", "Cliente FHIR")
    all_ok &= check_module(
        "app.services.fhir_condition_importer", "Importador de Conditions"
    )
    print()

    # Verificar API
    print("4. Verificando API...")
    all_ok &= check_module("app.api.fhir_import", "Router FHIR Import")
    print()

    # Verificar que el router se puede importar correctamente
    print("5. Verificando router...")
    try:
        from app.api.fhir_import import router

        print(f"✅ Router tiene {len(router.routes)} rutas registradas")
        print()
        print("Rutas disponibles:")
        for route in router.routes:
            if hasattr(route, "path") and hasattr(route, "methods"):
                methods = ", ".join(route.methods) if route.methods else "GET"
                print(f"   {methods:10} {route.path}")
        print()
    except Exception as e:
        print(f"❌ Error al verificar router: {str(e)}")
        all_ok = False
        print()

    print("=" * 60)
    if all_ok:
        print("✅ VERIFICACIÓN COMPLETADA - TODO OK")
        print()
        print("SIGUIENTE PASO:")
        print("1. Ejecutar migración de base de datos:")
        print("   psql -U ddx_user -d ddx_db -f migrations/010_add_fhir_conditions.sql")
        print()
        print("2. REINICIAR el servidor backend:")
        print("   Ctrl+C para detener el servidor actual")
        print("   uvicorn app.main:app --reload")
        print()
        print("3. Verificar que el endpoint esté disponible:")
        print("   http://localhost:8612/docs")
        print("   Buscar: 📥 FHIR Import")
    else:
        print("❌ VERIFICACIÓN FALLÓ - HAY ERRORES")
        print()
        print("Instalar dependencias faltantes:")
        print("   pip install httpx")
    print("=" * 60)

    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
