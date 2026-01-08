"""merge_all_heads

Revision ID: 81ff7605dd2b
Revises: add_config_adicional_001, add_portal_paciente
Create Date: 2025-12-18 19:17:27.014694

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '81ff7605dd2b'
down_revision = ('add_config_adicional_001', 'add_portal_paciente')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
