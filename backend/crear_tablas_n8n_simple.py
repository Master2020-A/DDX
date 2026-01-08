"""
Script simple para crear las tablas de N8N usando psycopg2
"""

import psycopg2
from urllib.parse import urlparse
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Obtener la URL de la base de datos del .env
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://user:password@localhost:5432/ddx"
)

# Parsear URL
result = urlparse(DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://"))

# Conectar a la base de datos
conn = psycopg2.connect(
    database=result.path[1:],
    user=result.username,
    password=result.password,
    host=result.hostname,
    port=result.port,
)

conn.autocommit = True
cursor = conn.cursor()

print("🔍 Verificando tablas de N8N...")

# Verificar si n8n_config existe
cursor.execute(
    """
    SELECT EXISTS (
        SELECT FROM information_schema.tables 
        WHERE table_name = 'n8n_config'
    )
"""
)
n8n_config_exists = cursor.fetchone()[0]

# Verificar si n8n_event_log existe
cursor.execute(
    """
    SELECT EXISTS (
        SELECT FROM information_schema.tables 
        WHERE table_name = 'n8n_event_log'
    )
"""
)
n8n_event_log_exists = cursor.fetchone()[0]

print(f"\n📊 Resultados:")
print(f"   n8n_config: {'✅ Existe' if n8n_config_exists else '❌ No existe'}")
print(f"   n8n_event_log: {'✅ Existe' if n8n_event_log_exists else '❌ No existe'}")

if not n8n_config_exists or not n8n_event_log_exists:
    print("\n🔧 Creando tablas faltantes...")

    if not n8n_config_exists:
        cursor.execute(
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
        print("   ✅ Tabla n8n_config creada")

    if not n8n_event_log_exists:
        cursor.execute(
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

        # Crear índices
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_n8n_event_log_evento_tipo ON n8n_event_log(evento_tipo)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_n8n_event_log_created_at ON n8n_event_log(created_at)"
        )

        print("   ✅ Tabla n8n_event_log creada")

    print("\n✅ Tablas de N8N creadas exitosamente")
else:
    print("\n✅ Todas las tablas de N8N ya existen")

cursor.close()
conn.close()

print("\n🎉 Proceso completado. Ahora puedes probar crear workflows desde el frontend.")
