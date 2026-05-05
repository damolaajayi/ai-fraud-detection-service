from fastapi import APIRouter

from app.schemas.fraud import FraudScoreRequest, FraudScoreResponse
from app.services.fraud_scoring.fraud_scoring_service import FraudScoringService
from app.services.rules_engine.fraud_rules import FraudRulesEngine

router = APIRouter()


@router.post("/score", response_model=FraudScoreResponse)
async def score_transaction(request: FraudScoreRequest) -> FraudScoreResponse:
    service = FraudScoringService(FraudRulesEngine())
    return service.score(request)