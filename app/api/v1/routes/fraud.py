from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.v1.dependencies import (
    get_feature_engineering_service,
    get_fraud_score_repository,
    get_fraud_scoring_service,
    get_transaction_feature_repository,
)
from app.infrastructure.repositories.fraud_score_repository import FraudScoreRepository
from app.infrastructure.repositories.transaction_feature_repository import (
    TransactionFeatureRepository,
)
from app.schemas.features import TransactionFeatureResponse
from app.schemas.fraud import FraudScoreRequest, FraudScoreResponse
from app.services.feature_engineering.feature_engineering_service import FeatureEngineeringService
from app.services.fraud_scoring.fraud_scoring_service import FraudScoringService

router = APIRouter()


@router.post(
    "/score",
    response_model=FraudScoreResponse,
    status_code=status.HTTP_201_CREATED,
)
async def score_transaction(
    request: FraudScoreRequest,
    feature_engineering_service: Annotated[
        FeatureEngineeringService,
        Depends(get_feature_engineering_service),
    ],
    scoring_service: Annotated[FraudScoringService, Depends(get_fraud_scoring_service)],
    fraud_score_repository: Annotated[
        FraudScoreRepository,
        Depends(get_fraud_score_repository),
    ],
    transaction_feature_repository: Annotated[
        TransactionFeatureRepository,
        Depends(get_transaction_feature_repository),
    ],
) -> FraudScoreResponse:
    features = await feature_engineering_service.extract(request, fraud_score_repository)
    response = scoring_service.score(request, features)

    fraud_score = await fraud_score_repository.add_async(request, response)
    await transaction_feature_repository.add_async(fraud_score.id, features)
    await fraud_score_repository.commit_async()

    return response.model_copy(update={"score_id": fraud_score.id})


@router.get("/scores/{score_id}", response_model=FraudScoreResponse)
async def get_fraud_score(
    score_id: UUID,
    fraud_score_repository: Annotated[
        FraudScoreRepository,
        Depends(get_fraud_score_repository),
    ],
) -> FraudScoreResponse:
    record = await fraud_score_repository.get_by_id_async(score_id)

    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fraud score was not found.",
        )

    return fraud_score_repository.to_response(record)


@router.get("/transactions/{transaction_id}", response_model=FraudScoreResponse)
async def get_latest_fraud_score_for_transaction(
    transaction_id: str,
    fraud_score_repository: Annotated[
        FraudScoreRepository,
        Depends(get_fraud_score_repository),
    ],
) -> FraudScoreResponse:
    record = await fraud_score_repository.get_latest_by_transaction_id_async(transaction_id)

    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fraud score was not found for this transaction.",
        )

    return fraud_score_repository.to_response(record)


@router.get("/scores/{score_id}/features", response_model=TransactionFeatureResponse)
async def get_features_for_fraud_score(
    score_id: UUID,
    transaction_feature_repository: Annotated[
        TransactionFeatureRepository,
        Depends(get_transaction_feature_repository),
    ],
) -> TransactionFeatureResponse:
    record = await transaction_feature_repository.get_by_fraud_score_id_async(score_id)

    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction features were not found for this fraud score.",
        )

    return transaction_feature_repository.to_response(record)
