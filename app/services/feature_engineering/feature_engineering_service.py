from datetime import UTC, datetime, timedelta

from app.infrastructure.repositories.fraud_score_repository import FraudScoreRepository
from app.schemas.features import TransactionFeatures
from app.schemas.fraud import FraudScoreRequest


class FeatureEngineeringService:
    _feature_set_version = "transaction-features-v1.0.0"

    async def extract(
        self,
        request: FraudScoreRequest,
        fraud_score_repository: FraudScoreRepository,
    ) -> TransactionFeatures:
        now = datetime.now(UTC)
        last_24h = request.created_at_utc - timedelta(hours=24)
        last_30d = request.created_at_utc - timedelta(days=30)

        customer_average_amount_30d = (
            await fraud_score_repository.average_customer_amount_since_async(
                request.customer_id,
                last_30d,
            )
        )

        return TransactionFeatures(
            transaction_id=request.transaction_id,
            customer_id=request.customer_id,
            feature_set_version=self._feature_set_version,
            amount_minor=request.amount_minor,
            amount_major=request.amount_minor / 100,
            currency=request.currency.upper(),
            payment_provider=request.payment_provider,
            channel=request.channel,
            has_customer_email=request.customer_email is not None,
            has_ip_address=request.ip_address is not None,
            has_device_id=request.device_id is not None,
            is_high_amount=request.amount_minor >= 1_000_000,
            customer_transaction_count_24h=(
                await fraud_score_repository.count_customer_transactions_since_async(
                    request.customer_id,
                    last_24h,
                )
            ),
            customer_amount_sum_24h=(
                await fraud_score_repository.sum_customer_amount_since_async(
                    request.customer_id,
                    last_24h,
                )
            ),
            customer_average_amount_30d=customer_average_amount_30d,
            customer_high_risk_count_30d=(
                await fraud_score_repository.count_customer_high_risk_since_async(
                    request.customer_id,
                    last_30d,
                )
            ),
            device_transaction_count_24h=await self._count_device_transactions(
                request,
                fraud_score_repository,
                last_24h,
            ),
            ip_transaction_count_24h=await self._count_ip_transactions(
                request,
                fraud_score_repository,
                last_24h,
            ),
            amount_to_customer_average_ratio=self._get_amount_ratio(
                request.amount_minor,
                customer_average_amount_30d,
            ),
            transaction_created_at_utc=request.created_at_utc,
            extracted_at_utc=now,
        )

    @staticmethod
    async def _count_device_transactions(
        request: FraudScoreRequest,
        fraud_score_repository: FraudScoreRepository,
        since_utc: datetime,
    ) -> int:
        if request.device_id is None:
            return 0

        return await fraud_score_repository.count_device_transactions_since_async(
            request.device_id,
            since_utc,
        )

    @staticmethod
    async def _count_ip_transactions(
        request: FraudScoreRequest,
        fraud_score_repository: FraudScoreRepository,
        since_utc: datetime,
    ) -> int:
        if request.ip_address is None:
            return 0

        return await fraud_score_repository.count_ip_transactions_since_async(
            request.ip_address,
            since_utc,
        )

    @staticmethod
    def _get_amount_ratio(amount_minor: int, average_amount_minor: float) -> float:
        if average_amount_minor <= 0:
            return 0.0

        return amount_minor / average_amount_minor
