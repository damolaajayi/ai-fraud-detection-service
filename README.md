# ai-fraud-detection-service

AI-powered fraud detection service built with FastAPI, machine learning, feature engineering, async processing, and production-ready backend architecture.

## Overview

`ai-fraud-detection-service` is a backend system that detects potentially fraudulent transactions using rule-based checks, machine learning models, and real-time risk scoring.

The service is designed to complement payment platforms such as `payment-routing-engine` by acting as an intelligent risk engine that can evaluate transactions before or after payment processing.

This project demonstrates how to build an AI-native backend service that combines:

- FastAPI
- machine learning inference
- feature engineering
- async background processing
- PostgreSQL persistence
- Redis caching
- model versioning
- monitoring and observability
- production-grade API design

This is not just a simple ML notebook project. It is designed as a real backend service that exposes fraud intelligence through APIs.

---

## Goals

The goal of this project is to model the core concerns of a real fraud detection platform:

- real-time fraud scoring
- transaction feature extraction
- rule-based risk checks
- ML-powered risk classification
- async model inference
- explainable fraud decisions
- model lifecycle management
- observability
- production-ready FastAPI architecture

It is also designed to support preparation for AWS Machine Learning Engineer concepts such as:

- data ingestion
- feature engineering
- model training
- model deployment
- inference endpoints
- monitoring
- model evaluation
- drift detection

---

## Core Capabilities

### Transaction risk scoring

The service accepts transaction data and returns a fraud risk score.

Example output:

```json
{
  "transactionId": "txn_123",
  "riskScore": 0.87,
  "riskLevel": "High",
  "decision": "Review",
  "reasons": [
    "Transaction amount is unusually high",
    "Customer has multiple failed attempts",
    "Provider failure pattern detected"
  ]
}
```

### Rule-based fraud checks

The system supports deterministic fraud rules such as:

- high transaction amount
- repeated failed transactions
- unusual transaction frequency
- unsupported country/currency combinations
- blacklisted customer or device
- suspicious provider failure patterns

### ML-based prediction

The service will support ML models that classify transactions as:

- low risk
- medium risk
- high risk
- suspicious
- fraudulent

### Feature engineering

The service extracts and stores useful fraud features such as:

- transaction amount
- customer transaction count
- failed attempt count
- provider failure rate
- transaction velocity
- average customer amount
- time since last transaction
- currency risk profile
- historical chargeback indicator

### Async processing

Fraud scoring can be performed:

- synchronously for real-time API calls
- asynchronously through a background worker

This supports both:

- real-time checkout decisions
- batch fraud analysis

### Model versioning

Predictions should include the model version used:

```json
{
  "modelVersion": "fraud-model-v1.0.0"
}
```

This allows traceability when model behavior changes.

### Explainability

The service should not only return a score. It should explain why a transaction was considered risky.

Example:

```json
{
  "riskScore": 0.76,
  "decision": "Review",
  "reasons": [
    "Amount is above customer's historical average",
    "Transaction velocity exceeded threshold"
  ]
}
```

---

## Architecture

The project follows a modular backend architecture.

```text
Client / Payment System
        ↓
FastAPI API Layer
        ↓
Application Services
        ↓
Fraud Rules + ML Inference
        ↓
PostgreSQL / Redis / Model Store
        ↓
Background Workers
```

---

## High-Level Components

### API Layer

Responsible for:

- HTTP endpoints
- request validation
- response formatting
- authentication later
- rate limiting later
- OpenAPI documentation

### Application Layer

Responsible for:

- fraud scoring workflows
- feature extraction coordination
- rule evaluation
- ML inference orchestration
- decision generation

### Domain Layer

Responsible for:

- fraud decision models
- risk levels
- scoring rules
- transaction feature objects
- business rules

### Infrastructure Layer

Responsible for:

- PostgreSQL database access
- Redis caching
- ML model loading
- message queue integration
- external service communication
- logging and tracing

### Worker Layer

Responsible for:

- async scoring
- batch processing
- feature refresh jobs
- model evaluation jobs
- scheduled monitoring tasks

---

## Planned Tech Stack

- Python
- FastAPI
- Pydantic
- SQLAlchemy
- Alembic
- PostgreSQL
- Redis
- Celery
- RabbitMQ or Redis broker
- scikit-learn
- pandas
- NumPy
- MLflow or simple model registry
- Docker / Docker Compose
- Pytest
- Ruff
- mypy
- OpenTelemetry
- Prometheus/Grafana later

---

## Solution Structure

```text
ai-fraud-detection-service/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── routes/
│   │       └── dependencies.py
│   ├── core/
│   │   ├── config.py
│   │   ├── logging.py
│   │   └── security.py
│   ├── db/
│   │   ├── session.py
│   │   └── base.py
│   ├── domain/
│   │   ├── entities/
│   │   ├── enums/
│   │   └── rules/
│   ├── models/
│   │   └── database/
│   ├── schemas/
│   ├── services/
│   │   ├── fraud_scoring/
│   │   ├── feature_engineering/
│   │   ├── model_inference/
│   │   └── rules_engine/
│   ├── infrastructure/
│   │   ├── repositories/
│   │   ├── cache/
│   │   ├── messaging/
│   │   └── ml/
│   ├── workers/
│   └── main.py
├── alembic/
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── models/
│   └── fraud_model_v1.pkl
├── notebooks/
├── scripts/
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml
├── README.md
└── .env.example
```

---

## Core Domain Concepts

### Entities

- `Transaction`
- `FraudScore`
- `FraudDecision`
- `FraudRule`
- `TransactionFeature`
- `ModelPrediction`
- `CustomerRiskProfile`

### Important enums

- `RiskLevel`
- `FraudDecisionType`
- `FraudRuleType`
- `ModelStatus`
- `TransactionChannel`

### Risk levels

- Low
- Medium
- High
- Critical

### Decisions

- Approve
- Review
- Block

---

## API Scope

### Fraud scoring

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/fraud/score` | Score a transaction in real time |
| `GET` | `/api/v1/fraud/scores/{score_id}` | Get fraud score details |
| `GET` | `/api/v1/fraud/transactions/{transaction_id}` | Get fraud analysis for a transaction |

### Rules

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/rules` | List fraud rules |
| `POST` | `/api/v1/rules` | Create fraud rule |
| `PUT` | `/api/v1/rules/{rule_id}` | Update fraud rule |
| `POST` | `/api/v1/rules/{rule_id}/disable` | Disable fraud rule |

### Features

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/features/extract` | Extract features from transaction data |
| `GET` | `/api/v1/features/transactions/{transaction_id}` | Get extracted transaction features |

### Models

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/models` | List registered fraud models |
| `GET` | `/api/v1/models/{model_id}` | Get model metadata |
| `POST` | `/api/v1/models/{model_id}/activate` | Activate model version |

### Operations

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Health check |
| `GET` | `/metrics` | Metrics endpoint later |

---

## Example Request

```json
{
  "transactionId": "txn_1001",
  "customerId": "cust_001",
  "amountMinor": 250000,
  "currency": "NGN",
  "paymentProvider": "Paystack",
  "channel": "Card",
  "customerEmail": "customer@example.com",
  "ipAddress": "102.88.10.22",
  "deviceId": "device_abc123",
  "createdAtUtc": "2026-04-29T10:30:00Z"
}
```

---

## Example Response

```json
{
  "transactionId": "txn_1001",
  "riskScore": 0.82,
  "riskLevel": "High",
  "decision": "Review",
  "modelVersion": "fraud-model-v1.0.0",
  "rulesTriggered": [
    "HighAmountRule",
    "VelocityRule"
  ],
  "reasons": [
    "Transaction amount is above normal customer behavior",
    "Customer has made multiple transactions within a short time window"
  ],
  "scoredAtUtc": "2026-04-29T10:30:05Z"
}
```

---

## ML Workflow

The ML workflow is expected to evolve through these stages:

```text
Raw transaction data
        ↓
Data cleaning
        ↓
Feature engineering
        ↓
Model training
        ↓
Model evaluation
        ↓
Model registration
        ↓
Model deployment
        ↓
Real-time inference
        ↓
Monitoring
```

---

## AWS ML Mapping

This project is intentionally designed to map to AWS Machine Learning Engineer skills.

| Project Component | AWS Equivalent |
|---|---|
| Raw transaction storage | Amazon S3 |
| Feature engineering | AWS Glue / SageMaker Processing |
| Model training | Amazon SageMaker Training Jobs |
| Model registry | SageMaker Model Registry |
| Real-time inference | SageMaker Endpoint / Lambda |
| Async inference | SQS / Lambda / SageMaker Async Inference |
| Monitoring | CloudWatch / SageMaker Model Monitor |
| API exposure | API Gateway / ECS |
| Database | RDS PostgreSQL |
| Cache | ElastiCache Redis |

---

## Development Principles

- Keep APIs clean and well-documented
- Separate rule-based scoring from ML-based scoring
- Make fraud decisions explainable
- Do not hide risk logic inside controllers
- Keep model inference behind a clear interface
- Store model version with every prediction
- Make features reusable for training and inference
- Prioritize observability and reproducibility
- Build for extension, not premature complexity

---

## Local Development

### Prerequisites

- Python 3.12+
- Docker
- Docker Compose
- PostgreSQL
- Redis

### Environment setup

Create a `.env` file from `.env.example`.

```bash
cp .env.example .env
```

Example `.env.example`:

```env
APP_NAME=ai-fraud-detection-service
ENVIRONMENT=development

DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/fraud_detection
REDIS_URL=redis://localhost:6379/0

MODEL_PATH=models/fraud_model_v1.pkl
ACTIVE_MODEL_VERSION=fraud-model-v1.0.0
```

### Run locally

```bash
uvicorn app.main:app --reload
```

### Run with Docker

```bash
docker compose up --build
```

### API docs

```text
http://localhost:8000/docs
```

---

## Testing

Run tests:

```bash
pytest
```

Run with coverage:

```bash
pytest --cov=app
```

---

## Roadmap

### Phase 1: Project foundation

- FastAPI project setup
- PostgreSQL setup
- SQLAlchemy models
- Alembic migrations
- basic fraud scoring endpoint
- rule-based scoring engine

### Phase 2: Feature engineering

- transaction feature extraction
- customer risk profiles
- transaction velocity checks
- provider failure pattern features
- Redis caching for recent transaction history

### Phase 3: ML inference

- train initial fraud model
- save model artifact
- load model in inference service
- return risk score and model version
- combine rule score and ML score

### Phase 4: Async processing

- Celery worker setup
- async fraud scoring jobs
- queue-based batch scoring
- retry and dead-letter handling

### Phase 5: Observability and production readiness

- structured logging
- OpenTelemetry tracing
- health checks
- Docker Compose environment
- integration tests
- CI pipeline

### Phase 6: AWS ML alignment

- S3-style data layout
- SageMaker-style training pipeline
- model registry simulation
- monitoring and drift detection
- deployment notes for AWS

---

## Future Enhancements

- real fraud dataset training
- anomaly detection model
- graph-based fraud detection
- device fingerprinting
- geolocation risk scoring
- customer behavior profiling
- model drift monitoring
- human review workflow
- fraud case management
- integration with `payment-routing-engine`

---

## Status

This project is currently in active design and implementation.

The first milestone is to build a clean FastAPI foundation with a rule-based fraud scoring engine before adding ML inference.

---

## Author

Built as part of a world-class backend and AI engineering portfolio focused on:

- fraud detection
- payment intelligence
- machine learning systems
- backend architecture
- AWS ML Engineer preparation
