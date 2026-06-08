from datetime import UTC, datetime
from types import SimpleNamespace
from uuid import UUID

import pytest
from fastapi.testclient import TestClient

from app.api.v1.dependencies import (
    get_feature_engineering_service,
    get_fraud_score_repository,
    get_fraud_scoring_service,
    get_transaction_feature_repository,
)
from app.main import app
from app.schemas.features import TransactionFeatures
from app.schemas.fraud import (
    FraudDecision,
    FraudScoreRequest,
    FraudScoreResponse,
    RiskLevel,
)

SCORE_ID = UUID("11111111-1111-1111-1111-111111111111")
FEATURE_ID = UUID("22222222-2222-2222-2222-222222222222")
NOW = datetime(2026, 5, 22, 10, 0, tzinfo=UTC)


@pytest.fixture
def client() -> TestClient:
    app.dependency_overrides.clear()
    yield TestClient(app)
    app.dependency_overrides.clear()


class FakeFeatureEngineeringService:
    async def extract(
        self,
        request: FraudScoreRequest,
        fraud_score_repository: object,
    ) -> TransactionFeatures:
        return TransactionFeatures(
            transaction_id=request.transaction_id,
            customer_id=request.customer_id,
            feature_set_version="transaction-features-v1.0.0",
            amount_minor=request.amount_minor,
            amount_major=request.amount_minor / 100,
            currency=request.currency.upper(),
            payment_provider=request.payment_provider,
            channel=request.channel,
            has_customer_email=request.customer_email is not None,
            has_ip_address=request.ip_address is not None,
            has_device_id=request.device_id is not None,
            is_high_amount=request.amount_minor >= 1_000_000,
            customer_transaction_count_24h=0,
            customer_amount_sum_24h=0,
            customer_average_amount_30d=0,
            customer_high_risk_count_30d=0,
            device_transaction_count_24h=0,
            ip_transaction_count_24h=0,
            amount_to_customer_average_ratio=0,
            transaction_created_at_utc=request.created_at_utc,
            extracted_at_utc=NOW,
        )


class FakeFraudScoringService:
    def score(
        self,
        request: FraudScoreRequest,
        features: TransactionFeatures | None = None,
    ) -> FraudScoreResponse:
        return FraudScoreResponse(
            transaction_id=request.transaction_id,
            risk_score=0.35,
            risk_level=RiskLevel.medium,
            decision=FraudDecision.review,
            model_version="fraud-model-v1.0.0",
            rules_triggered=["HighAmountRule"],
            reasons=["Transaction amount is unusually high."],
            scored_at_utc=NOW,
        )


class FakeFraudScoreRepository:
    def __init__(self, record: SimpleNamespace | None = None) -> None:
        self.record = record
        self.added = False
        self.committed = False

    async def add_async(
        self,
        request: FraudScoreRequest,
        response: FraudScoreResponse,
    ) -> SimpleNamespace:
        self.added = True
        self.record = _fraud_score_record()
        return self.record

    async def commit_async(self) -> None:
        self.committed = True

    async def get_by_id_async(self, score_id: UUID) -> SimpleNamespace | None:
        return self.record if score_id == SCORE_ID else None

    async def get_latest_by_transaction_id_async(
        self,
        transaction_id: str,
    ) -> SimpleNamespace | None:
        if self.record is None or transaction_id != self.record.transaction_id:
            return None

        return self.record

    @staticmethod
    def to_response(record: SimpleNamespace) -> FraudScoreResponse:
        return FraudScoreResponse(
            score_id=record.id,
            transaction_id=record.transaction_id,
            risk_score=record.risk_score,
            risk_level=RiskLevel(record.risk_level),
            decision=FraudDecision(record.decision),
            model_version=record.model_version,
            rules_triggered=record.rules_triggered,
            reasons=record.reasons,
            scored_at_utc=record.scored_at_utc,
        )


class FakeTransactionFeatureRepository:
    def __init__(self, record: SimpleNamespace | None = None) -> None:
        self.record = record
        self.added = False

    async def add_async(
        self,
        fraud_score_id: UUID,
        features: TransactionFeatures,
    ) -> SimpleNamespace:
        self.added = True
        self.record = _transaction_feature_record()
        return self.record

    async def get_by_fraud_score_id_async(
        self,
        fraud_score_id: UUID,
    ) -> SimpleNamespace | None:
        return self.record if fraud_score_id == SCORE_ID else None

    @staticmethod
    def to_response(record: SimpleNamespace) -> dict[str, object]:
        return {
            "feature_id": record.id,
            "score_id": record.fraud_score_id,
            "transaction_id": record.transaction_id,
            "customer_id": record.customer_id,
            "feature_set_version": record.feature_set_version,
            "amount_minor": record.amount_minor,
            "amount_major": record.amount_major,
            "currency": record.currency,
            "payment_provider": record.payment_provider,
            "channel": record.channel,
            "has_customer_email": record.has_customer_email,
            "has_ip_address": record.has_ip_address,
            "has_device_id": record.has_device_id,
            "is_high_amount": record.is_high_amount,
            "customer_transaction_count_24h": record.customer_transaction_count_24h,
            "customer_amount_sum_24h": record.customer_amount_sum_24h,
            "customer_average_amount_30d": record.customer_average_amount_30d,
            "customer_high_risk_count_30d": record.customer_high_risk_count_30d,
            "device_transaction_count_24h": record.device_transaction_count_24h,
            "ip_transaction_count_24h": record.ip_transaction_count_24h,
            "amount_to_customer_average_ratio": record.amount_to_customer_average_ratio,
            "transaction_created_at_utc": record.transaction_created_at_utc,
            "extracted_at_utc": record.extracted_at_utc,
        }


def test_score_transaction_persists_score_and_features(client: TestClient) -> None:
    fraud_score_repository = FakeFraudScoreRepository()
    transaction_feature_repository = FakeTransactionFeatureRepository()
    _override_dependencies(fraud_score_repository, transaction_feature_repository)

    response = client.post("/api/v1/fraud/score", json=_score_request_payload())

    assert response.status_code == 201
    assert response.json()["score_id"] == str(SCORE_ID)
    assert fraud_score_repository.added is True
    assert fraud_score_repository.committed is True
    assert transaction_feature_repository.added is True


def test_get_score_by_id_returns_saved_score(client: TestClient) -> None:
    _override_dependencies(FakeFraudScoreRepository(_fraud_score_record()))

    response = client.get(f"/api/v1/fraud/scores/{SCORE_ID}")

    assert response.status_code == 200
    assert response.json()["score_id"] == str(SCORE_ID)
    assert response.json()["transaction_id"] == "txn-001"


def test_get_score_by_id_returns_404_when_missing(client: TestClient) -> None:
    _override_dependencies(FakeFraudScoreRepository())

    response = client.get(f"/api/v1/fraud/scores/{SCORE_ID}")

    assert response.status_code == 404


def test_get_latest_score_by_transaction_id_returns_saved_score(client: TestClient) -> None:
    _override_dependencies(FakeFraudScoreRepository(_fraud_score_record()))

    response = client.get("/api/v1/fraud/transactions/txn-001")

    assert response.status_code == 200
    assert response.json()["score_id"] == str(SCORE_ID)


def test_get_features_by_score_id_returns_saved_features(client: TestClient) -> None:
    _override_dependencies(
        FakeFraudScoreRepository(),
        FakeTransactionFeatureRepository(_transaction_feature_record()),
    )

    response = client.get(f"/api/v1/fraud/scores/{SCORE_ID}/features")

    assert response.status_code == 200
    assert response.json()["feature_id"] == str(FEATURE_ID)
    assert response.json()["score_id"] == str(SCORE_ID)
    assert response.json()["feature_set_version"] == "transaction-features-v1.0.0"


def _override_dependencies(
    fraud_score_repository: FakeFraudScoreRepository,
    transaction_feature_repository: FakeTransactionFeatureRepository | None = None,
) -> None:
    app.dependency_overrides[get_feature_engineering_service] = FakeFeatureEngineeringService
    app.dependency_overrides[get_fraud_scoring_service] = FakeFraudScoringService
    app.dependency_overrides[get_fraud_score_repository] = lambda: fraud_score_repository
    app.dependency_overrides[get_transaction_feature_repository] = (
        lambda: transaction_feature_repository or FakeTransactionFeatureRepository()
    )


def _score_request_payload() -> dict[str, object]:
    return {
        "transaction_id": "txn-001",
        "customer_id": "cust-001",
        "amount_minor": 1_000_000,
        "currency": "NGN",
        "payment_provider": "Paystack",
        "channel": "Card",
        "customer_email": "customer@example.com",
        "ip_address": "192.0.2.10",
        "device_id": "device-001",
        "created_at_utc": NOW.isoformat(),
    }


def _fraud_score_record() -> SimpleNamespace:
    return SimpleNamespace(
        id=SCORE_ID,
        transaction_id="txn-001",
        risk_score=0.35,
        risk_level="Medium",
        decision="Review",
        model_version="fraud-model-v1.0.0",
        rules_triggered=["HighAmountRule"],
        reasons=["Transaction amount is unusually high."],
        scored_at_utc=NOW,
    )


def _transaction_feature_record() -> SimpleNamespace:
    return SimpleNamespace(
        id=FEATURE_ID,
        fraud_score_id=SCORE_ID,
        transaction_id="txn-001",
        customer_id="cust-001",
        feature_set_version="transaction-features-v1.0.0",
        amount_minor=1_000_000,
        amount_major=10_000.0,
        currency="NGN",
        payment_provider="Paystack",
        channel="Card",
        has_customer_email=True,
        has_ip_address=True,
        has_device_id=True,
        is_high_amount=True,
        customer_transaction_count_24h=0,
        customer_amount_sum_24h=0,
        customer_average_amount_30d=0.0,
        customer_high_risk_count_30d=0,
        device_transaction_count_24h=0,
        ip_transaction_count_24h=0,
        amount_to_customer_average_ratio=0.0,
        transaction_created_at_utc=NOW,
        extracted_at_utc=NOW,
    )
