from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class TransactionChannel(StrEnum):
    card = "Card"
    transfer = "Transfer"
    ussd = "USSD"
    wallet = "Wallet"


class RiskLevel(StrEnum):
    low = "Low"
    medium = "Medium"
    high = "High"
    critical = "Critical"


class FraudDecision(StrEnum):
    approve = "Approve"
    review = "Review"
    block = "Block"


class FraudScoreRequest(BaseModel):
    transaction_id: str = Field(..., min_length=3, max_length=100)
    customer_id: str = Field(..., min_length=3, max_length=100)
    amount_minor: int = Field(..., gt=0)
    currency: str = Field(..., min_length=3, max_length=3)
    payment_provider: str = Field(..., min_length=2, max_length=50)
    channel: TransactionChannel
    customer_email: str | None = None
    ip_address: str | None = None
    device_id: str | None = None
    created_at_utc: datetime


class FraudScoreResponse(BaseModel):
    transaction_id: str
    risk_score: float = Field(..., ge=0, le=1)
    risk_level: RiskLevel
    decision: FraudDecision
    model_version: str
    rules_triggered: list[str]
    reasons: list[str]
    scored_at_utc: datetime