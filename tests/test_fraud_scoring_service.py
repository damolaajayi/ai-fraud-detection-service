from datetime import UTC, datetime

import pytest

from app.schemas.features import TransactionFeatures
from app.schemas.fraud import FraudDecision, FraudScoreRequest, RiskLevel, TransactionChannel
from app.schemas.ml import ModelPredictionResult
from app.services.fraud_scoring.fraud_scoring_service import FraudScoringService
from app.services.model_inference.model_inference_service import ModelInferenceService
from app.services.rules_engine.fraud_rules import FraudRulesEngine

NOW = datetime(2026, 5, 22, 10, 0, tzinfo=UTC)


class FakeModelInferenceService:
    def predict(self, features: TransactionFeatures) -> ModelPredictionResult:
        return ModelPredictionResult(
            model_score=0.90,
            model_version="fraud-model-test-v1",
            model_features={"amount_minor": features.amount_minor},
        )


def test_rule_only_scoring_still_works_without_model() -> None:
    request = _request()

    response = FraudScoringService(FraudRulesEngine()).score(request)

    assert response.risk_score == 0.35
    assert response.risk_level == RiskLevel.medium
    assert response.decision == FraudDecision.review
    assert response.rules_triggered == ["HighAmountRule"]


def test_missing_model_file_falls_back_to_rule_score() -> None:
    request = _request()
    features = _features()
    model_service = ModelInferenceService(model_path="models/does-not-exist.pkl")

    response = FraudScoringService(FraudRulesEngine(), model_service).score(request, features)

    assert response.risk_score == 0.35
    assert response.rules_triggered == ["HighAmountRule"]


def test_hybrid_scoring_combines_rules_and_model_prediction() -> None:
    request = _request()
    features = _features()

    response = FraudScoringService(
        FraudRulesEngine(),
        FakeModelInferenceService(),
    ).score(request, features)

    assert response.risk_score == pytest.approx(0.57)
    assert response.risk_level == RiskLevel.medium
    assert response.decision == FraudDecision.review
    assert response.model_version == "fraud-model-test-v1"
    assert response.rules_triggered == ["HighAmountRule", "BaselineModelInference"]
    assert response.reasons[-1] == "Baseline model contributed a risk score of 0.90."


def _request() -> FraudScoreRequest:
    return FraudScoreRequest(
        transaction_id="txn-001",
        customer_id="cust-001",
        amount_minor=1_000_000,
        currency="NGN",
        payment_provider="Paystack",
        channel=TransactionChannel.card,
        customer_email="customer@example.com",
        ip_address="192.0.2.10",
        device_id="device-001",
        created_at_utc=NOW,
    )


def _features() -> TransactionFeatures:
    return TransactionFeatures(
        transaction_id="txn-001",
        customer_id="cust-001",
        feature_set_version="transaction-features-v1.0.0",
        amount_minor=1_000_000,
        amount_major=10_000.0,
        currency="NGN",
        payment_provider="Paystack",
        channel=TransactionChannel.card,
        has_customer_email=True,
        has_ip_address=True,
        has_device_id=True,
        is_high_amount=True,
        customer_transaction_count_24h=1,
        customer_amount_sum_24h=1_000_000,
        customer_average_amount_30d=250_000.0,
        customer_high_risk_count_30d=0,
        device_transaction_count_24h=1,
        ip_transaction_count_24h=1,
        amount_to_customer_average_ratio=4.0,
        transaction_created_at_utc=NOW,
        extracted_at_utc=NOW,
    )
