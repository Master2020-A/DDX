"""add modelo_ia to asistente_ia

Revision ID: 28b6cd113b1e
Revises: security_001
Create Date: 2025-12-15 15:15:24.370653

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql  # para UUID en Postgres


# revision identifiers, used by Alembic.
revision = "28b6cd113b1e"
down_revision = "security_001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1) Columna modelo_ia en la tabla asistente_ia
    op.add_column(
        "asistente_ia",
        sa.Column("modelo_ia", sa.String(length=100), nullable=True),
    )

    # 2) Columna diagnostico_id en la tabla recomendaciones_tratamiento
    op.add_column(
        "recomendaciones_tratamiento",
        sa.Column("diagnostico_id", postgresql.UUID(as_uuid=True), nullable=True),
    )


def downgrade() -> None:
    # Revertir cambios si haces alembic downgrade
    op.drop_column("recomendaciones_tratamiento", "diagnostico_id")
    op.drop_column("asistente_ia", "modelo_ia")
