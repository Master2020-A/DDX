"""
Script para verificar datos del Portal del Paciente
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))


async def main():
    print("=" * 70)
    print("🔍 VERIFICANDO DATOS DEL PORTAL DEL PACIENTE")
    print("=" * 70)

    from sqlalchemy import select, func
    from app.core.database import AsyncSessionLocal

    # Importar modelos
    import app.models.portal_paciente
    from app.models.portal_paciente import (
        CitaPaciente,
        SolicitudEstudio,
        PagoServicio,
        MensajePacienteMedico,
        RecordatorioMedicamento,
        ConfiguracionPortal,
    )

    async with AsyncSessionLocal() as db:
        try:
            # Contar citas
            result = await db.execute(select(func.count(CitaPaciente.id)))
            total_citas = result.scalar() or 0
            print(f"\n📅 Citas: {total_citas}")

            # Contar solicitudes de estudios
            result = await db.execute(select(func.count(SolicitudEstudio.id)))
            total_estudios = result.scalar() or 0
            print(f"🔬 Solicitudes de estudios: {total_estudios}")

            # Contar pagos
            result = await db.execute(select(func.count(PagoServicio.id)))
            total_pagos = result.scalar() or 0
            print(f"💳 Pagos: {total_pagos}")

            # Contar mensajes
            result = await db.execute(select(func.count(MensajePacienteMedico.id)))
            total_mensajes = result.scalar() or 0
            print(f"💬 Mensajes: {total_mensajes}")

            # Contar recordatorios
            result = await db.execute(select(func.count(RecordatorioMedicamento.id)))
            total_recordatorios = result.scalar() or 0
            print(f"💊 Recordatorios: {total_recordatorios}")

            # Contar configuraciones
            result = await db.execute(select(func.count(ConfiguracionPortal.id)))
            total_configs = result.scalar() or 0
            print(f"⚙️  Configuraciones: {total_configs}")

            print("\n" + "=" * 70)
            if all(
                [
                    total_citas,
                    total_estudios,
                    total_pagos,
                    total_mensajes,
                    total_recordatorios,
                ]
            ):
                print("✅ ¡DATOS VERIFICADOS CORRECTAMENTE!")
            else:
                print(
                    "⚠️  Algunos datos no se crearon. Ejecuta: python poblar_portal_paciente.py"
                )
            print("=" * 70)

        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback

            traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
