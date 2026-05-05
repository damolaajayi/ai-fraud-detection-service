from dataclasses import dataclass

from app.schemas.fraud import FraudScoreRequest


@dataclass(frozen=True)
class RuleResult:
    rule_name: str
    score: float
    reason: str


class FraudRulesEngine:
    def evaluate(self, request: FraudScoreRequest) -> list[RuleResult]:
        results: list[RuleResult] = []

        if request.amount_minor >= 1_000_000:
            results.append(
                RuleResult(
                    rule_name="HighAmountRule",
                    score=0.35,
                    reason="Transaction amount is unusually high.",
                )
            )

        if request.currency.upper() not in {"NGN", "USD", "GBP", "EUR"}:
            results.append(
                RuleResult(
                    rule_name="UnsupportedCurrencyRule",
                    score=0.25,
                    reason="Transaction currency is outside the supported low-risk currency set.",
                )
            )

        if request.device_id is None:
            results.append(
                RuleResult(
                    rule_name="MissingDeviceRule",
                    score=0.15,
                    reason="Device identifier is missing.",
                )
            )

        if request.ip_address is None:
            results.append(
                RuleResult(
                    rule_name="MissingIpAddressRule",
                    score=0.10,
                    reason="IP address is missing.",
                )
            )

        return results