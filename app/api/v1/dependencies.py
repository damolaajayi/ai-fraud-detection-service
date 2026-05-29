from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.infrastructure.repositories.fraud_score_repository import FraudScoreRepository
from app.infrastructure.repositories.transaction_feature_repository import (
    TransactionFeatureRepository,
)
from app.services.feature_engineering.feature_engineering_service import FeatureEngineeringService
from app.services.fraud_scoring.fraud_scoring_service import FraudScoringService
from app.services.rules_engine.fraud_rules import FraudRulesEngine


async def get_fraud_score_repository(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> FraudScoreRepository:
    return FraudScoreRepository(session)


async def get_transaction_feature_repository(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> TransactionFeatureRepository:
    return TransactionFeatureRepository(session)


def get_feature_engineering_service() -> FeatureEngineeringService:
    return FeatureEngineeringService()


def get_fraud_scoring_service() -> FraudScoringService:
    return FraudScoringService(FraudRulesEngine())
