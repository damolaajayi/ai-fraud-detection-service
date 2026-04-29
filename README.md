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
