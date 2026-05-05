from fastapi import FastAPI

from app.api.v1.routes.health import router as health_router
from app.api.v1.routes.fraud import router as fraud_router
from app.core.config import get_settings


settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    debug=settings.debug,
)


app.include_router(health_router, tags=["Health"])
app.include_router(fraud_router, prefix="/api/v1/fraud", tags=["Fraud"])