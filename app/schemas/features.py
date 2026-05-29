from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.fraud import TransactionChannel


class TransactionFeatures(BaseModel):
    transaction_id: str
    customer_id: str
    feature_set_version: str
    amount_minor: int = Field(..., gt=0)
    amount_major: float = Field(..., gt=0)
    currency: str
    payment_provider: str
    channel: TransactionChannel
    has_customer_email: bool
    has_ip_address: bool
    has_device_id: bool
    is_high_amount: bool
    customer_transaction_count_24h: int = Field(default=0, ge=0)
    customer_amount_sum_24h: int = Field(default=0, ge=0)
    customer_average_amount_30d: float = Field(default=0, ge=0)
    customer_high_risk_count_30d: int = Field(default=0, ge=0)
    device_transaction_count_24h: int = Field(default=0, ge=0)
    ip_transaction_count_24h: int = Field(default=0, ge=0)
    amount_to_customer_average_ratio: float = Field(default=0, ge=0)
    transaction_created_at_utc: datetime
    extracted_at_utc: datetime


class TransactionFeatureResponse(TransactionFeatures):
    feature_id: UUID
    score_id: UUID
