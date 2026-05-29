from datetime import datetime
from uuid import UUID

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database.fraud_score import FraudScoreRecord
from app.schemas.fraud import (
    FraudDecision,
    FraudScoreRequest,
    FraudScoreResponse,
    RiskLevel,
)


class FraudScoreRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add_async(
        self,
        request: FraudScoreRequest,
        response: FraudScoreResponse,
    ) -> FraudScoreRecord:
        record = FraudScoreRecord(
            transaction_id=request.transaction_id,
            customer_id=request.customer_id,
            amount_minor=request.amount_minor,
            currency=request.currency.upper(),
            payment_provider=request.payment_provider,
            channel=request.channel.value,
            customer_email=request.customer_email,
            ip_address=request.ip_address,
            device_id=request.device_id,
            risk_score=response.risk_score,
            risk_level=response.risk_level.value,
            decision=response.decision.value,
            model_version=response.model_version,
            rules_triggered=response.rules_triggered,
            reasons=response.reasons,
            transaction_created_at_utc=request.created_at_utc,
            scored_at_utc=response.scored_at_utc,
        )

        self._session.add(record)
        await self._session.flush()

        return record

    async def commit_async(self) -> None:
        await self._session.commit()

    async def get_by_id_async(self, score_id: UUID) -> FraudScoreRecord | None:
        result = await self._session.execute(
            select(FraudScoreRecord).where(FraudScoreRecord.id == score_id)
        )

        return result.scalar_one_or_none()

    async def get_latest_by_transaction_id_async(
        self,
        transaction_id: str,
    ) -> FraudScoreRecord | None:
        result = await self._session.execute(
            select(FraudScoreRecord)
            .where(FraudScoreRecord.transaction_id == transaction_id)
            .order_by(desc(FraudScoreRecord.scored_at_utc))
            .limit(1)
        )

        return result.scalar_one_or_none()

    async def count_customer_transactions_since_async(
        self,
        customer_id: str,
        since_utc: datetime,
    ) -> int:
        result = await self._session.execute(
            select(func.count())
            .select_from(FraudScoreRecord)
            .where(FraudScoreRecord.customer_id == customer_id)
            .where(FraudScoreRecord.transaction_created_at_utc >= since_utc)
        )

        return int(result.scalar_one())

    async def sum_customer_amount_since_async(
        self,
        customer_id: str,
        since_utc: datetime,
    ) -> int:
        result = await self._session.execute(
            select(func.coalesce(func.sum(FraudScoreRecord.amount_minor), 0))
            .where(FraudScoreRecord.customer_id == customer_id)
            .where(FraudScoreRecord.transaction_created_at_utc >= since_utc)
        )

        return int(result.scalar_one())

    async def average_customer_amount_since_async(
        self,
        customer_id: str,
        since_utc: datetime,
    ) -> float:
        result = await self._session.execute(
            select(func.coalesce(func.avg(FraudScoreRecord.amount_minor), 0))
            .where(FraudScoreRecord.customer_id == customer_id)
            .where(FraudScoreRecord.transaction_created_at_utc >= since_utc)
        )

        return float(result.scalar_one())

    async def count_customer_high_risk_since_async(
        self,
        customer_id: str,
        since_utc: datetime,
    ) -> int:
        result = await self._session.execute(
            select(func.count())
            .select_from(FraudScoreRecord)
            .where(FraudScoreRecord.customer_id == customer_id)
            .where(FraudScoreRecord.transaction_created_at_utc >= since_utc)
            .where(FraudScoreRecord.risk_level.in_(["High", "Critical"]))
        )

        return int(result.scalar_one())

    async def count_device_transactions_since_async(
        self,
        device_id: str,
        since_utc: datetime,
    ) -> int:
        result = await self._session.execute(
            select(func.count())
            .select_from(FraudScoreRecord)
            .where(FraudScoreRecord.device_id == device_id)
            .where(FraudScoreRecord.transaction_created_at_utc >= since_utc)
        )

        return int(result.scalar_one())

    async def count_ip_transactions_since_async(
        self,
        ip_address: str,
        since_utc: datetime,
    ) -> int:
        result = await self._session.execute(
            select(func.count())
            .select_from(FraudScoreRecord)
            .where(FraudScoreRecord.ip_address == ip_address)
            .where(FraudScoreRecord.transaction_created_at_utc >= since_utc)
        )

        return int(result.scalar_one())

    @staticmethod
    def to_response(record: FraudScoreRecord) -> FraudScoreResponse:
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
