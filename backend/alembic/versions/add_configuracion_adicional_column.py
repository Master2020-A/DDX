"""add configuracion_adicional column to configuracion_portal

Revision ID: add_config_adicional_001
Revises: None
Create Date: 2025-12-18 19:00:00
"""

from alembic import op
from sqlalchemy.dialects import postgresql

# Identificadores de Alembic
revision = "add_config_adicional_001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Hacer la migración idempotente: no falla si la columna ya existe
    op.execute(
        """
        ALTER TABLE configuracion_portal
        ADD COLUMN IF NOT EXISTS configuracion_adicional JSONB DEFAULT '{}'::jsonb
        """
    )


def downgrade():
    op.execute(
        """
        ALTER TABLE configuracion_portal
        DROP COLUMN IF EXISTS configuracion_adicional
        """
    )
