"""create transaction features table

Revision ID: 7b2c9d4e1f60
Revises: 3eb90ad307bc
Create Date: 2026-05-17 12:30:00.000000

"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "7b2c9d4e1f60"
down_revision: str | Sequence[str] | None = "3eb90ad307bc"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "transaction_features",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("fraud_score_id", sa.UUID(), nullable=False),
        sa.Column("transaction_id", sa.String(length=100), nullable=False),
        sa.Column("customer_id", sa.String(length=100), nullable=False),
        sa.Column("feature_set_version", sa.String(length=100), nullable=False),
        sa.Column("amount_minor", sa.Integer(), nullable=False),
        sa.Column("amount_major", sa.Float(), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("payment_provider", sa.String(length=50), nullable=False),
        sa.Column("channel", sa.String(length=50), nullable=False),
        sa.Column("has_customer_email", sa.Boolean(), nullable=False),
        sa.Column("has_ip_address", sa.Boolean(), nullable=False),
        sa.Column("has_device_id", sa.Boolean(), nullable=False),
        sa.Column("is_high_amount", sa.Boolean(), nullable=False),
        sa.Column("customer_transaction_count_24h", sa.Integer(), nullable=False),
        sa.Column("customer_amount_sum_24h", sa.Integer(), nullable=False),
        sa.Column("customer_average_amount_30d", sa.Float(), nullable=False),
        sa.Column("customer_high_risk_count_30d", sa.Integer(), nullable=False),
        sa.Column("device_transaction_count_24h", sa.Integer(), nullable=False),
        sa.Column("ip_transaction_count_24h", sa.Integer(), nullable=False),
        sa.Column("amount_to_customer_average_ratio", sa.Float(), nullable=False),
        sa.Column("transaction_created_at_utc", sa.DateTime(timezone=True), nullable=False),
        sa.Column("extracted_at_utc", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at_utc", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at_utc", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["fraud_score_id"],
            ["fraud_scores.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_transaction_features_customer_id"),
        "transaction_features",
        ["customer_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_transaction_features_fraud_score_id"),
        "transaction_features",
        ["fraud_score_id"],
        unique=True,
    )
    op.create_index(
        op.f("ix_transaction_features_transaction_id"),
        "transaction_features",
        ["transaction_id"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(
        op.f("ix_transaction_features_transaction_id"),
        table_name="transaction_features",
    )
    op.drop_index(
        op.f("ix_transaction_features_fraud_score_id"),
        table_name="transaction_features",
    )
    op.drop_index(
        op.f("ix_transaction_features_customer_id"),
        table_name="transaction_features",
    )
    op.drop_table("transaction_features")
