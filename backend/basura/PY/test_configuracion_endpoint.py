import asyncio
import sys
from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.paciente import Paciente
from app.models.portal_paciente import ConfiguracionPortal
from uuid import UUID


async def test_configuracion():
    """Probar endpoint de configuración"""

    paciente_id = UUID("49bfb1e1-699c-4161-90cd-9162c226259c")

    async with AsyncSessionLocal() as db:
        # Verificar que el paciente existe
        print(f"\n1. Verificando paciente {paciente_id}...")
        result = await db.execute(select(Paciente).where(Paciente.id == paciente_id))
        paciente = result.scalar_one_or_none()

        if not paciente:
            print(f"❌ ERROR: Paciente no encontrado")
            return

        print(f"✅ Paciente encontrado: {paciente.nombre} {paciente.apellido_paterno}")

        # Verificar configuración existente
        print(f"\n2. Verificando configuración existente...")
        result = await db.execute(
            select(ConfiguracionPortal).where(
                ConfiguracionPortal.paciente_id == paciente_id
            )
        )
        config = result.scalar_one_or_none()

        if config:
            print(f"✅ Configuración encontrada:")
            print(f"   - Email: {config.notificaciones_email}")
            print(f"   - SMS: {config.notificaciones_sms}")
            print(f"   - Push: {config.notificaciones_push}")
            print(f"   - Idioma: {config.idioma}")
            print(f"   - Tema: {config.tema}")
        else:
            print(f"⚠️  No existe configuración, creando una por defecto...")

            # Crear configuración por defecto
            nueva_config = ConfiguracionPortal(
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
            db.add(nueva_config)
            await db.commit()
            await db.refresh(nueva_config)

            print(f"✅ Configuración creada exitosamente")
            print(f"   - ID: {nueva_config.id}")


if __name__ == "__main__":
    try:
        asyncio.run(test_configuracion())
        print("\n✅ Prueba completada exitosamente")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
