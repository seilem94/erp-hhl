"""Create the activity log for projects and expenses.

Revision ID: 3845a60b9d12
Revises: b528c7394d01
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "3845a60b9d12"
down_revision: str = "b528c7394d01"
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("actor_email", sa.String(320), nullable=False),
        sa.Column("accion", sa.String(16), nullable=False),
        sa.Column("entidad", sa.String(32), nullable=False),
        sa.Column("entidad_id", sa.String(64), nullable=False),
        sa.Column("proyecto_id", sa.Uuid(), nullable=True),
        sa.Column("resumen", sa.Text(), nullable=False),
        sa.Column("detalles", postgresql.JSONB(none_as_null=True), nullable=True),
        sa.CheckConstraint(
            "accion IN ('CREATE', 'UPDATE', 'DELETE')", name="ck_audit_logs_accion"
        ),
        sa.ForeignKeyConstraint(["proyecto_id"], ["projects.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_audit_logs_actor_email", "audit_logs", ["actor_email"])
    op.create_index("ix_audit_logs_created_at_id", "audit_logs", ["created_at", "id"])
    op.create_index("ix_audit_logs_entidad_id", "audit_logs", ["entidad_id"])
    op.create_index("ix_audit_logs_proyecto_id", "audit_logs", ["proyecto_id"])


def downgrade() -> None:
    op.drop_table("audit_logs")
