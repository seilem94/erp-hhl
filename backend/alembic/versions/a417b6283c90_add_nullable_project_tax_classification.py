"""Add explicit project tax classification without inventing historical values.

Revision ID: a417b6283c90
Revises: dd79d22101bf
"""

import sqlalchemy as sa

from alembic import op

revision: str = "a417b6283c90"
down_revision: str = "dd79d22101bf"
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.add_column("projects", sa.Column("has_iva", sa.Boolean(), nullable=True))


def downgrade() -> None:
    op.drop_column("projects", "has_iva")
