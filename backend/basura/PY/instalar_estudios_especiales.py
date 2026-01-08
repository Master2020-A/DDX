"""
Script de instalación para el sistema de estudios especiales (EKG, EEG, Ecografías)
"""
import subprocess
import sys
import os

def main():
    print("=" * 70)
    print("🏥 INSTALACIÓN - SISTEMA DE ESTUDIOS ESPECIALES")
    print("=" * 70)
    print()
    
    print("Este script configurará:")
    print("  ✅ Modelos de base de datos (EKG, EEG, Ecografías)")
    print("  ✅ Servicios de interpretación automática")
    print("  ✅ Endpoints API")
    print()
    
    # Paso 1: Verificar que estamos en el directorio correcto
    if not os.path.exists("app"):
        print("❌ Error: Debe ejecutar este script desde el directorio backend/")
        sys.exit(1)
    
    print("📋 PASO 1: Verificando archivos creados...")
    archivos_requeridos = [
        "app/models/estudios_especiales.py",
        "app/services/interpretador_ekg.py",
        "app/services/interpretador_eeg.py",
        "app/services/interpretador_ecografia.py",
        "app/api/estudios_especiales.py"
    ]
    
    archivos_faltantes = []
    for archivo in archivos_requeridos:
        if os.path.exists(archivo):
            print(f"  ✅ {archivo}")
        else:
            print(f"  ❌ {archivo} - FALTANTE")
            archivos_faltantes.append(archivo)
    
    if archivos_faltantes:
        print()
        print("❌ Error: Faltan archivos requeridos. Por favor, créelos primero.")
        sys.exit(1)
    
    print()
    print("📋 PASO 2: Registrando modelos en __init__.py...")
    
    # Leer el archivo __init__.py
    init_file = "app/models/__init__.py"
    with open(init_file, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    # Verificar si ya están importados
    if "from app.models.estudios_especiales import" not in contenido:
        # Agregar imports
        linea_import = "\nfrom app.models.estudios_especiales import EstudioEKG, EstudioEEG, Ecografia\n"
        
        # Buscar la última línea de import
        lineas = contenido.split('\n')
        ultima_import = 0
        for i, linea in enumerate(lineas):
            if linea.startswith('from app.models.'):
                ultima_import = i
        
        # Insertar después de la última importación
        lineas.insert(ultima_import + 1, linea_import.strip())
        
        # Guardar
        with open(init_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lineas))
        
        print("  ✅ Modelos registrados en __init__.py")
    else:
        print("  ℹ️  Modelos ya están registrados")
    
    print()
    print("📋 PASO 3: Registrando rutas en main.py...")
    
    # Leer el archivo main.py
    main_file = "app/main.py"
    with open(main_file, 'r', encoding='utf-8') as f:
        contenido_main = f.read()
    
    # Verificar si ya está importado
    if "from app.api import estudios_especiales" not in contenido_main:
        # Buscar la sección de imports de API
        lineas_main = contenido_main.split('\n')
        
        # Encontrar dónde agregar el import
        for i, linea in enumerate(lineas_main):
            if "from app.api import" in linea:
                lineas_main.insert(i + 1, "from app.api import estudios_especiales")
                break
        
        # Encontrar dónde agregar el router
        for i, linea in enumerate(lineas_main):
            if "app.include_router(" in linea:
                # Insertar después de los otros routers
                lineas_main.insert(i + 1, "app.include_router(estudios_especiales.router)")
                break
        
        # Guardar
        with open(main_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lineas_main))
        
        print("  ✅ Rutas registradas en main.py")
    else:
        print("  ℹ️  Rutas ya están registradas")
    
    print()
    print("📋 PASO 4: Creando migración de base de datos...")
    print()
    print("  Ejecute los siguientes comandos:")
    print()
    print("  1. Crear migración:")
    print("     alembic revision --autogenerate -m \"Agregar estudios especiales (EKG, EEG, Ecografías)\"")
    print()
    print("  2. Aplicar migración:")
    print("     alembic upgrade head")
    print()
    
    respuesta = input("¿Desea crear la migración ahora? (s/n): ").lower()
    
    if respuesta == 's':
        try:
            print()
            print("  Creando migración...")
            subprocess.run([
                "alembic", "revision", "--autogenerate",
                "-m", "Agregar estudios especiales (EKG, EEG, Ecografías)"
            ], check=True)
            
            print()
            print("  Aplicando migración...")
            subprocess.run(["alembic", "upgrade", "head"], check=True)
            
            print()
            print("  ✅ Migración completada")
        except subprocess.CalledProcessError as e:
            print(f"  ❌ Error al ejecutar migración: {e}")
            print("  Por favor, ejecute los comandos manualmente")
    else:
        print("  ℹ️  Recuerde ejecutar los comandos de migración manualmente")
    
    print()
    print("=" * 70)
    print("✅ INSTALACIÓN COMPLETADA")
    print("=" * 70)
    print()
    print("📋 PRÓXIMOS PASOS:")
    print()
    print("  1. Si no ejecutó la migración, hágalo ahora:")
    print("     alembic revision --autogenerate -m \"Agregar estudios especiales\"")
    print("     alembic upgrade head")
    print()
    print("  2. Reinicie el servidor:")
    print("     uvicorn app.main:app --reload --port 8612")
    print()
    print("  3. Verifique los endpoints en:")
    print("     http://localhost:8612/docs")
    print()
    print("  4. Endpoints disponibles:")
    print("     POST   /api/estudios-especiales/ekg")
    print("     GET    /api/estudios-especiales/ekg/paciente/{paciente_id}")
    print("     POST   /api/estudios-especiales/eeg")
    print("     GET    /api/estudios-especiales/eeg/paciente/{paciente_id}")
    print("     POST   /api/estudios-especiales/ecografia")
    print("     GET    /api/estudios-especiales/ecografia/paciente/{paciente_id}")
    print("     GET    /api/estudios-especiales/paciente/{paciente_id}/resumen")
    print()
    print("📖 Documentación completa en:")
    print("   SISTEMA_ESTUDIOS_ESPECIALES.md")
    print()

if __name__ == "__main__":
    main()
