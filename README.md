# ai-fraud-detection-service

Production-minded fraud detection backend built with FastAPI, PostgreSQL, async SQLAlchemy, Alembic, rule-based scoring, feature engineering, and a simple baseline ML pipeline.

## Why This Project Exists

This project shows how a fraud scoring service can be structured beyond a notebook demo. It receives transaction data, extracts reusable fraud features, applies explainable rules, optionally blends in a trained ML model score, stores the score and feature snapshot, and exposes retrieval endpoints for auditability.

It is intentionally scoped for a portfolio project: practical, readable, and ML-ready without adding cloud deployment, authentication, Kubernetes, or heavyweight ML infrastructure too early.

## Architecture

```text
Client
  -> FastAPI Route
  -> Feature Engineering Service
  -> Rules Engine
  -> Optional ML Inference Service
  -> Fraud Scoring Service
  -> PostgreSQL
```

The code keeps the important boundaries clear:

- Routes handle HTTP concerns and dependency injection.
- Services handle business workflows such as feature extraction and scoring.
- Repositories handle database access.
- SQLAlchemy models live separately from Pydantic schemas.
- `app/db/base.py` only defines `Base`.
- `app/db/models.py` imports SQLAlchemy models for Alembic discovery.

## Current Features

- Health endpoint.
- Real-time transaction scoring.
- Rule-based fraud checks with explainable reasons.
- Optional baseline ML inference if a model artifact exists.
- Hybrid scoring formula: `final_score = min((0.6 * rule_score) + (0.4 * model_score), 1.0)`.
- PostgreSQL persistence for fraud scores.
- Separate persistence for transaction feature snapshots.
- Retrieval by fraud score ID.
- Retrieval of latest fraud score by transaction ID.
- Retrieval of saved features for a fraud score.
- Alembic migrations.
- Demo data seed script.
- Baseline scikit-learn training script.
- Tests for rules, feature engineering, scoring, routes, retrieval, and fallback behavior.

## Tech Stack

- Python 3.12+
- FastAPI
- Pydantic v2
- SQLAlchemy 2.0 async
- asyncpg
- PostgreSQL
- Alembic
- Redis via Docker Compose for later async workflows
- scikit-learn
- pandas
- joblib
- pytest
- Ruff

## Project Structure

```text
app/
  api/v1/routes/                 FastAPI route handlers
  api/v1/dependencies.py         Dependency wiring
  core/config.py                 Pydantic settings
  db/base.py                     SQLAlchemy Base
  db/models.py                   Alembic model discovery imports
  db/session.py                  Async engine and session factory
  infrastructure/repositories/   Database repositories
  models/database/               SQLAlchemy database models
  schemas/                       Pydantic request/response schemas
  services/feature_engineering/  Feature extraction
  services/fraud_scoring/        Rule and hybrid scoring orchestration
  services/model_inference/      Optional model artifact inference
  services/rules_engine/         Deterministic fraud rules
alembic/                         Database migrations
models/                          Local trained model artifacts, gitignored
scripts/                         Seed and training scripts
tests/                           Unit and route tests
```

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Health check |
| `POST` | `/api/v1/fraud/score` | Score and persist a transaction |
| `GET` | `/api/v1/fraud/scores/{score_id}` | Get a fraud score by ID |
| `GET` | `/api/v1/fraud/transactions/{transaction_id}` | Get latest score for a transaction |
| `GET` | `/api/v1/fraud/scores/{score_id}/features` | Get saved features for a score |

## Example Request

```json
{
  "transaction_id": "txn-1001",
  "customer_id": "cust-001",
  "amount_minor": 1500000,
  "currency": "NGN",
  "payment_provider": "Paystack",
  "channel": "Card",
  "customer_email": null,
  "ip_address": null,
  "device_id": null,
  "created_at_utc": "2026-05-22T10:00:00Z"
}
```

## Example Response

```json
{
  "score_id": "11111111-1111-1111-1111-111111111111",
  "transaction_id": "txn-1001",
  "risk_score": 0.6,
  "risk_level": "Medium",
  "decision": "Review",
  "model_version": "fraud-model-v1.0.0",
  "rules_triggered": [
    "HighAmountRule",
    "MissingDeviceRule",
    "MissingIpAddressRule"
  ],
  "reasons": [
    "Transaction amount is unusually high.",
    "Device identifier is missing.",
    "IP address is missing."
  ],
  "scored_at_utc": "2026-05-22T10:00:01Z"
}
```

## Feature Engineering

The service stores an ML-ready feature snapshot for each scored transaction. Current features include:

- Amount in minor and major units.
- Currency, provider, and channel.
- Presence of customer email, IP address, and device ID.
- High amount indicator.
- Customer transaction count over 24 hours.
- Customer amount sum over 24 hours.
- Customer average amount over 30 days.
- Customer high-risk count over 30 days.
- Device transaction count over 24 hours.
- IP transaction count over 24 hours.
- Amount-to-customer-average ratio.
- Feature set version.

Storing these features separately makes future model training and prediction debugging much easier.

## Rule-Based Scoring

The rules engine currently checks:

- High transaction amount.
- Unsupported currency.
- Missing device ID.
- Missing IP address.

Each triggered rule contributes to the score and adds a human-readable reason. This keeps decisions explainable even before ML is introduced.

## Baseline ML Pipeline

The training script loads saved `transaction_features` from PostgreSQL, creates temporary weak labels from risk signals, trains a simple `RandomForestClassifier`, and saves:

- `models/fraud_model_v1.pkl`
- `models/fraud_model_v1_metadata.json`

The model artifact is intentionally local and gitignored. If the model is missing, the API continues to use rule-based scoring only.

## Local Setup

Create and activate a virtual environment, then install the project:

```powershell
pip install -e ".[dev]"
```

Create your local environment file:

```powershell
Copy-Item .env.example .env
```

Start local dependencies:

```powershell
docker compose up -d
```

Apply migrations:

```powershell
alembic upgrade head
```

Seed demo data:

```powershell
python scripts/seed_demo_data.py
```

Train the baseline model:

```powershell
python scripts/train_model.py
```

Run the API:

```powershell
uvicorn app.main:app --reload
```

Run tests:

```powershell
pytest
```

API docs are available at:

```text
http://127.0.0.1:8000/docs
```

## Docker Compose

`docker-compose.yml` starts:

- PostgreSQL on `localhost:5433`
- Redis on `localhost:6379`

The default local database URL is:

```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5433/fraud_detection
```

## What I Learned

This project demonstrates:

- How to structure a FastAPI backend with clean service and repository boundaries.
- How to keep API responses explainable for risk decisions.
- How to persist feature snapshots for future ML training and inference traceability.
- How to add ML inference as an optional capability without breaking rule-based scoring.
- How Alembic, async SQLAlchemy, and PostgreSQL fit into an ML-ready backend.

## Future Improvements

- Add real fraud labels and train on a real dataset.
- Add model evaluation reports and threshold tuning.
- Store separate rule score, model score, and final score columns.
- Add structured logging and request IDs.
- Add CI checks for tests and linting.
- Add Celery jobs for batch scoring and scheduled monitoring.
- Add authentication and deployment only after the local service is fully stable.

## Portfolio Summary

`ai-fraud-detection-service` is a compact but realistic fraud scoring backend. It shows API design, async database persistence, explainable decisions, feature engineering, baseline ML training, optional model inference, and tests in one coherent project.
