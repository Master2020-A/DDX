import asyncio
import sys

sys.path.insert(0, ".")

from app.core.database import engine, Base
from app.models.app_movil import (
    DispositivoMovil,
    NotificacionPush,
    DocumentoEscaneado,
    SincronizacionOffline,
    CitaMovil,
    ConfiguracionAppMovil,
    SesionMovil,
)


async def crear_tablas():
    print("Creando tablas de app movil...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Tablas creadas exitosamente!")


asyncio.run(crear_tablas())
