import asyncio
import os
from uuid import uuid4

from sqlalchemy import insert
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import settings
from app.core.database import Base
from app.models.n8n_config import N8NConfig


async def main():
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all, tables=[N8NConfig.__table__])

        stmt = insert(N8NConfig).values(
            api_key=f"n8n_{uuid4().hex}",
            nombre="DDX N8N",
            descripcion="Configuración automática",
            n8n_webhook_url="http://localhost:5678/webhook",
            n8n_api_url="http://localhost:5678",
            activo=True,
            webhooks_habilitados=True,
            timeout_segundos=5,
            eventos_habilitados=None,
            total_eventos_enviados=0,
            total_eventos_exitosos=0,
            total_eventos_fallidos=0,
            created_by=os.getenv("DEFAULT_ADMIN_ID", str(uuid4())),
        )
        await conn.execute(stmt)
        await conn.commit()
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
