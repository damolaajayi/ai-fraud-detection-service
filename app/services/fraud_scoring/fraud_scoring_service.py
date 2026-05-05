from datetime import UTC, datetime

from app.core.config import get_settings
from app.schemas.fraud import FraudDecision, FraudScoreRequest, FraudScoreResponse, RiskLevel
from app.services.rules_engine.fraud_rules import FraudRulesEngine


class FraudScoringService:
    def __init__(self, rules_engine: FraudRulesEngine) -> None:
        self._rules_engine = rules_engine
        self._settings = get_settings()

    def score(self, request: FraudScoreRequest) -> FraudScoreResponse:
        rule_results = self._rules_engine.evaluate(request)

        risk_score = min(sum(result.score for result in rule_results), 1.0)

        risk_level = self._get_risk_level(risk_score)
        decision = self._get_decision(risk_score)

        return FraudScoreResponse(
            transaction_id=request.transaction_id,
            risk_score=risk_score,
            risk_level=risk_level,
            decision=decision,
            model_version=self._settings.active_model_version,
            rules_triggered=[result.rule_name for result in rule_results],
            reasons=[result.reason for result in rule_results],
            scored_at_utc=datetime.now(UTC),
        )

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