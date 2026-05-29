from datetime import UTC, datetime

from app.schemas.fraud import FraudScoreRequest, TransactionChannel
from app.services.rules_engine.fraud_rules import FraudRulesEngine


def test_rules_engine_flags_high_amount_and_missing_identifiers() -> None:
    request = FraudScoreRequest(
        transaction_id="txn-001",
        customer_id="cust-001",
        amount_minor=1_200_000,
        currency="NGN",
        payment_provider="Paystack",
        channel=TransactionChannel.card,
        customer_email="customer@example.com",
        ip_address=None,
        device_id=None,
        created_at_utc=datetime(2026, 5, 22, 10, 0, tzinfo=UTC),
    )

    results = FraudRulesEngine().evaluate(request)

    assert [result.rule_name for result in results] == [
        "HighAmountRule",
        "MissingDeviceRule",
        "MissingIpAddressRule",
    ]
    assert sum(result.score for result in results) == 0.60
