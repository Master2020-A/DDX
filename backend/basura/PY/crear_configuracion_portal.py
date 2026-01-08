import asyncio
from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.paciente import Paciente
from app.models.portal_paciente import ConfiguracionPortal
from uuid import UUID


async def crear_configuracion():
    paciente_id = UUID("49bfb1e1-699c-4161-90cd-9162c226259c")

    async with AsyncSessionLocal() as db:
        # Verificar paciente
        result = await db.execute(select(Paciente).where(Paciente.id == paciente_id))
        paciente = result.scalar_one_or_none()

        if not paciente:
            print(f"ERROR: Paciente {paciente_id} no encontrado")
            return

        print(f"Paciente encontrado: {paciente.nombre_completo}")

        # Verificar si ya existe configuración
        result = await db.execute(
            select(ConfiguracionPortal).where(
                ConfiguracionPortal.paciente_id == paciente_id
            )
        )
        config_existente = result.scalar_one_or_none()

        if config_existente:
            print("Ya existe configuración para este paciente")
            return

        # Crear configuración
        config = ConfiguracionPortal(
            paciente_id=paciente_id,
            notificaciones_email=True,
            notificaciones_sms=False,
            notificaciones_push=True,
            compartir_datos_investigacion=False,
            mostrar_perfil_publico=False,
            idioma="es",
            tema="claro",
            zona_horaria="America/Mexico_City",
            recordatorios_citas=True,
            recordatorios_medicamentos=True,
            recordatorios_estudios=True,
        )

        db.add(config)
        await db.commit()
        print("✅ Configuración creada exitosamente")


if __name__ == "__main__":
    asyncio.run(crear_configuracion())
