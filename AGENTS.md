# AGENTS.md

## Project Name

`ai-fraud-detection-service`

## Project Purpose

This project is an AI-powered fraud detection backend service built with FastAPI.

The goal is to build a production-minded fraud intelligence service that can:

- receive transaction data
- validate transaction payloads
- extract fraud-related features
- apply rule-based fraud checks
- later apply machine learning inference
- generate explainable fraud risk scores
- persist fraud scoring results
- support model versioning
- support future async processing
- map well to AWS Machine Learning Engineer concepts

This is not intended to be a simple notebook-based ML project. It should be designed as a backend system that can support machine learning in a production-style environment.

---

## Current Tech Stack

- Python
- FastAPI
- Pydantic v2
- Pydantic Settings
- PostgreSQL
- SQLAlchemy 2.0 async
- asyncpg
- Alembic
- Redis later
- Celery later
- scikit-learn later
- pandas / NumPy later
- Docker / Docker Compose
- Pytest
- Ruff
- mypy later

---

## Architecture Overview

The project uses a modular FastAPI architecture.

```text
Client / Payment System
        ↓
FastAPI API Layer
        ↓
Application Services
        ↓
Rules Engine / Feature Engineering / ML Inference
        ↓
Repositories
        ↓
PostgreSQL / Redis / Model Store
```

---

## Folder Responsibilities

```text
app/
├── api/
│   └── v1/
│       ├── routes/
│       └── dependencies.py
├── core/
├── db/
├── domain/
├── infrastructure/
│   └── repositories/
├── models/
│   └── database/
├── schemas/
├── services/
│   ├── fraud_scoring/
│   ├── feature_engineering/
│   ├── model_inference/
│   └── rules_engine/
├── workers/
└── main.py
```

### `app/api`

Contains API route definitions.

Rules:

- Keep route handlers thin.
- Do not put business logic directly in routes.
- Use dependencies to inject services and repositories.
- Return Pydantic response schemas.

### `app/core`

Contains application configuration and core setup.

Currently includes:

- `config.py`

Rules:

- Use Pydantic Settings.
- Load secrets/config from environment variables or `.env`.
- Do not hardcode secrets.

### `app/db`

Contains database setup.

Current files:

- `base.py`
- `session.py`
- `models.py`

Rules:

- `base.py` should only define SQLAlchemy `Base`.
- Do not import database models directly inside `base.py`.
- Use `models.py` to import SQLAlchemy models for Alembic discovery.
- Avoid circular imports.

### `app/models/database`

Contains SQLAlchemy database models.

Rules:

- Database models should represent persistence concerns.
- Do not use database models as API response models.
- Use explicit mapping between database models and Pydantic schemas.

### `app/schemas`

Contains Pydantic schemas.

Rules:

- Use Pydantic v2 style.
- Keep request and response models clean.
- Validate payloads as close to the API boundary as possible.
- Use snake_case fields.

### `app/services`

Contains business/application logic.

Rules:

- Fraud scoring logic belongs here.
- Feature engineering logic belongs here.
- ML inference orchestration belongs here later.
- Do not put persistence logic here directly; use repositories.

### `app/infrastructure/repositories`

Contains repository classes for database access.

Rules:

- Use async SQLAlchemy.
- Return database records or mapped responses where appropriate.
- Keep query logic out of route handlers.
- Keep repositories focused on persistence.

### `alembic`

Contains database migrations.

Rules:

- Use Alembic for schema changes.
- Update `app/db/models.py` when adding a new SQLAlchemy model.
- Generate migrations using `alembic revision --autogenerate`.
- Review generated migrations before applying.

---

## Current Implemented Features

The project currently supports:

- FastAPI app startup
- health endpoint
- fraud score endpoint
- fraud score retrieval by score ID
- fraud score retrieval by transaction ID
- Pydantic request/response validation
- rule-based fraud scoring
- explainable fraud decisions
- model version included in scoring response
- PostgreSQL persistence
- async SQLAlchemy setup
- Alembic migrations
- Docker Compose for PostgreSQL and Redis
- feature engineering based on historical fraud scores

---

## Current Important Endpoints

```http
GET /health
```

Checks if the service is running.

```http
POST /api/v1/fraud/score
```

Scores a transaction for fraud risk.

```http
GET /api/v1/fraud/scores/{score_id}
```

Gets a fraud score by its ID.

```http
GET /api/v1/fraud/transactions/{transaction_id}
```

Gets the latest fraud score for a transaction.

---

## Current Important Schemas

- `FraudScoreRequest`
- `FraudScoreResponse`
- `TransactionFeatures`
- `RiskLevel`
- `FraudDecision`
- `TransactionChannel`

---

## Current Important Services

- `FraudRulesEngine`
- `FraudScoringService`
- `FeatureEngineeringService`

---

## Current Important Repository

- `FraudScoreRepository`

---

## Current Important Database Model

- `FraudScoreRecord`

---

## Design Principles

Follow these principles when modifying the project:

1. Keep routes thin.
2. Keep business logic in services.
3. Keep persistence logic in repositories.
4. Keep database models separate from API schemas.
5. Use explicit mapping instead of magic mapping libraries.
6. Use async SQLAlchemy for database operations.
7. Keep fraud decisions explainable.
8. Store model version with every prediction.
9. Avoid circular imports.
10. Prefer clarity over clever abstractions.
11. Do not introduce unnecessary packages.
12. Make the system easy to extend for ML inference later.

---

## Fraud Scoring Philosophy

The service should combine:

```text
rule-based scoring + feature engineering + ML inference later
```

Rule-based scoring is useful because it is:

- explainable
- deterministic
- easy to debug
- useful even before ML is added

ML inference will be added later to improve decision quality.

The final system should not return only a risk score. It should also return:

- risk level
- decision
- model version
- triggered rules
- human-readable reasons

---

## Risk Decision Model

The current decision model is:

```text
Low risk      → Approve
Medium risk   → Review
High risk     → Review
Critical risk → Block
```

Do not remove explainability from the response.

---

## Feature Engineering Goals

Feature engineering is a major goal of this project.

Important features include:

- customer transaction count in the last 24 hours
- customer total amount in the last 24 hours
- customer average transaction amount
- amount-to-average ratio
- customer high-risk count
- device transaction count
- IP transaction count
- provider risk profile later
- currency risk profile later

These features will later become model inputs.

---

## AWS Machine Learning Engineer Alignment

This project should map well to AWS ML concepts.

| Project Area | AWS Equivalent |
|---|---|
| Raw transaction storage | Amazon S3 / RDS |
| Feature engineering | AWS Glue / SageMaker Processing |
| Model training | SageMaker Training Jobs |
| Model artifact storage | S3 |
| Model versioning | SageMaker Model Registry |
| Real-time inference | SageMaker Endpoint / ECS |
| Async inference | SQS / Lambda / SageMaker Async Inference |
| Monitoring | CloudWatch / SageMaker Model Monitor |
| Drift detection | SageMaker Model Monitor |

When adding new features, think about how they would map to production ML systems.

---

## Database Rules

Use PostgreSQL.

Local development connection string may look like:

```env
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5433/fraud_detection
```

Inside Docker Compose, use:

```env
DATABASE_URL=postgresql+asyncpg://postgres:password@postgres:5432/fraud_detection
```

If the password contains special characters like `@`, encode it in the URL:

```text
@ → %40
```

Example:

```env
DATABASE_URL=postgresql+asyncpg://postgres:D%40examplepassword@localhost:5433/fraud_detection
```

Do not commit real secrets.

---

## Alembic Rules

When adding a new database model:

1. Create the SQLAlchemy model in `app/models/database`.
2. Import it in `app/db/models.py`.
3. Generate a migration:

```bash
alembic revision --autogenerate -m "your migration message"
```

4. Review the generated migration.
5. Apply it:

```bash
alembic upgrade head
```

Do not import models directly inside `app/db/base.py`.

`app/db/base.py` should remain:

```python
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass
```

---

## Coding Style

Use:

- Python 3.12+ style
- type hints
- async/await for database operations
- Pydantic v2
- SQLAlchemy 2.0 async style
- FastAPI dependency injection
- readable service classes
- explicit mapping methods

Avoid:

- business logic in routes
- database queries in routes
- circular imports
- global mutable state
- unexplained magic numbers
- unnecessary abstractions

---

## When Generating Code

When making changes, always:

1. Show the file path.
2. Provide the full file if replacing a small file.
3. For larger files, show the exact method or section to change.
4. Include necessary imports.
5. Mention if an Alembic migration is required.
6. Include commands to run/test the change.
7. Keep naming consistent with the existing project.
8. Avoid introducing a package unless clearly needed.

---

## Current Next Priority

The next major feature is:

```text
Persist extracted transaction features separately.
```

This should prepare the system for ML training and model input tracking.

Expected additions:

- `TransactionFeatureRecord` SQLAlchemy model
- `TransactionFeatureRepository`
- schema for transaction features if needed
- persistence flow for extracted features
- Alembic migration
- read endpoint later if useful

The goal is to store the features used during scoring so future ML work can use them for:

- training data
- debugging predictions
- model monitoring
- drift analysis
- explainability

---

## Long-Term Roadmap

### Phase 1

- FastAPI foundation
- rule-based scoring
- PostgreSQL persistence
- Alembic migrations

### Phase 2

- feature engineering
- persisted transaction features
- customer risk profiles

### Phase 3

- ML model training
- model artifact storage
- model inference service
- model versioning

### Phase 4

- Redis caching
- Celery async scoring
- batch scoring jobs

### Phase 5

- observability
- metrics
- tracing
- production Docker setup

### Phase 6

- AWS ML alignment
- SageMaker-style training pipeline
- model monitoring
- drift detection

---

## Final Reminder

This project should always be treated as a production-minded backend service that supports ML.

Do not design it like a notebook project.

The goal is to build the backend system that can support real AI-powered fraud detection.
