"""add cie10 table

Revision ID: cie10_001
Revises: interconsultas_001
Create Date: 2025-12-11

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "cie10_001"
down_revision = "interconsultas_001"
branch_labels = None
depends_on = None


def upgrade():
    # Crear tabla cie10
    op.create_table(
        "cie10",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("codigo", sa.String(length=10), nullable=False),
        sa.Column("descripcion", sa.Text(), nullable=False),
        sa.Column("categoria", sa.String(length=100), nullable=True),
        sa.Column("subcategoria", sa.String(length=200), nullable=True),
        sa.Column("keywords", sa.Text(), nullable=True),
        sa.Column("sinonimos", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # Crear índices
    op.create_index("ix_cie10_codigo", "cie10", ["codigo"], unique=True)
    op.create_index("ix_cie10_categoria", "cie10", ["categoria"], unique=False)

    # Crear índices trigram para búsqueda de texto (requiere extensión pg_trgm)
    # Primero verificar/crear la extensión
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")

    # Índices GIN para búsqueda de texto
    op.execute(
        "CREATE INDEX idx_cie10_descripcion_trgm ON cie10 USING gin (descripcion gin_trgm_ops)"
    )
    op.execute(
        "CREATE INDEX idx_cie10_keywords_trgm ON cie10 USING gin (keywords gin_trgm_ops)"
    )


def downgrade():
    # Eliminar índices
    op.execute("DROP INDEX IF EXISTS idx_cie10_keywords_trgm")
    op.execute("DROP INDEX IF EXISTS idx_cie10_descripcion_trgm")
    op.drop_index("ix_cie10_categoria", table_name="cie10")
    op.drop_index("ix_cie10_codigo", table_name="cie10")

    # Eliminar tabla
    op.drop_table("cie10")
