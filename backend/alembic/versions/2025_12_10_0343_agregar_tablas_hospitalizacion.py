"""Agregar tablas de hospitalizacion

Revision ID: hospitalizacion_001
Revises: ee6dec9c9fb4
Create Date: 2025-12-10 03:43:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'hospitalizacion_001'
down_revision = 'ee6dec9c9fb4'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Crear tabla de camas
    op.create_table(
        'camas',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('numero_cama', sa.String(), nullable=False),
        sa.Column('area', sa.String(), nullable=False),
        sa.Column('piso', sa.String(), nullable=True),
        sa.Column('habitacion', sa.String(), nullable=True),
        sa.Column('estado', sa.String(), nullable=False),
        sa.Column('tipo_cama', sa.String(), nullable=True),
        sa.Column('tiene_oxigeno', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('tiene_monitor', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('tiene_ventilador', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('capacidad_peso', sa.Float(), nullable=True),
        sa.Column('hospitalizacion_actual_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('fecha_ultima_limpieza', sa.DateTime(timezone=True), nullable=True),
        sa.Column('fecha_ultimo_mantenimiento', sa.DateTime(timezone=True), nullable=True),
        sa.Column('observaciones', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('numero_cama')
    )
    op.create_index('ix_camas_estado', 'camas', ['estado'])
    op.create_index('ix_camas_area', 'camas', ['area'])

    # Crear tabla de hospitalizaciones
    op.create_table(
        'hospitalizaciones',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('paciente_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('consulta_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('medico_responsable_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('fecha_ingreso', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('fecha_alta', sa.DateTime(timezone=True), nullable=True),
        sa.Column('motivo_ingreso', sa.Text(), nullable=False),
        sa.Column('diagnostico_ingreso', sa.Text(), nullable=False),
        sa.Column('diagnostico_egreso', sa.Text(), nullable=True),
        sa.Column('resumen_clinico', sa.Text(), nullable=True),
        sa.Column('area_hospitalizacion', sa.String(), nullable=True),
        sa.Column('numero_cama', sa.String(), nullable=True),
        sa.Column('piso', sa.String(), nullable=True),
        sa.Column('estado', sa.String(), nullable=False),
        sa.Column('prioridad', sa.String(), nullable=False, server_default='normal'),
        sa.Column('tipo_ingreso', sa.String(), nullable=True),
        sa.Column('alergias_conocidas', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('antecedentes_relevantes', sa.Text(), nullable=True),
        sa.Column('tratamiento_actual', sa.Text(), nullable=True),
        sa.Column('tipo_seguro', sa.String(), nullable=True),
        sa.Column('numero_poliza', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['paciente_id'], ['pacientes.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['consulta_id'], ['consultas.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['medico_responsable_id'], ['usuarios.id'], ondelete='RESTRICT')
    )
    op.create_index('ix_hospitalizaciones_paciente_id', 'hospitalizaciones', ['paciente_id'])
    op.create_index('ix_hospitalizaciones_estado', 'hospitalizaciones', ['estado'])
    op.create_index('ix_hospitalizaciones_fecha_ingreso', 'hospitalizaciones', ['fecha_ingreso'])

    # Crear tabla de notas de evolución
    op.create_table(
        'notas_evolucion',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('hospitalizacion_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('medico_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('fecha_nota', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('tipo_nota', sa.String(), nullable=False, server_default='evolucion'),
        sa.Column('turno', sa.String(), nullable=True),
        sa.Column('subjetivo', sa.Text(), nullable=True),
        sa.Column('objetivo', sa.Text(), nullable=True),
        sa.Column('temperatura', sa.Float(), nullable=True),
        sa.Column('presion_arterial_sistolica', sa.Integer(), nullable=True),
        sa.Column('presion_arterial_diastolica', sa.Integer(), nullable=True),
        sa.Column('frecuencia_cardiaca', sa.Integer(), nullable=True),
        sa.Column('frecuencia_respiratoria', sa.Integer(), nullable=True),
        sa.Column('saturacion_oxigeno', sa.Float(), nullable=True),
        sa.Column('evaluacion', sa.Text(), nullable=True),
        sa.Column('plan', sa.Text(), nullable=True),
        sa.Column('estudios_solicitados', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('procedimientos_realizados', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('estado_general', sa.String(), nullable=True),
        sa.Column('nivel_conciencia', sa.String(), nullable=True),
        sa.Column('observaciones', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['hospitalizacion_id'], ['hospitalizaciones.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['medico_id'], ['usuarios.id'], ondelete='RESTRICT')
    )
    op.create_index('ix_notas_evolucion_hospitalizacion_id', 'notas_evolucion', ['hospitalizacion_id'])
    op.create_index('ix_notas_evolucion_fecha_nota', 'notas_evolucion', ['fecha_nota'])

    # Crear tabla de indicaciones médicas
    op.create_table(
        'indicaciones_medicas',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('hospitalizacion_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('medico_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('fecha_indicacion', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('tipo_indicacion', sa.String(), nullable=False),
        sa.Column('descripcion', sa.Text(), nullable=False),
        sa.Column('dosis', sa.String(), nullable=True),
        sa.Column('via_administracion', sa.String(), nullable=True),
        sa.Column('frecuencia', sa.String(), nullable=True),
        sa.Column('duracion', sa.String(), nullable=True),
        sa.Column('prioridad', sa.String(), nullable=False, server_default='normal'),
        sa.Column('estado', sa.String(), nullable=False, server_default='activa'),
        sa.Column('fecha_inicio', sa.DateTime(timezone=True), nullable=True),
        sa.Column('fecha_fin', sa.DateTime(timezone=True), nullable=True),
        sa.Column('fecha_suspension', sa.DateTime(timezone=True), nullable=True),
        sa.Column('motivo_suspension', sa.Text(), nullable=True),
        sa.Column('observaciones', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['hospitalizacion_id'], ['hospitalizaciones.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['medico_id'], ['usuarios.id'], ondelete='RESTRICT')
    )
    op.create_index('ix_indicaciones_medicas_hospitalizacion_id', 'indicaciones_medicas', ['hospitalizacion_id'])
    op.create_index('ix_indicaciones_medicas_estado', 'indicaciones_medicas', ['estado'])

    # Crear tabla de notas de alta
    op.create_table(
        'notas_alta',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('hospitalizacion_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('medico_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('fecha_alta', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('tipo_alta', sa.String(), nullable=False),
        sa.Column('motivo_ingreso', sa.Text(), nullable=False),
        sa.Column('resumen_evolucion', sa.Text(), nullable=False),
        sa.Column('diagnostico_egreso', sa.Text(), nullable=False),
        sa.Column('procedimientos_realizados', sa.Text(), nullable=True),
        sa.Column('complicaciones', sa.Text(), nullable=True),
        sa.Column('condicion_egreso', sa.String(), nullable=True),
        sa.Column('estado_funcional', sa.String(), nullable=True),
        sa.Column('medicamentos_egreso', sa.Text(), nullable=True),
        sa.Column('dieta_recomendada', sa.Text(), nullable=True),
        sa.Column('cuidados_domiciliarios', sa.Text(), nullable=True),
        sa.Column('restricciones', sa.Text(), nullable=True),
        sa.Column('fecha_control', sa.DateTime(timezone=True), nullable=True),
        sa.Column('especialidad_control', sa.String(), nullable=True),
        sa.Column('estudios_pendientes', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('pronostico', sa.String(), nullable=True),
        sa.Column('observaciones', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['hospitalizacion_id'], ['hospitalizaciones.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['medico_id'], ['usuarios.id'], ondelete='RESTRICT'),
        sa.UniqueConstraint('hospitalizacion_id')
    )
    op.create_index('ix_notas_alta_fecha_alta', 'notas_alta', ['fecha_alta'])


def downgrade() -> None:
    # Eliminar tablas en orden inverso
    op.drop_index('ix_notas_alta_fecha_alta', table_name='notas_alta')
    op.drop_table('notas_alta')
    
    op.drop_index('ix_indicaciones_medicas_estado', table_name='indicaciones_medicas')
    op.drop_index('ix_indicaciones_medicas_hospitalizacion_id', table_name='indicaciones_medicas')
    op.drop_table('indicaciones_medicas')
    
    op.drop_index('ix_notas_evolucion_fecha_nota', table_name='notas_evolucion')
    op.drop_index('ix_notas_evolucion_hospitalizacion_id', table_name='notas_evolucion')
    op.drop_table('notas_evolucion')
    
    op.drop_index('ix_hospitalizaciones_fecha_ingreso', table_name='hospitalizaciones')
    op.drop_index('ix_hospitalizaciones_estado', table_name='hospitalizaciones')
    op.drop_index('ix_hospitalizaciones_paciente_id', table_name='hospitalizaciones')
    op.drop_table('hospitalizaciones')
    
    op.drop_index('ix_camas_area', table_name='camas')
    op.drop_index('ix_camas_estado', table_name='camas')
    op.drop_table('camas')
