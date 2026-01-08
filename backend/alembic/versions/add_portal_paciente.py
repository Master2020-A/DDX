"""add portal paciente tables

Revision ID: add_portal_paciente
Revises: 28b6cd113b1e
Create Date: 2025-12-17 13:00:00.000000

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "add_portal_paciente"
down_revision = "28b6cd113b1e"
branch_labels = None
depends_on = None


def upgrade():
    # Crear tabla citas_pacientes
    op.create_table(
        "citas_pacientes",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("paciente_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("medico_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("tipo_cita", sa.String(50), nullable=False),
        sa.Column("especialidad_solicitada", sa.String(100), nullable=True),
        sa.Column("motivo_consulta", sa.Text(), nullable=False),
        sa.Column("fecha_solicitada", sa.Date(), nullable=False),
        sa.Column("hora_solicitada", sa.Time(), nullable=True),
        sa.Column("fecha_confirmada", sa.DateTime(), nullable=True),
        sa.Column("duracion_minutos", sa.Integer(), nullable=True),
        sa.Column("estado", sa.String(50), nullable=False),
        sa.Column("notas_paciente", sa.Text(), nullable=True),
        sa.Column("notas_medico", sa.Text(), nullable=True),
        sa.Column("recordatorio_enviado", sa.Boolean(), nullable=True),
        sa.Column("fecha_recordatorio", sa.DateTime(), nullable=True),
        sa.Column("fecha_cancelacion", sa.DateTime(), nullable=True),
        sa.Column("motivo_cancelacion", sa.Text(), nullable=True),
        sa.Column("cancelado_por", sa.String(50), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["paciente_id"],
            ["pacientes.id"],
        ),
        sa.ForeignKeyConstraint(
            ["medico_id"],
            ["usuarios.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # Crear tabla solicitudes_estudios
    op.create_table(
        "solicitudes_estudios",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("paciente_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "medico_solicitante_id", postgresql.UUID(as_uuid=True), nullable=True
        ),
        sa.Column(
            "medico_autorizador_id", postgresql.UUID(as_uuid=True), nullable=True
        ),
        sa.Column("tipo_estudio", sa.String(50), nullable=False),
        sa.Column("nombre_estudio", sa.String(255), nullable=False),
        sa.Column("descripcion", sa.Text(), nullable=True),
        sa.Column("indicaciones_especiales", sa.Text(), nullable=True),
        sa.Column("estado", sa.String(50), nullable=False),
        sa.Column("prioridad", sa.String(50), nullable=True),
        sa.Column("fecha_solicitud", sa.DateTime(), nullable=True),
        sa.Column("fecha_autorizacion", sa.DateTime(), nullable=True),
        sa.Column("fecha_programada", sa.DateTime(), nullable=True),
        sa.Column("fecha_realizacion", sa.DateTime(), nullable=True),
        sa.Column("resultado_disponible", sa.Boolean(), nullable=True),
        sa.Column("resultado_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("url_resultado", sa.String(500), nullable=True),
        sa.Column("notas_paciente", sa.Text(), nullable=True),
        sa.Column("notas_autorizacion", sa.Text(), nullable=True),
        sa.Column("motivo_rechazo", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["paciente_id"],
            ["pacientes.id"],
        ),
        sa.ForeignKeyConstraint(
            ["medico_solicitante_id"],
            ["usuarios.id"],
        ),
        sa.ForeignKeyConstraint(
            ["medico_autorizador_id"],
            ["usuarios.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # Crear tabla pagos_servicios
    op.create_table(
        "pagos_servicios",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("paciente_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("cita_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("solicitud_estudio_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("concepto", sa.String(255), nullable=False),
        sa.Column("descripcion", sa.Text(), nullable=True),
        sa.Column("monto", sa.Numeric(10, 2), nullable=False),
        sa.Column("moneda", sa.String(3), nullable=True),
        sa.Column("metodo_pago", sa.String(50), nullable=False),
        sa.Column("referencia_pago", sa.String(255), nullable=True),
        sa.Column("estado", sa.String(50), nullable=False),
        sa.Column("fecha_pago", sa.DateTime(), nullable=True),
        sa.Column("fecha_procesado", sa.DateTime(), nullable=True),
        sa.Column("fecha_completado", sa.DateTime(), nullable=True),
        sa.Column(
            "datos_transaccion", postgresql.JSON(astext_type=sa.Text()), nullable=True
        ),
        sa.Column("comprobante_url", sa.String(500), nullable=True),
        sa.Column("factura_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("reembolsado", sa.Boolean(), nullable=True),
        sa.Column("fecha_reembolso", sa.DateTime(), nullable=True),
        sa.Column("motivo_reembolso", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["paciente_id"],
            ["pacientes.id"],
        ),
        sa.ForeignKeyConstraint(
            ["cita_id"],
            ["citas_pacientes.id"],
        ),
        sa.ForeignKeyConstraint(
            ["solicitud_estudio_id"],
            ["solicitudes_estudios.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # Crear tabla mensajes_paciente_medico
    op.create_table(
        "mensajes_paciente_medico",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("paciente_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("medico_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("remitente_tipo", sa.String(50), nullable=False),
        sa.Column("asunto", sa.String(255), nullable=True),
        sa.Column("mensaje", sa.Text(), nullable=False),
        sa.Column(
            "archivos_adjuntos", postgresql.JSON(astext_type=sa.Text()), nullable=True
        ),
        sa.Column("estado", sa.String(50), nullable=False),
        sa.Column("leido", sa.Boolean(), nullable=True),
        sa.Column("fecha_lectura", sa.DateTime(), nullable=True),
        sa.Column("mensaje_padre_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["paciente_id"],
            ["pacientes.id"],
        ),
        sa.ForeignKeyConstraint(
            ["medico_id"],
            ["usuarios.id"],
        ),
        sa.ForeignKeyConstraint(
            ["mensaje_padre_id"],
            ["mensajes_paciente_medico.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # Crear tabla recordatorios_medicamentos
    op.create_table(
        "recordatorios_medicamentos",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("paciente_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("receta_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("nombre_medicamento", sa.String(255), nullable=False),
        sa.Column("dosis", sa.String(100), nullable=False),
        sa.Column("via_administracion", sa.String(50), nullable=True),
        sa.Column("indicaciones", sa.Text(), nullable=True),
        sa.Column("frecuencia", sa.String(50), nullable=False),
        sa.Column("horarios", postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column("fecha_inicio", sa.Date(), nullable=False),
        sa.Column("fecha_fin", sa.Date(), nullable=True),
        sa.Column("duracion_dias", sa.Integer(), nullable=True),
        sa.Column("activo", sa.Boolean(), nullable=True),
        sa.Column("pausado", sa.Boolean(), nullable=True),
        sa.Column("notificar_email", sa.Boolean(), nullable=True),
        sa.Column("notificar_sms", sa.Boolean(), nullable=True),
        sa.Column("notificar_push", sa.Boolean(), nullable=True),
        sa.Column("ultima_toma_registrada", sa.DateTime(), nullable=True),
        sa.Column("tomas_registradas", sa.Integer(), nullable=True),
        sa.Column("tomas_omitidas", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["paciente_id"],
            ["pacientes.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # Crear tabla registros_toma_medicamento
    op.create_table(
        "registros_toma_medicamento",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("recordatorio_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("fecha_programada", sa.DateTime(), nullable=False),
        sa.Column("fecha_real", sa.DateTime(), nullable=True),
        sa.Column("tomado", sa.Boolean(), nullable=True),
        sa.Column("omitido", sa.Boolean(), nullable=True),
        sa.Column("motivo_omision", sa.Text(), nullable=True),
        sa.Column("notas", sa.Text(), nullable=True),
        sa.Column("efectos_secundarios", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["recordatorio_id"],
            ["recordatorios_medicamentos.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # Crear tabla accesos_expediente
    op.create_table(
        "accesos_expediente",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("paciente_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("usuario_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("tipo_acceso", sa.String(50), nullable=False),
        sa.Column("seccion_accedida", sa.String(100), nullable=True),
        sa.Column("recurso_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("ip_address", sa.String(50), nullable=True),
        sa.Column("user_agent", sa.String(255), nullable=True),
        sa.Column("duracion_segundos", sa.Integer(), nullable=True),
        sa.Column("fecha_acceso", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["paciente_id"],
            ["pacientes.id"],
        ),
        sa.ForeignKeyConstraint(
            ["usuario_id"],
            ["usuarios.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # Crear tabla configuracion_portal
    op.create_table(
        "configuracion_portal",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("paciente_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("notificaciones_email", sa.Boolean(), nullable=True),
        sa.Column("notificaciones_sms", sa.Boolean(), nullable=True),
        sa.Column("notificaciones_push", sa.Boolean(), nullable=True),
        sa.Column("compartir_datos_investigacion", sa.Boolean(), nullable=True),
        sa.Column("mostrar_perfil_publico", sa.Boolean(), nullable=True),
        sa.Column("idioma", sa.String(10), nullable=True),
        sa.Column("tema", sa.String(20), nullable=True),
        sa.Column("zona_horaria", sa.String(50), nullable=True),
        sa.Column("recordatorios_citas", sa.Boolean(), nullable=True),
        sa.Column("recordatorios_medicamentos", sa.Boolean(), nullable=True),
        sa.Column("recordatorios_estudios", sa.Boolean(), nullable=True),
        sa.Column(
            "configuracion_adicional",
            postgresql.JSON(astext_type=sa.Text()),
            nullable=True,
        ),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["paciente_id"],
            ["pacientes.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("paciente_id"),
    )

    # Crear índices
    op.create_index("ix_citas_paciente_id", "citas_pacientes", ["paciente_id"])
    op.create_index("ix_citas_estado", "citas_pacientes", ["estado"])
    op.create_index("ix_citas_fecha", "citas_pacientes", ["fecha_solicitada"])

    op.create_index(
        "ix_solicitudes_paciente_id", "solicitudes_estudios", ["paciente_id"]
    )
    op.create_index("ix_solicitudes_estado", "solicitudes_estudios", ["estado"])

    op.create_index("ix_pagos_paciente_id", "pagos_servicios", ["paciente_id"])
    op.create_index("ix_pagos_estado", "pagos_servicios", ["estado"])

    op.create_index(
        "ix_mensajes_paciente_id", "mensajes_paciente_medico", ["paciente_id"]
    )
    op.create_index("ix_mensajes_medico_id", "mensajes_paciente_medico", ["medico_id"])
    op.create_index("ix_mensajes_leido", "mensajes_paciente_medico", ["leido"])

    op.create_index(
        "ix_recordatorios_paciente_id", "recordatorios_medicamentos", ["paciente_id"]
    )
    op.create_index("ix_recordatorios_activo", "recordatorios_medicamentos", ["activo"])


def downgrade():
    # Eliminar índices
    op.drop_index("ix_recordatorios_activo", table_name="recordatorios_medicamentos")
    op.drop_index(
        "ix_recordatorios_paciente_id", table_name="recordatorios_medicamentos"
    )
    op.drop_index("ix_mensajes_leido", table_name="mensajes_paciente_medico")
    op.drop_index("ix_mensajes_medico_id", table_name="mensajes_paciente_medico")
    op.drop_index("ix_mensajes_paciente_id", table_name="mensajes_paciente_medico")
    op.drop_index("ix_pagos_estado", table_name="pagos_servicios")
    op.drop_index("ix_pagos_paciente_id", table_name="pagos_servicios")
    op.drop_index("ix_solicitudes_estado", table_name="solicitudes_estudios")
    op.drop_index("ix_solicitudes_paciente_id", table_name="solicitudes_estudios")
    op.drop_index("ix_citas_fecha", table_name="citas_pacientes")
    op.drop_index("ix_citas_estado", table_name="citas_pacientes")
    op.drop_index("ix_citas_paciente_id", table_name="citas_pacientes")

    # Eliminar tablas
    op.drop_table("configuracion_portal")
    op.drop_table("accesos_expediente")
    op.drop_table("registros_toma_medicamento")
    op.drop_table("recordatorios_medicamentos")
    op.drop_table("mensajes_paciente_medico")
    op.drop_table("pagos_servicios")
    op.drop_table("solicitudes_estudios")
    op.drop_table("citas_pacientes")
