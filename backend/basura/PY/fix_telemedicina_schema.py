# fix_telemedicina_schema.py

import asyncio
from sqlalchemy import text
from app.core.database import engine


async def main():
    async with engine.begin() as conn:
        # Agregar columnas faltantes si no existen
        await conn.execute(
            text(
                """
            ALTER TABLE consultas_remotas
            ADD COLUMN IF NOT EXISTS token_sala VARCHAR(255);
        """
            )
        )

        await conn.execute(
            text(
                """
            ALTER TABLE consultas_remotas
            ADD COLUMN IF NOT EXISTS url_sala_medico VARCHAR(500);
        """
            )
        )

        await conn.execute(
            text(
                """
            ALTER TABLE consultas_remotas
            ADD COLUMN IF NOT EXISTS url_sala_paciente VARCHAR(500);
        """
            )
        )

        await conn.execute(
            text(
                """
            ALTER TABLE consultas_remotas
            ADD COLUMN IF NOT EXISTS recordatorio_enviado BOOLEAN NOT NULL DEFAULT FALSE;
        """
            )
        )

    print("✅ Esquema de consultas_remotas actualizado.")


if __name__ == "__main__":
    asyncio.run(main())
