"""
Script para crear las tablas del módulo de Backups y Recuperación
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import engine, Base
from app.models import (
    Backup,
    ProgramacionBackup,
    Restauracion,
    ReplicacionBD,
    MonitoreoSalud,
    AlertaBackup,
    PlanRecuperacion,
)


async def main():
    print("🔧 Creando tablas del módulo de Backups y Recuperación...")

    try:
        async with engine.begin() as conn:
            # Crear las tablas
            await conn.run_sync(Base.metadata.create_all)

        print("✅ Tablas creadas exitosamente:")
        print("   - backups")
        print("   - programacion_backups")
        print("   - restauraciones")
        print("   - replicacion_bd")
        print("   - monitoreo_salud")
        print("   - alertas_backup")
        print("   - planes_recuperacion")
        print("\n✅ Migración completada exitosamente")
        print("\n📝 Próximos pasos:")
        print("   1. Configurar variables de entorno:")
        print("      - BACKUP_PATH: Ruta para almacenar backups")
        print("      - POSTGRES_HOST, POSTGRES_PORT, POSTGRES_USER, POSTGRES_PASSWORD")
        print("   2. Instalar herramientas de PostgreSQL (pg_dump, psql)")
        print("   3. Configurar programaciones de backup automático")
        print("   4. Definir plan de recuperación ante desastres")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
