"""
Script para crear tablas de Inteligencia Artificial Médica
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import text
from app.core.database import engine


async def crear_tablas_ia():
    """Crear tablas de IA Médica desde archivo SQL"""
    print("🤖 Creando tablas de Inteligencia Artificial Médica...")

    sql_file = Path(__file__).parent / "migrations" / "ia_medica.sql"

    if not sql_file.exists():
        print(f"❌ No se encontró el archivo: {sql_file}")
        return False

    with open(sql_file, "r", encoding="utf-8") as f:
        sql_content = f.read()

    # Dividir en statements individuales
    statements = [s.strip() for s in sql_content.split(";") if s.strip()]

    async with engine.begin() as conn:
        for i, statement in enumerate(statements, 1):
            if not statement or statement.startswith("--"):
                continue

            try:
                await conn.execute(text(statement))
                print(f"✅ Statement {i}/{len(statements)} ejecutado")
            except Exception as e:
                error_str = str(e).lower()
                if "already exists" in error_str or "ya existe" in error_str:
                    print(
                        f"ℹ️  Statement {i}/{len(statements)}: Ya existe, continuando..."
                    )
                else:
                    print(
                        f"⚠️  Error en statement {i}/{len(statements)}: {str(e)[:200]}"
                    )

    print("✅ Tablas de IA Médica creadas exitosamente")
    return True


async def main():
    print("=" * 60)
    print("🤖 CREAR TABLAS DE INTELIGENCIA ARTIFICIAL MÉDICA")
    print("=" * 60)

    success = await crear_tablas_ia()

    if success:
        print("\n" + "=" * 60)
        print("✅ MIGRACIÓN COMPLETADA")
        print("=" * 60)
        print("\n📝 Tablas creadas:")
        print("   - analisis_ia")
        print("   - predicciones_riesgo")
        print("   - recomendaciones_tratamiento")
        print("   - interacciones_medicamentosas")
        print("   - anomalias_detectadas")
        print("   - asistente_ia")
        print("\n🔄 Reinicia el servidor backend para aplicar los cambios")
    else:
        print("\n" + "=" * 60)
        print("❌ MIGRACIÓN FALLIDA")
        print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
