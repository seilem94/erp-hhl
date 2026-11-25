"""Store money as whole pesos and preserve expense descriptions as titles.

Revision ID: 6f4c0b9e21ad
Revises: 3845a60b9d12
"""

import sqlalchemy as sa

from alembic import op

revision: str = "6f4c0b9e21ad"
down_revision: str = "3845a60b9d12"
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.alter_column(
        "expenses",
        "description",
        new_column_name="title",
        existing_type=sa.Text(),
        type_=sa.String(),
        existing_nullable=False,
    )
    op.add_column("expenses", sa.Column("detail", sa.Text(), nullable=True))
    op.alter_column(
        "expenses",
        "amount",
        existing_type=sa.Numeric(12, 2),
        type_=sa.BigInteger(),
        existing_nullable=False,
        postgresql_using="ROUND(amount)::bigint",
    )
    op.alter_column(
        "projects",
        "budget",
        existing_type=sa.Numeric(12, 2),
        type_=sa.BigInteger(),
        existing_nullable=True,
        postgresql_using="ROUND(budget)::bigint",
    )


def downgrade() -> None:
    # PostgreSQL aborts the transaction if a value exceeds the old range.
    op.alter_column(
        "projects",
        "budget",
        existing_type=sa.BigInteger(),
        type_=sa.Numeric(12, 2),
        existing_nullable=True,
    )
    op.alter_column(
        "expenses",
        "amount",
        existing_type=sa.BigInteger(),
        type_=sa.Numeric(12, 2),
        existing_nullable=False,
    )
    op.drop_column("expenses", "detail")
    op.alter_column(
        "expenses",
        "title",
        new_column_name="description",
        existing_type=sa.String(),
        type_=sa.Text(),
        existing_nullable=False,
    )
