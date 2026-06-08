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
from app.models.database.transaction_feature import TransactionFeatureRecord

MODEL_VERSION = "fraud-model-v1.0.0"

BASE_DIR = Path(__file__).resolve().parents[1]
MODEL_DIR = BASE_DIR / "models"
MODEL_PATH = MODEL_DIR / "fraud_model_v1.pkl"
METADATA_PATH = MODEL_DIR / "fraud_model_v1_metadata.json"

FEATURE_COLUMNS = [
    "amount_minor",
    "amount_major",
    "has_customer_email",
    "has_ip_address",
    "has_device_id",
    "is_high_amount",
    "customer_transaction_count_24h",
    "customer_amount_sum_24h",
    "customer_average_amount_30d",
    "customer_high_risk_count_30d",
    "device_transaction_count_24h",
    "ip_transaction_count_24h",
    "amount_to_customer_average_ratio",
]


def create_weak_label(row: pd.Series) -> int:
    if row["is_high_amount"]:
        return 1

    if row["customer_high_risk_count_30d"] >= 1:
        return 1

    if row["amount_to_customer_average_ratio"] >= 3:
        return 1

    if row["device_transaction_count_24h"] >= 4:
        return 1

    if row["ip_transaction_count_24h"] >= 4:
        return 1

    return 0


def record_to_row(record: TransactionFeatureRecord) -> dict[str, float | int]:
    return {
        "amount_minor": record.amount_minor,
        "amount_major": record.amount_major,
        "has_customer_email": int(record.has_customer_email),
        "has_ip_address": int(record.has_ip_address),
        "has_device_id": int(record.has_device_id),
        "is_high_amount": int(record.is_high_amount),
        "customer_transaction_count_24h": record.customer_transaction_count_24h,
        "customer_amount_sum_24h": record.customer_amount_sum_24h,
        "customer_average_amount_30d": record.customer_average_amount_30d,
        "customer_high_risk_count_30d": record.customer_high_risk_count_30d,
        "device_transaction_count_24h": record.device_transaction_count_24h,
        "ip_transaction_count_24h": record.ip_transaction_count_24h,
        "amount_to_customer_average_ratio": record.amount_to_customer_average_ratio,
    }


async def load_training_dataframe() -> pd.DataFrame:
    async with AsyncSessionLocal() as session:
        repository = TransactionFeatureRepository(session)
        records = await repository.list_for_training_async()

    return pd.DataFrame([record_to_row(record) for record in records])


def train_model(dataframe: pd.DataFrame) -> tuple[dict[str, object], dict[str, object]]:
    if dataframe.empty:
        raise RuntimeError(
            "No transaction features found. Run `python scripts/seed_demo_data.py` "
            "or score transactions before training."
        )

    dataframe["label"] = dataframe.apply(create_weak_label, axis=1)

    if dataframe["label"].nunique() < 2:
        raise RuntimeError(
            "Training data has only one label class. Add both low-risk and high-risk examples."
        )

    x = dataframe[FEATURE_COLUMNS]
    y = dataframe["label"]

    stratify = y if y.value_counts().min() >= 2 else None
    x_train, x_test, y_train, y_test = train_test_split(
        x,
        y,
        test_size=0.30,
        random_state=42,
        stratify=stratify,
    )

    model = RandomForestClassifier(
        n_estimators=100,
        random_state=42,
        class_weight="balanced",
    )
    model.fit(x_train, y_train)

    report = classification_report(
        y_test,
        model.predict(x_test),
        output_dict=True,
        zero_division=0,
    )

    model_package: dict[str, object] = {
        "model": model,
        "feature_columns": FEATURE_COLUMNS,
        "model_version": MODEL_VERSION,
    }
    metadata: dict[str, object] = {
        "model_version": MODEL_VERSION,
        "trained_at_utc": datetime.now(UTC).isoformat(),
        "training_records": int(len(dataframe)),
        "positive_labels": int(dataframe["label"].sum()),
        "negative_labels": int((dataframe["label"] == 0).sum()),
        "feature_columns": FEATURE_COLUMNS,
        "metrics": report,
        "label_strategy": "weak_labels_from_feature_and_rule_signals",
    }

    return model_package, metadata


async def main() -> None:
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    dataframe = await load_training_dataframe()
    model_package, metadata = train_model(dataframe)

    joblib.dump(model_package, MODEL_PATH)
    METADATA_PATH.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    print(f"Model saved to: {MODEL_PATH}")
    print(f"Metadata saved to: {METADATA_PATH}")
    print(json.dumps(metadata, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
