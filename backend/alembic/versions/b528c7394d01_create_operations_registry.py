"""Create the persistent operation registry and preserve payload-free confirmations.

Revision ID: b528c7394d01
Revises: a417b6283c90
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "b528c7394d01"
down_revision: str = "a417b6283c90"
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.create_table(
        "operations",
        sa.Column("actor_id", sa.Uuid(), nullable=False),
        sa.Column("operation_id", sa.Uuid(), nullable=False),
        sa.Column("command_type", sa.String(50), nullable=False),
        sa.Column("resource_type", sa.String(24), nullable=False),
        sa.Column("target_resource_id", sa.Uuid(), nullable=True),
        sa.Column("fingerprint_version", sa.Integer(), nullable=False),
        sa.Column("command_version", sa.Integer(), nullable=False),
        sa.Column("request_fingerprint", sa.String(64), nullable=False),
        sa.Column("state", sa.String(16), nullable=False),
        sa.Column("reserved_in_transaction", sa.BigInteger(), nullable=False),
        sa.Column("result_resource_id", sa.Uuid(), nullable=True),
        sa.Column("result_schema_version", sa.Integer(), nullable=True),
        sa.Column("result_payload", postgresql.JSONB(none_as_null=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("actor_id", "operation_id"),
        sa.CheckConstraint(
            "state IN ('reserved', 'confirmed')", name="ck_operations_state"
        ),
        sa.CheckConstraint(
            "(command_type = 'register_expense' AND resource_type = 'expense') OR "
            "(command_type IN ('create_project', 'update_project') "
            "AND resource_type = 'project')",
            name="ck_operations_command_resource",
        ),
        sa.CheckConstraint(
            "fingerprint_version > 0 AND command_version > 0",
            name="ck_operations_versions",
        ),
        sa.CheckConstraint(
            "length(request_fingerprint) = 64",
            name="ck_operations_fingerprint_length",
        ),
        sa.CheckConstraint(
            "reserved_in_transaction > 0", name="ck_operations_owner_transaction"
        ),
        sa.CheckConstraint(
            "command_type <> 'update_project' OR target_resource_id IS NOT NULL",
            name="ck_operations_update_target",
        ),
        sa.CheckConstraint(
            "(state = 'reserved' AND result_resource_id IS NULL "
            "AND result_schema_version IS NULL AND result_payload IS NULL "
            "AND completed_at IS NULL) OR "
            "(state = 'confirmed' AND result_resource_id IS NOT NULL "
            "AND result_schema_version IS NOT NULL AND result_schema_version > 0 "
            "AND completed_at IS NOT NULL)",
            name="ck_operations_confirmation_shape",
        ),
        sa.CheckConstraint(
            "state <> 'confirmed' OR target_resource_id IS NULL "
            "OR target_resource_id = result_resource_id",
            name="ck_operations_target_result",
        ),
    )


def downgrade() -> None:
    op.drop_table("operations")
