import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))


async def main():
    from sqlalchemy import text
    from app.core.database import AsyncSessionLocal

    print("Aplicando migracion del Portal del Paciente...")

    async with AsyncSessionLocal() as db:
        try:
            # Verificar si existe
            result = await db.execute(
                text(
                    "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'citas_pacientes')"
                )
            )
            existe = result.scalar()

            if existe:
                print("Las tablas ya existen")
                return

            print("Creando tablas...")

            # Crear todas las tablas
            sqls = [
                """CREATE TABLE citas_pacientes (
                    id UUID PRIMARY KEY, paciente_id UUID NOT NULL REFERENCES pacientes(id),
                    medico_id UUID REFERENCES usuarios(id), tipo_cita VARCHAR(50) NOT NULL,
                    especialidad_solicitada VARCHAR(100), motivo_consulta TEXT NOT NULL,
                    fecha_solicitada DATE NOT NULL, hora_solicitada TIME, fecha_confirmada TIMESTAMP,
                    duracion_minutos INTEGER, estado VARCHAR(50) NOT NULL, notas_paciente TEXT,
                    notas_medico TEXT, recordatorio_enviado BOOLEAN, fecha_recordatorio TIMESTAMP,
                    fecha_cancelacion TIMESTAMP, motivo_cancelacion TEXT, cancelado_por VARCHAR(50),
                    created_at TIMESTAMP, updated_at TIMESTAMP
                )""",
                """CREATE TABLE solicitudes_estudios (
                    id UUID PRIMARY KEY, paciente_id UUID NOT NULL REFERENCES pacientes(id),
                    medico_solicitante_id UUID REFERENCES usuarios(id),
                    medico_autorizador_id UUID REFERENCES usuarios(id),
                    tipo_estudio VARCHAR(50) NOT NULL, nombre_estudio VARCHAR(255) NOT NULL,
                    descripcion TEXT, indicaciones_especiales TEXT, estado VARCHAR(50) NOT NULL,
                    prioridad VARCHAR(50), fecha_solicitud TIMESTAMP, fecha_autorizacion TIMESTAMP,
                    fecha_programada TIMESTAMP, fecha_realizacion TIMESTAMP, resultado_disponible BOOLEAN,
                    resultado_id UUID, url_resultado VARCHAR(500), notas_paciente TEXT,
                    notas_autorizacion TEXT, motivo_rechazo TEXT, created_at TIMESTAMP, updated_at TIMESTAMP
                )""",
                """CREATE TABLE pagos_servicios (
                    id UUID PRIMARY KEY, paciente_id UUID NOT NULL REFERENCES pacientes(id),
                    cita_id UUID REFERENCES citas_pacientes(id),
                    solicitud_estudio_id UUID REFERENCES solicitudes_estudios(id),
                    concepto VARCHAR(255) NOT NULL, descripcion TEXT, monto NUMERIC(10,2) NOT NULL,
                    moneda VARCHAR(3), metodo_pago VARCHAR(50) NOT NULL, referencia_pago VARCHAR(255),
                    estado VARCHAR(50) NOT NULL, fecha_pago TIMESTAMP, fecha_procesado TIMESTAMP,
                    fecha_completado TIMESTAMP, datos_transaccion JSON, comprobante_url VARCHAR(500),
                    factura_id UUID, reembolsado BOOLEAN, fecha_reembolso TIMESTAMP,
                    motivo_reembolso TEXT, created_at TIMESTAMP, updated_at TIMESTAMP
                )""",
                """CREATE TABLE mensajes_paciente_medico (
                    id UUID PRIMARY KEY, paciente_id UUID NOT NULL REFERENCES pacientes(id),
                    medico_id UUID NOT NULL REFERENCES usuarios(id), remitente_tipo VARCHAR(50) NOT NULL,
                    asunto VARCHAR(255), mensaje TEXT NOT NULL, archivos_adjuntos JSON,
                    estado VARCHAR(50) NOT NULL, leido BOOLEAN, fecha_lectura TIMESTAMP,
                    mensaje_padre_id UUID REFERENCES mensajes_paciente_medico(id),
                    created_at TIMESTAMP, updated_at TIMESTAMP
                )""",
                """CREATE TABLE recordatorios_medicamentos (
                    id UUID PRIMARY KEY, paciente_id UUID NOT NULL REFERENCES pacientes(id),
                    receta_id UUID, nombre_medicamento VARCHAR(255) NOT NULL, dosis VARCHAR(100) NOT NULL,
                    via_administracion VARCHAR(50), indicaciones TEXT, frecuencia VARCHAR(50) NOT NULL,
                    horarios JSON NOT NULL, fecha_inicio DATE NOT NULL, fecha_fin DATE,
                    duracion_dias INTEGER, activo BOOLEAN, pausado BOOLEAN, notificar_email BOOLEAN,
                    notificar_sms BOOLEAN, notificar_push BOOLEAN, ultima_toma_registrada TIMESTAMP,
                    tomas_registradas INTEGER, tomas_omitidas INTEGER, created_at TIMESTAMP, updated_at TIMESTAMP
                )""",
                """CREATE TABLE registros_toma_medicamento (
                    id UUID PRIMARY KEY, recordatorio_id UUID NOT NULL REFERENCES recordatorios_medicamentos(id),
                    fecha_programada TIMESTAMP NOT NULL, fecha_real TIMESTAMP, tomado BOOLEAN,
                    omitido BOOLEAN, motivo_omision TEXT, notas TEXT, efectos_secundarios TEXT,
                    created_at TIMESTAMP
                )""",
                """CREATE TABLE configuracion_portal (
                    id UUID PRIMARY KEY, paciente_id UUID NOT NULL UNIQUE REFERENCES pacientes(id),
                    notificaciones_email BOOLEAN, notificaciones_sms BOOLEAN, notificaciones_push BOOLEAN,
                    compartir_datos_investigacion BOOLEAN, mostrar_perfil_publico BOOLEAN,
                    idioma VARCHAR(10), tema VARCHAR(20), zona_horaria VARCHAR(50),
                    recordatorios_citas BOOLEAN, recordatorios_medicamentos BOOLEAN,
                    recordatorios_estudios BOOLEAN, created_at TIMESTAMP, updated_at TIMESTAMP
                )""",
                """CREATE TABLE accesos_expediente (
                    id UUID PRIMARY KEY, paciente_id UUID NOT NULL REFERENCES pacientes(id),
                    usuario_id UUID REFERENCES usuarios(id), tipo_acceso VARCHAR(50) NOT NULL,
                    seccion_accedida VARCHAR(100), fecha_acceso TIMESTAMP NOT NULL,
                    ip_address VARCHAR(50), user_agent TEXT, duracion_segundos INTEGER, created_at TIMESTAMP
                )""",
            ]

            for sql in sqls:
                await db.execute(text(sql))

            # Crear índices
            indices = [
                "CREATE INDEX idx_citas_paciente ON citas_pacientes(paciente_id)",
                "CREATE INDEX idx_citas_medico ON citas_pacientes(medico_id)",
                "CREATE INDEX idx_citas_fecha ON citas_pacientes(fecha_solicitada)",
                "CREATE INDEX idx_solicitudes_paciente ON solicitudes_estudios(paciente_id)",
                "CREATE INDEX idx_pagos_paciente ON pagos_servicios(paciente_id)",
                "CREATE INDEX idx_mensajes_paciente ON mensajes_paciente_medico(paciente_id)",
                "CREATE INDEX idx_recordatorios_paciente ON recordatorios_medicamentos(paciente_id)",
                "CREATE INDEX idx_accesos_paciente ON accesos_expediente(paciente_id)",
            ]

            for idx in indices:
                await db.execute(text(idx))

            await db.commit()
            print("Tablas creadas exitosamente!")

            # Actualizar Alembic
            await db.execute(
                text("UPDATE alembic_version SET version_num = 'add_portal_paciente'")
            )
            await db.commit()
            print("Migracion completada!")

        except Exception as e:
            print(f"Error: {e}")
            await db.rollback()
            raise


asyncio.run(main())
