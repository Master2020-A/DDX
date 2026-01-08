# fix_telemedicina_columns.py

import asyncio
from sqlalchemy import text
from app.core.database import engine


async def main():
    async with engine.begin() as conn:
        # ==========================
        # consultas_remotas
        # ==========================
        await conn.execute(
            text(
                """
            ALTER TABLE consultas_remotas
            ADD COLUMN IF NOT EXISTS metadata_conexion JSONB;
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

        # ==========================
        # mensajes_chat
        # ==========================
        await conn.execute(
            text(
                """
            ALTER TABLE mensajes_chat
            ADD COLUMN IF NOT EXISTS leido BOOLEAN NOT NULL DEFAULT FALSE;
        """
            )
        )

        await conn.execute(
            text(
                """
            ALTER TABLE mensajes_chat
            ADD COLUMN IF NOT EXISTS fecha_leido TIMESTAMP WITHOUT TIME ZONE NULL;
        """
            )
        )

        # ==========================
        # prescripciones_electronicas
        # ==========================
        await conn.execute(
            text(
                """
            ALTER TABLE prescripciones_electronicas
            ADD COLUMN IF NOT EXISTS activa BOOLEAN NOT NULL DEFAULT TRUE;
        """
            )
        )

        await conn.execute(
            text(
                """
            ALTER TABLE prescripciones_electronicas
            ADD COLUMN IF NOT EXISTS firma_medico TEXT;
        """
            )
        )

        await conn.execute(
            text(
                """
            ALTER TABLE prescripciones_electronicas
            ADD COLUMN IF NOT EXISTS codigo_verificacion VARCHAR(20);
        """
            )
        )

        # ==========================
        # seguimientos_post_consulta
        # ==========================
        await conn.execute(
            text(
                """
            ALTER TABLE seguimientos_post_consulta
            ADD COLUMN IF NOT EXISTS enviado BOOLEAN NOT NULL DEFAULT FALSE;
        """
            )
        )

        await conn.execute(
            text(
                """
            ALTER TABLE seguimientos_post_consulta
            ADD COLUMN IF NOT EXISTS fecha_enviado TIMESTAMP WITHOUT TIME ZONE NULL;
        """
            )
        )

        await conn.execute(
            text(
                """
            ALTER TABLE seguimientos_post_consulta
            ADD COLUMN IF NOT EXISTS respuesta_paciente TEXT;
        """
            )
        )

        await conn.execute(
            text(
                """
            ALTER TABLE seguimientos_post_consulta
            ADD COLUMN IF NOT EXISTS fecha_respuesta TIMESTAMP WITHOUT TIME ZONE NULL;
        """
            )
        )

    print("✅ Columnas de telemedicina verificadas/creadas correctamente.")


if __name__ == "__main__":
    asyncio.run(main())
