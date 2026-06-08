import asyncio
from datetime import UTC, datetime, timedelta

from app.db.session import AsyncSessionLocal
from app.infrastructure.repositories.fraud_score_repository import FraudScoreRepository
from app.infrastructure.repositories.transaction_feature_repository import (
    TransactionFeatureRepository,
)
from app.schemas.fraud import FraudScoreRequest, TransactionChannel
from app.services.feature_engineering.feature_engineering_service import FeatureEngineeringService
from app.services.fraud_scoring.fraud_scoring_service import FraudScoringService
from app.services.model_inference.model_inference_service import ModelInferenceService
from app.services.rules_engine.fraud_rules import FraudRulesEngine

BASE_TIME = datetime(2026, 5, 22, 10, 0, tzinfo=UTC)


def build_demo_requests() -> list[FraudScoreRequest]:
    return [
        FraudScoreRequest(
            transaction_id="demo-low-001",
            customer_id="demo-customer-low",
            amount_minor=12_500,
            currency="NGN",
            payment_provider="Paystack",
            channel=TransactionChannel.card,
            customer_email="low@example.com",
            ip_address="192.0.2.10",
            device_id="demo-device-low",
            created_at_utc=BASE_TIME,
        ),
        FraudScoreRequest(
            transaction_id="demo-low-002",
            customer_id="demo-customer-low",
            amount_minor=18_000,
            currency="NGN",
            payment_provider="Paystack",
            channel=TransactionChannel.wallet,
            customer_email="low@example.com",
            ip_address="192.0.2.10",
            device_id="demo-device-low",
            created_at_utc=BASE_TIME + timedelta(minutes=20),
        ),
        FraudScoreRequest(
            transaction_id="demo-velocity-001",
            customer_id="demo-customer-velocity",
            amount_minor=95_000,
            currency="USD",
            payment_provider="Stripe",
            channel=TransactionChannel.card,
            customer_email="velocity@example.com",
            ip_address="198.51.100.44",
            device_id="demo-device-velocity",
            created_at_utc=BASE_TIME + timedelta(hours=1),
        ),
        FraudScoreRequest(
            transaction_id="demo-velocity-002",
            customer_id="demo-customer-velocity",
            amount_minor=125_000,
            currency="USD",
            payment_provider="Stripe",
            channel=TransactionChannel.card,
            customer_email="velocity@example.com",
            ip_address="198.51.100.44",
            device_id="demo-device-velocity",
            created_at_utc=BASE_TIME + timedelta(hours=1, minutes=5),
        ),
        FraudScoreRequest(
            transaction_id="demo-high-001",
            customer_id="demo-customer-risky",
            amount_minor=1_500_000,
            currency="NGN",
            payment_provider="Paystack",
            channel=TransactionChannel.card,
            customer_email=None,
            ip_address=None,
            device_id=None,
            created_at_utc=BASE_TIME + timedelta(hours=2),
        ),
        FraudScoreRequest(
            transaction_id="demo-high-002",
            customer_id="demo-customer-risky",
            amount_minor=2_100_000,
            currency="XYZ",
            payment_provider="UnknownProvider",
            channel=TransactionChannel.transfer,
            customer_email=None,
            ip_address="203.0.113.99",
            device_id="demo-device-risky",
            created_at_utc=BASE_TIME + timedelta(hours=2, minutes=15),
        ),
    ]


async def seed_demo_data() -> None:
    async with AsyncSessionLocal() as session:
        fraud_score_repository = FraudScoreRepository(session)
        transaction_feature_repository = TransactionFeatureRepository(session)
        feature_engineering_service = FeatureEngineeringService()
        scoring_service = FraudScoringService(FraudRulesEngine(), ModelInferenceService())

        for request in build_demo_requests():
            features = await feature_engineering_service.extract(request, fraud_score_repository)
            response = scoring_service.score(request, features)
            fraud_score = await fraud_score_repository.add_async(request, response)
            await transaction_feature_repository.add_async(fraud_score.id, features)

        await fraud_score_repository.commit_async()

    print("Seeded demo fraud scores and transaction features.")


if __name__ == "__main__":
    asyncio.run(seed_demo_data())
