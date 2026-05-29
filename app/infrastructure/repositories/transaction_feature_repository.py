from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database.transaction_feature import TransactionFeatureRecord
from app.schemas.features import TransactionFeatureResponse, TransactionFeatures


class TransactionFeatureRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add_async(
        self,
        fraud_score_id: UUID,
        features: TransactionFeatures,
    ) -> TransactionFeatureRecord:
        record = TransactionFeatureRecord(
            fraud_score_id=fraud_score_id,
            transaction_id=features.transaction_id,
            customer_id=features.customer_id,
            feature_set_version=features.feature_set_version,
            amount_minor=features.amount_minor,
            amount_major=features.amount_major,
            currency=features.currency,
            payment_provider=features.payment_provider,
            channel=features.channel.value,
            has_customer_email=features.has_customer_email,
            has_ip_address=features.has_ip_address,
            has_device_id=features.has_device_id,
            is_high_amount=features.is_high_amount,
            customer_transaction_count_24h=features.customer_transaction_count_24h,
            customer_amount_sum_24h=features.customer_amount_sum_24h,
            customer_average_amount_30d=features.customer_average_amount_30d,
            customer_high_risk_count_30d=features.customer_high_risk_count_30d,
            device_transaction_count_24h=features.device_transaction_count_24h,
            ip_transaction_count_24h=features.ip_transaction_count_24h,
            amount_to_customer_average_ratio=features.amount_to_customer_average_ratio,
            transaction_created_at_utc=features.transaction_created_at_utc,
            extracted_at_utc=features.extracted_at_utc,
        )

        self._session.add(record)
        await self._session.flush()

        return record

    async def get_by_fraud_score_id_async(
        self,
        fraud_score_id: UUID,
    ) -> TransactionFeatureRecord | None:
        result = await self._session.execute(
            select(TransactionFeatureRecord).where(
                TransactionFeatureRecord.fraud_score_id == fraud_score_id
            )
        )

        return result.scalar_one_or_none()

    @staticmethod
    def to_response(record: TransactionFeatureRecord) -> TransactionFeatureResponse:
        return TransactionFeatureResponse(
            feature_id=record.id,
            score_id=record.fraud_score_id,
            transaction_id=record.transaction_id,
            customer_id=record.customer_id,
            feature_set_version=record.feature_set_version,
            amount_minor=record.amount_minor,
            amount_major=record.amount_major,
            currency=record.currency,
            payment_provider=record.payment_provider,
            channel=record.channel,
            has_customer_email=record.has_customer_email,
            has_ip_address=record.has_ip_address,
            has_device_id=record.has_device_id,
            is_high_amount=record.is_high_amount,
            customer_transaction_count_24h=record.customer_transaction_count_24h,
            customer_amount_sum_24h=record.customer_amount_sum_24h,
            customer_average_amount_30d=record.customer_average_amount_30d,
            customer_high_risk_count_30d=record.customer_high_risk_count_30d,
            device_transaction_count_24h=record.device_transaction_count_24h,
            ip_transaction_count_24h=record.ip_transaction_count_24h,
            amount_to_customer_average_ratio=record.amount_to_customer_average_ratio,
            transaction_created_at_utc=record.transaction_created_at_utc,
            extracted_at_utc=record.extracted_at_utc,
        )
