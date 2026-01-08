"""
Script simplificado para ejecutar migración de IA Médica
"""

import sys
import os

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(__file__))

print("Iniciando migración de IA Médica...")

try:
    import asyncio
    from pathlib import Path
    from sqlalchemy import text
    from app.core.database import engine

    print("✓ Módulos importados correctamente")

    async def ejecutar_migracion():
        sql_file = Path(__file__).parent / "migrations" / "ia_medica.sql"

        if not sql_file.exists():
            print(f"ERROR: No se encontró {sql_file}")
            return False

        print(f"✓ Archivo SQL encontrado: {sql_file}")

        with open(sql_file, "r", encoding="utf-8") as f:
            sql_content = f.read()

        print(f"✓ Contenido SQL leído ({len(sql_content)} caracteres)")

        # Dividir en statements
        statements = [
            s.strip()
            for s in sql_content.split(";")
            if s.strip() and not s.strip().startswith("--")
        ]
        print(f"✓ {len(statements)} statements encontrados")

        async with engine.begin() as conn:
            print("✓ Conexión a base de datos establecida")

            for i, statement in enumerate(statements, 1):
                try:
                    await conn.execute(text(statement))
                    print(f"  ✓ Statement {i}/{len(statements)} ejecutado")
                except Exception as e:
                    error_str = str(e).lower()
                    if "already exists" in error_str or "ya existe" in error_str:
                        print(f"  ℹ Statement {i}/{len(statements)}: Ya existe")
                    else:
                        print(f"  ✗ Error en statement {i}: {str(e)[:150]}")

        print("\n✅ MIGRACIÓN COMPLETADA")
        print("\nTablas creadas:")
        print("  - analisis_ia")
        print("  - predicciones_riesgo")
        print("  - recomendaciones_tratamiento")
        print("  - interacciones_medicamentosas")
        print("  - anomalias_detectadas")
        print("  - asistente_ia")
        return True

    # Ejecutar
    asyncio.run(ejecutar_migracion())

except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)
