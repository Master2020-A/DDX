"""Script para corregir tipos ENUM faltantes en API Pública"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import text
from app.core.database import engine


async def fix_enums():
    """Agregar tipos ENUM faltantes"""
    print("🔧 Corrigiendo tipos ENUM para API Pública...")

    statements = [
        # Crear tipo ENUM para TipoEvento
        """
        DO $$ BEGIN
            CREATE TYPE tipoevento AS ENUM (
                'paciente.creado',
                'paciente.actualizado',
                'paciente.eliminado',
                'consulta.creada',
                'consulta.actualizada',
                'consulta.finalizada',
                'laboratorio.creado',
                'laboratorio.completado',
                'factura.generada',
                'factura.timbrada',
                'cita.creada',
                'cita.cancelada'
            );
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
        """,
        # Crear tipo ENUM para EstadoPlugin
        """
        DO $$ BEGIN
            CREATE TYPE estadoplugin AS ENUM (
                'pendiente',
                'en_revision',
                'aprobado',
                'rechazado',
                'suspendido',
                'obsoleto'
            );
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
        """,
        # Convertir columna estado a ENUM
        """
        DO $$ 
        BEGIN
            IF EXISTS (
                SELECT 1 
                FROM information_schema.columns 
                WHERE table_name = 'plugins' 
                AND column_name = 'estado' 
                AND data_type = 'character varying'
            ) THEN
                ALTER TABLE plugins 
                ALTER COLUMN estado TYPE estadoplugin 
                USING estado::estadoplugin;
            END IF;
        END $$;
        """,
    ]

    async with engine.begin() as conn:
        for i, statement in enumerate(statements, 1):
            try:
                await conn.execute(text(statement))
                print(f"✅ Statement {i}/3 ejecutado correctamente")
            except Exception as e:
                error_str = str(e).lower()
                if (
                    "already exists" in error_str
                    or "ya existe" in error_str
                    or "duplicate" in error_str
                ):
                    print(f"ℹ️  Statement {i}/3: Tipo ya existe, continuando...")
                else:
                    print(f"⚠️  Error en statement {i}/3: {str(e)[:200]}")

    print("✅ Tipos ENUM procesados exitosamente")
    return True


async def main():
    print("=" * 60)
    print("🔧 CORREGIR TIPOS ENUM DE API PÚBLICA")
    print("=" * 60)

    success = await fix_enums()

    if success:
        print("\n" + "=" * 60)
        print("✅ CORRECCIÓN COMPLETADA")
        print("=" * 60)
        print("\n📝 Reinicia el servidor backend para aplicar los cambios")
    else:
        print("\n" + "=" * 60)
        print("❌ CORRECCIÓN FALLIDA")
        print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
