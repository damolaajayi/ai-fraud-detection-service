import asyncio
import json
from datetime import UTC, datetime
from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split

from app.db.session import AsyncSessionLocal
from app.infrastructure.repositories.transaction_feature_repository import (
    TransactionFeatureRepository,
)


MODEL_VERSION = "fraud-model-v1.0.0"

BASE_DIR = Path(__file__).resolve().parents[1]
MODEL_DIR = BASE_DIR / "models"
MODEL_PATH = MODEL_DIR / "fraud_model_v1.pkl"
METADATA_PATH = MODEL_DIR / "fraud_model_v1_metadata.json"


FEATURE_COLUMNS = [
    "amount_minor",
    "is_missing_device_id",
    "is_missing_ip_address",
    "is_missing_customer_email",
    "customer_transaction_count_24h",
    "customer_total_amount_24h",
    "customer_average_amount_24h",
    "amount_to_customer_average_ratio",
    "customer_high_risk_count_24h",
    "device_transaction_count_24h",
    "ip_transaction_count_1h",
]


def create_label(row: pd.Series) -> int:
    """
    Temporary weak label.

    Since we do not have confirmed fraud labels yet, we create a baseline label
    from existing rule/model-like signals.

    Later, this should be replaced with real fraud labels:
    - confirmed_fraud
    - chargeback
    - manual_review_result
    - customer_dispute
    """
    if row["customer_high_risk_count_24h"] >= 2:
        return 1

    if row["amount_to_customer_average_ratio"] >= 3:
        return 1

    if row["ip_transaction_count_1h"] >= 5:
        return 1

    if row["device_transaction_count_24h"] >= 5:
        return 1

    if row["amount_minor"] >= 1_000_000:
        return 1

    return 0


async def load_training_dataframe() -> pd.DataFrame:
    async with AsyncSessionLocal() as session:
        repository = TransactionFeatureRepository(session)
        records = await repository.list_for_training_async()

    rows = []

    for record in records:
        rows.append(
            {
                "amount_minor": record.amount_minor,
                "is_missing_device_id": int(record.is_missing_device_id),
                "is_missing_ip_address": int(record.is_missing_ip_address),
                "is_missing_customer_email": int(record.is_missing_customer_email),
                "customer_transaction_count_24h": record.customer_transaction_count_24h,
                "customer_total_amount_24h": record.customer_total_amount_24h,
                "customer_average_amount_24h": record.customer_average_amount_24h,
                "amount_to_customer_average_ratio": record.amount_to_customer_average_ratio,
                "customer_high_risk_count_24h": record.customer_high_risk_count_24h,
                "device_transaction_count_24h": record.device_transaction_count_24h,
                "ip_transaction_count_1h": record.ip_transaction_count_1h,
            }
        )

    return pd.DataFrame(rows)


async def main() -> None:
    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    dataframe = await load_training_dataframe()

    if dataframe.empty:
        raise RuntimeError(
            "No transaction features found. Score some transactions before training the model."
        )

    dataframe["label"] = dataframe.apply(create_label, axis=1)

    if dataframe["label"].nunique() < 2:
        raise RuntimeError(
            "Training data has only one class. Add both low-risk and high-risk sample transactions."
        )

    x = dataframe[FEATURE_COLUMNS]
    y = dataframe["label"]

    x_train, x_test, y_train, y_test = train_test_split(
        x,
        y,
        test_size=0.25,
        random_state=42,
        stratify=y,
    )

    model = RandomForestClassifier(
        n_estimators=100,
        random_state=42,
        class_weight="balanced",
    )

    model.fit(x_train, y_train)

    y_pred = model.predict(x_test)

    report = classification_report(
        y_test,
        y_pred,
        output_dict=True,
        zero_division=0,
    )

    model_package = {
        "model": model,
        "feature_columns": FEATURE_COLUMNS,
        "model_version": MODEL_VERSION,
    }

    joblib.dump(model_package, MODEL_PATH)

    metadata = {
        "model_version": MODEL_VERSION,
        "trained_at_utc": datetime.now(UTC).isoformat(),
        "training_records": int(len(dataframe)),
        "feature_columns": FEATURE_COLUMNS,
        "metrics": report,
        "label_strategy": "weak_labels_from_rule_based_signals",
    }

    METADATA_PATH.write_text(
        json.dumps(metadata, indent=2),
        encoding="utf-8",
    )

    print(f"Model saved to: {MODEL_PATH}")
    print(f"Metadata saved to: {METADATA_PATH}")
    print(json.dumps(metadata, indent=2))


if __name__ == "__main__":
    asyncio.run(main())