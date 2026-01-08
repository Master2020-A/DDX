"""
Script para verificar si las tablas de N8N existen
"""

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from app.core.config import settings


async def verificar_tablas():
    """Verificar si las tablas de N8N existen"""
    print("🔍 Verificando tablas de N8N...")

    engine = create_async_engine(settings.DATABASE_URL, echo=False)

    try:
        async with engine.begin() as conn:
            # Verificar n8n_config
            result = await conn.execute(
                text(
                    "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'n8n_config')"
                )
            )
            n8n_config_exists = result.scalar()

            # Verificar n8n_event_log
            result = await conn.execute(
                text(
                    "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'n8n_event_log')"
                )
            )
            n8n_event_log_exists = result.scalar()

            print(f"\n📊 Resultados:")
            print(
                f"   n8n_config: {'✅ Existe' if n8n_config_exists else '❌ No existe'}"
            )
            print(
                f"   n8n_event_log: {'✅ Existe' if n8n_event_log_exists else '❌ No existe'}"
            )

            if not n8n_config_exists or not n8n_event_log_exists:
                print("\n🔧 Creando tablas faltantes...")

                if not n8n_config_exists:
                    await conn.execute(
                        text(
                            """
                        CREATE TABLE n8n_config (
                            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                            api_key VARCHAR(255) UNIQUE NOT NULL,
                            nombre VARCHAR(100) NOT NULL DEFAULT 'N8N Integration',
                            descripcion TEXT,
                            n8n_webhook_url VARCHAR(500) NOT NULL,
                            n8n_api_url VARCHAR(500),
                            activo BOOLEAN NOT NULL DEFAULT TRUE,
                            webhooks_habilitados BOOLEAN NOT NULL DEFAULT TRUE,
                            timeout_segundos INTEGER NOT NULL DEFAULT 5,
                            eventos_habilitados JSONB,
                            total_eventos_enviados INTEGER NOT NULL DEFAULT 0,
                            total_eventos_exitosos INTEGER NOT NULL DEFAULT 0,
                            total_eventos_fallidos INTEGER NOT NULL DEFAULT 0,
                            ultimo_evento_enviado TIMESTAMP,
                            created_by UUID NOT NULL,
                            created_at TIMESTAMP NOT NULL DEFAULT NOW(),
                            updated_at TIMESTAMP DEFAULT NOW()
                        )
                    """
                        )
                    )
                    print("   ✅ Tabla n8n_config creada")

                if not n8n_event_log_exists:
                    await conn.execute(
                        text(
                            """
                        CREATE TABLE n8n_event_log (
                            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                            evento_tipo VARCHAR(100) NOT NULL,
                            evento_data JSONB NOT NULL,
                            prioridad VARCHAR(20) NOT NULL DEFAULT 'normal',
                            webhook_url VARCHAR(500) NOT NULL,
                            exitoso BOOLEAN NOT NULL,
                            codigo_http INTEGER,
                            tiempo_respuesta_ms INTEGER,
                            error TEXT,
                            created_at TIMESTAMP NOT NULL DEFAULT NOW()
                        )
                    """
                        )
                    )
                    print("   ✅ Tabla n8n_event_log creada")

                print("\n✅ Tablas de N8N creadas exitosamente")
            else:
                print("\n✅ Todas las tablas de N8N ya existen")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        raise
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(verificar_tablas())
