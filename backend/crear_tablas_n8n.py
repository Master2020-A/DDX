"""
Script para crear las tablas de N8N en la base de datos
"""

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from app.core.config import settings
from app.models.n8n_config import N8NConfig, N8NEventLog
from app.core.database import Base


async def crear_tablas_n8n():
    """Crear las tablas de N8N"""
    print("🔄 Creando tablas de N8N...")

    # Crear engine
    engine = create_async_engine(settings.DATABASE_URL, echo=True)

    try:
        # Crear solo las tablas de N8N
        async with engine.begin() as conn:
            # Crear tablas
            await conn.run_sync(
                Base.metadata.create_all,
                tables=[N8NConfig.__table__, N8NEventLog.__table__],
            )

        print("✅ Tablas de N8N creadas exitosamente")
        print("   - n8n_config")
        print("   - n8n_event_log")

    except Exception as e:
        print(f"❌ Error al crear tablas: {e}")
        raise
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(crear_tablas_n8n())
