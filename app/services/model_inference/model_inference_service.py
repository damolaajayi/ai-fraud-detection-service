from pathlib import Path
from typing import Any

import joblib

from app.core.config import get_settings
from app.schemas.features import TransactionFeatures
from app.schemas.ml import ModelPredictionResult


class ModelInferenceService:
    def __init__(self, model_path: str | None = None) -> None:
        settings = get_settings()
        self._model_path = self._resolve_model_path(model_path or settings.model_path)
        self._active_model_version = settings.active_model_version
        self._model_package: dict[str, Any] | None = None
        self._load_attempted = False

    def predict(self, features: TransactionFeatures) -> ModelPredictionResult | None:
        model_package = self._load_model_package()

        if model_package is None:
            return None

        feature_columns = model_package["feature_columns"]
        feature_values = self._to_model_features(features)
        model_input = [[feature_values[column] for column in feature_columns]]
        model = model_package["model"]

        if hasattr(model, "predict_proba"):
            model_score = float(model.predict_proba(model_input)[0][1])
        else:
            model_score = float(model.predict(model_input)[0])

        return ModelPredictionResult(
            model_score=max(0.0, min(model_score, 1.0)),
            model_version=str(model_package.get("model_version", self._active_model_version)),
            model_features={column: feature_values[column] for column in feature_columns},
        )

    def _load_model_package(self) -> dict[str, Any] | None:
        if self._model_package is not None:
            return self._model_package

        if self._load_attempted:
            return None

        self._load_attempted = True

        if not self._model_path.exists():
            return None

        package = joblib.load(self._model_path)

        if (
            not isinstance(package, dict)
            or "model" not in package
            or "feature_columns" not in package
        ):
            return None

        self._model_package = package
        return self._model_package

    @staticmethod
    def _to_model_features(features: TransactionFeatures) -> dict[str, float | int]:
        return {
            "amount_minor": features.amount_minor,
            "amount_major": features.amount_major,
            "has_customer_email": int(features.has_customer_email),
            "has_ip_address": int(features.has_ip_address),
            "has_device_id": int(features.has_device_id),
            "is_high_amount": int(features.is_high_amount),
            "customer_transaction_count_24h": features.customer_transaction_count_24h,
            "customer_amount_sum_24h": features.customer_amount_sum_24h,
            "customer_average_amount_30d": features.customer_average_amount_30d,
            "customer_high_risk_count_30d": features.customer_high_risk_count_30d,
            "device_transaction_count_24h": features.device_transaction_count_24h,
            "ip_transaction_count_24h": features.ip_transaction_count_24h,
            "amount_to_customer_average_ratio": features.amount_to_customer_average_ratio,
        }

    @staticmethod
    def _resolve_model_path(model_path: str) -> Path:
        path = Path(model_path)

        if path.is_absolute():
            return path

        return Path(__file__).resolve().parents[3] / path
