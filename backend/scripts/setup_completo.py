"""
Script para ejecutar migraciones y poblar datos
"""
import asyncio
import sys
import subprocess
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

async def main():
    print("\n" + "="*60)
    print("🚀 SETUP COMPLETO - HOSPITALIZACIÓN E INTERCONSULTAS")
    print("="*60 + "\n")
    
    # Ejecutar migraciones
    print("📋 Ejecutando migraciones de Alembic...")
    try:
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            cwd=Path(__file__).parent.parent,
            capture_output=True,
            text=True
        )
        print(result.stdout)
        if result.stderr:
            print("Errores:", result.stderr)
        print("✅ Migraciones ejecutadas\n")
    except Exception as e:
        print(f"⚠️  Error en migraciones: {e}\n")
    
    # Poblar datos
    print("📊 Poblando datos de prueba...")
    from scripts.poblar_hospitalizacion_interconsultas import main as poblar
    await poblar()

if __name__ == "__main__":
    asyncio.run(main())
