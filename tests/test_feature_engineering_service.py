from datetime import UTC, datetime

import pytest

from app.schemas.fraud import FraudScoreRequest, TransactionChannel
from app.services.feature_engineering.feature_engineering_service import (
    FeatureEngineeringService,
)


class FakeFraudScoreRepository:
    async def average_customer_amount_since_async(
        self,
        customer_id: str,
        since_utc: datetime,
    ) -> float:
        return 50_000.0

    async def count_customer_transactions_since_async(
        self,
        customer_id: str,
        since_utc: datetime,
    ) -> int:
        return 3

    async def sum_customer_amount_since_async(
        self,
        customer_id: str,
        since_utc: datetime,
    ) -> int:
        return 150_000

    async def count_customer_high_risk_since_async(
        self,
        customer_id: str,
        since_utc: datetime,
    ) -> int:
        return 1

    async def count_device_transactions_since_async(
        self,
        device_id: str,
        since_utc: datetime,
    ) -> int:
        return 2

    async def count_ip_transactions_since_async(
        self,
        ip_address: str,
        since_utc: datetime,
    ) -> int:
        return 4


@pytest.mark.asyncio
async def test_extract_builds_ml_ready_transaction_features() -> None:
    request = FraudScoreRequest(
        transaction_id="txn-001",
        customer_id="cust-001",
        amount_minor=100_000,
        currency="ngn",
        payment_provider="Paystack",
        channel=TransactionChannel.card,
        customer_email="customer@example.com",
        ip_address="192.0.2.10",
        device_id="device-001",
        created_at_utc=datetime(2026, 5, 22, 10, 0, tzinfo=UTC),
    )

    features = await FeatureEngineeringService().extract(
        request,
        FakeFraudScoreRepository(),
    )

    assert features.feature_set_version == "transaction-features-v1.0.0"
    assert features.currency == "NGN"
    assert features.amount_major == 1000.0
    assert features.has_customer_email is True
    assert features.has_ip_address is True
    assert features.has_device_id is True
    assert features.customer_transaction_count_24h == 3
    assert features.customer_amount_sum_24h == 150_000
    assert features.customer_average_amount_30d == 50_000.0
    assert features.customer_high_risk_count_30d == 1
    assert features.device_transaction_count_24h == 2
    assert features.ip_transaction_count_24h == 4
    assert features.amount_to_customer_average_ratio == 2.0
