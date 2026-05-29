from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.database.mixins import TimestampMixin


class TransactionFeatureRecord(Base, TimestampMixin):
    __tablename__ = "transaction_features"

    id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    fraud_score_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        ForeignKey("fraud_scores.id", ondelete="CASCADE"),
        unique=True,
        index=True,
        nullable=False,
    )

    transaction_id: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    customer_id: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    feature_set_version: Mapped[str] = mapped_column(String(100), nullable=False)

    amount_minor: Mapped[int] = mapped_column(Integer, nullable=False)
    amount_major: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    payment_provider: Mapped[str] = mapped_column(String(50), nullable=False)
    channel: Mapped[str] = mapped_column(String(50), nullable=False)

    has_customer_email: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_ip_address: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_device_id: Mapped[bool] = mapped_column(Boolean, nullable=False)
    is_high_amount: Mapped[bool] = mapped_column(Boolean, nullable=False)

    customer_transaction_count_24h: Mapped[int] = mapped_column(Integer, nullable=False)
    customer_amount_sum_24h: Mapped[int] = mapped_column(Integer, nullable=False)
    customer_average_amount_30d: Mapped[float] = mapped_column(Float, nullable=False)
    customer_high_risk_count_30d: Mapped[int] = mapped_column(Integer, nullable=False)
    device_transaction_count_24h: Mapped[int] = mapped_column(Integer, nullable=False)
    ip_transaction_count_24h: Mapped[int] = mapped_column(Integer, nullable=False)
    amount_to_customer_average_ratio: Mapped[float] = mapped_column(Float, nullable=False)

    transaction_created_at_utc: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    extracted_at_utc: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
