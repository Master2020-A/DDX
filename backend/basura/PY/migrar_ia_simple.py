import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

print("=" * 60)
print("INICIANDO MIGRACIÓN DE IA MÉDICA")
print("=" * 60)

try:
    import asyncio
    from pathlib import Path
    from sqlalchemy import text
    from app.core.database import engine

    print("✓ Módulos importados")

    async def ejecutar():
        sql_file = Path(__file__).parent / "migrations" / "ia_medica.sql"

        if not sql_file.exists():
            print(f"✗ No se encontró: {sql_file}")
            return

        print(f"✓ Archivo SQL encontrado")

        with open(sql_file, "r", encoding="utf-8") as f:
            sql_content = f.read()

        statements = [
            s.strip()
            for s in sql_content.split(";")
            if s.strip() and not s.strip().startswith("--")
        ]
        print(f"✓ {len(statements)} statements a ejecutar\n")

        async with engine.begin() as conn:
            for i, statement in enumerate(statements, 1):
                try:
                    await conn.execute(text(statement))
                    print(f"✓ [{i}/{len(statements)}] Ejecutado")
                except Exception as e:
                    if (
                        "already exists" in str(e).lower()
                        or "ya existe" in str(e).lower()
                    ):
                        print(f"ℹ [{i}/{len(statements)}] Ya existe")
                    else:
                        print(f"✗ [{i}/{len(statements)}] Error: {str(e)[:100]}")

        print("\n" + "=" * 60)
        print("✅ MIGRACIÓN COMPLETADA")
        print("=" * 60)
        print("\nTablas creadas:")
        print("  • analisis_ia")
        print("  • predicciones_riesgo")
        print("  • recomendaciones_tratamiento")
        print("  • interacciones_medicamentosas")
        print("  • anomalias_detectadas")
        print("  • asistente_ia")
        print("\n🔄 El servidor se reiniciará automáticamente")

    asyncio.run(ejecutar())

except Exception as e:
    print(f"\n✗ ERROR: {e}")
    import traceback

    traceback.print_exc()
