from datetime import UTC, datetime

from app.core.config import get_settings
from app.schemas.features import TransactionFeatures
from app.schemas.fraud import FraudDecision, FraudScoreRequest, FraudScoreResponse, RiskLevel
from app.schemas.ml import ModelPredictionResult
from app.services.model_inference.model_inference_service import ModelInferenceService
from app.services.rules_engine.fraud_rules import FraudRulesEngine


class FraudScoringService:
    def __init__(
        self,
        rules_engine: FraudRulesEngine,
        model_inference_service: ModelInferenceService | None = None,
    ) -> None:
        self._rules_engine = rules_engine
        self._model_inference_service = model_inference_service
        self._settings = get_settings()

    def score(
        self,
        request: FraudScoreRequest,
        features: TransactionFeatures | None = None,
    ) -> FraudScoreResponse:
        rule_results = self._rules_engine.evaluate(request)
        rule_score = min(sum(result.score for result in rule_results), 1.0)
        model_prediction = self._predict_with_model(features)

        if model_prediction is None:
            risk_score = rule_score
            model_version = self._settings.active_model_version
            rules_triggered = [result.rule_name for result in rule_results]
            reasons = [result.reason for result in rule_results]
        else:
            risk_score = min((0.6 * rule_score) + (0.4 * model_prediction.model_score), 1.0)
            model_version = model_prediction.model_version
            rules_triggered = [result.rule_name for result in rule_results] + [
                "BaselineModelInference"
            ]
            reasons = [result.reason for result in rule_results] + [
                f"Baseline model contributed a risk score of {model_prediction.model_score:.2f}."
            ]

        risk_level = self._get_risk_level(risk_score)
        decision = self._get_decision(risk_score)

        return FraudScoreResponse(
            transaction_id=request.transaction_id,
            risk_score=risk_score,
            risk_level=risk_level,
            decision=decision,
            model_version=model_version,
            rules_triggered=rules_triggered,
            reasons=reasons,
            scored_at_utc=datetime.now(UTC),
        )

    def _predict_with_model(
        self,
        features: TransactionFeatures | None,
    ) -> ModelPredictionResult | None:
        if features is None or self._model_inference_service is None:
            return None

        return self._model_inference_service.predict(features)

    @staticmethod
    def _get_risk_level(score: float) -> RiskLevel:
        if score >= 0.85:
            return RiskLevel.critical
        if score >= 0.65:
            return RiskLevel.high
        if score >= 0.35:
            return RiskLevel.medium
        return RiskLevel.low

    @staticmethod
    def _get_decision(score: float) -> FraudDecision:
        if score >= 0.85:
            return FraudDecision.block
        if score >= 0.35:
            return FraudDecision.review
        return FraudDecision.approve
