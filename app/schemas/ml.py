from pydantic import BaseModel, Field


class ModelPredictionResult(BaseModel):
    model_score: float = Field(..., ge=0, le=1)
    model_version: str
    model_features: dict[str, float | int | str | bool]