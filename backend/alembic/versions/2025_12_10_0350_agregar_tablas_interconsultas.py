"""Agregar tablas de interconsultas

Revision ID: interconsultas_001
Revises: hospitalizacion_001
Create Date: 2025-12-10 03:50:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'interconsultas_001'
down_revision = 'hospitalizacion_001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Crear tabla de interconsultas
    op.create_table(
        'interconsultas',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('paciente_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('consulta_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('hospitalizacion_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('medico_solicitante_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('especialista_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('especialidad_requerida', sa.String(100), nullable=False),
        sa.Column('motivo_solicitud', sa.Text(), nullable=False),
        sa.Column('antecedentes_relevantes', sa.Text(), nullable=True),
        sa.Column('estudios_adjuntos', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('urgencia', sa.String(20), nullable=False, server_default='normal'),
        sa.Column('estado', sa.String(50), nullable=False, server_default='solicitada'),
        sa.Column('fecha_solicitud', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('fecha_aceptacion', sa.DateTime(timezone=True), nullable=True),
        sa.Column('fecha_programada', sa.DateTime(timezone=True), nullable=True),
        sa.Column('fecha_realizada', sa.DateTime(timezone=True), nullable=True),
        sa.Column('fecha_completada', sa.DateTime(timezone=True), nullable=True),
        sa.Column('diagnostico_especialista', sa.Text(), nullable=True),
        sa.Column('hallazgos', sa.Text(), nullable=True),
        sa.Column('recomendaciones', sa.Text(), nullable=True),
        sa.Column('plan_tratamiento', sa.Text(), nullable=True),
        sa.Column('requiere_seguimiento', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('fecha_seguimiento', sa.DateTime(timezone=True), nullable=True),
        sa.Column('motivo_rechazo', sa.Text(), nullable=True),
        sa.Column('prioridad_clinica', sa.Integer(), server_default='1', nullable=False),
        sa.Column('notas_internas', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['paciente_id'], ['pacientes.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['consulta_id'], ['consultas.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['hospitalizacion_id'], ['hospitalizaciones.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['medico_solicitante_id'], ['usuarios.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['especialista_id'], ['usuarios.id'], ondelete='SET NULL')
    )
    op.create_index('ix_interconsultas_paciente_id', 'interconsultas', ['paciente_id'])
    op.create_index('ix_interconsultas_consulta_id', 'interconsultas', ['consulta_id'])
    op.create_index('ix_interconsultas_estado', 'interconsultas', ['estado'])
    op.create_index('ix_interconsultas_especialidad', 'interconsultas', ['especialidad_requerida'])
    op.create_index('ix_interconsultas_fecha_solicitud', 'interconsultas', ['fecha_solicitud'])

    # Crear tabla de notificaciones
    op.create_table(
        'notificaciones_interconsulta',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('interconsulta_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('medico_destinatario_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tipo', sa.String(50), nullable=False),
        sa.Column('titulo', sa.String(200), nullable=False),
        sa.Column('mensaje', sa.Text(), nullable=False),
        sa.Column('leida', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('fecha_lectura', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['interconsulta_id'], ['interconsultas.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['medico_destinatario_id'], ['usuarios.id'], ondelete='CASCADE')
    )
    op.create_index('ix_notificaciones_interconsulta_id', 'notificaciones_interconsulta', ['interconsulta_id'])
    op.create_index('ix_notificaciones_medico_id', 'notificaciones_interconsulta', ['medico_destinatario_id'])
    op.create_index('ix_notificaciones_leida', 'notificaciones_interconsulta', ['leida'])

    # Crear tabla de mensajes (chat)
    op.create_table(
        'mensajes_interconsulta',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('interconsulta_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('medico_emisor_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('mensaje', sa.Text(), nullable=False),
        sa.Column('archivos_adjuntos', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('leido', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('fecha_lectura', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['interconsulta_id'], ['interconsultas.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['medico_emisor_id'], ['usuarios.id'], ondelete='CASCADE')
    )
    op.create_index('ix_mensajes_interconsulta_id', 'mensajes_interconsulta', ['interconsulta_id'])
    op.create_index('ix_mensajes_created_at', 'mensajes_interconsulta', ['created_at'])

    # Crear tabla de seguimientos
    op.create_table(
        'seguimientos_interconsulta',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('interconsulta_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('medico_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tipo_seguimiento', sa.String(50), nullable=False),
        sa.Column('observaciones', sa.Text(), nullable=False),
        sa.Column('estado_paciente', sa.String(100), nullable=True),
        sa.Column('cambios_tratamiento', sa.Text(), nullable=True),
        sa.Column('proxima_revision', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['interconsulta_id'], ['interconsultas.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['medico_id'], ['usuarios.id'], ondelete='CASCADE')
    )
    op.create_index('ix_seguimientos_interconsulta_id', 'seguimientos_interconsulta', ['interconsulta_id'])


def downgrade() -> None:
    # Eliminar tablas en orden inverso
    op.drop_index('ix_seguimientos_interconsulta_id', table_name='seguimientos_interconsulta')
    op.drop_table('seguimientos_interconsulta')
    
    op.drop_index('ix_mensajes_created_at', table_name='mensajes_interconsulta')
    op.drop_index('ix_mensajes_interconsulta_id', table_name='mensajes_interconsulta')
    op.drop_table('mensajes_interconsulta')
    
    op.drop_index('ix_notificaciones_leida', table_name='notificaciones_interconsulta')
    op.drop_index('ix_notificaciones_medico_id', table_name='notificaciones_interconsulta')
    op.drop_index('ix_notificaciones_interconsulta_id', table_name='notificaciones_interconsulta')
    op.drop_table('notificaciones_interconsulta')
    
    op.drop_index('ix_interconsultas_fecha_solicitud', table_name='interconsultas')
    op.drop_index('ix_interconsultas_especialidad', table_name='interconsultas')
    op.drop_index('ix_interconsultas_estado', table_name='interconsultas')
    op.drop_index('ix_interconsultas_consulta_id', table_name='interconsultas')
    op.drop_index('ix_interconsultas_paciente_id', table_name='interconsultas')
    op.drop_table('interconsultas')
