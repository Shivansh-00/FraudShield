# FraudShield AI – Real-Time Intelligent Fraud Detection Platform

FraudShield AI is a production-style fintech platform for real-time digital payment fraud detection. It combines supervised + unsupervised ML, explainable AI, graph-risk signals, and a live executive dashboard.

## 1) Architecture Explanation

```text
User Transaction
   │
   ▼
FastAPI API Gateway (validation, rate limiting, logging)
   │
   ▼
Transaction Processor (feature extraction + graph novelty)
   │
   ├──► ML Inference Engine (XGBoost/RandomForest)
   ├──► Anomaly Signal Engine
   └──► Explainability Engine
   │
   ▼
Risk Scoring Service (0-1 score + severity band)
   │
   ├──► PostgreSQL persistence (transactions + alerts)
   ├──► Redis cache (fraud stats hot cache)
   └──► WebSocket stream + alert fanout
   │
   ▼
React Dashboard (KPIs, live feed, alerts, trend, risk histogram)
```

## 2) Full End-to-End Integration

### Backend integration flow
1. `POST /api/v1/transaction` validates payload.
2. ML service computes fraud probability + anomaly score.
3. Risk service applies weighted score and graph novelty uplift.
4. Transaction is persisted into PostgreSQL.
5. High/Critical cases create alert rows.
6. Redis cache invalidates and recomputes KPI stats.
7. WebSocket pushes transaction/alert events to UI.
8. Frontend refresh + live updates render immediately.

### Data stores
- **PostgreSQL**: source of truth for transaction and alert history.
- **Redis**: cache for `GET /fraud-stats` for low-latency dashboard KPI reads.
- **In-memory fallback**: automatic fallback if DB/Redis unavailable (dev resiliency mode).

## 3) API Documentation

Base URL: `http://localhost:8000/api/v1`

- `POST /transaction`: ingest transaction, score risk, persist, alert.
- `POST /predict-fraud`: alias scoring endpoint.
- `GET /transactions`: recent persisted transactions.
- `GET /fraud-alerts`: recent persisted alerts.
- `GET /fraud-stats`: cached KPI summary from Redis/Postgres.
- `GET /health`: service probe.
- `WS /ws/live`: real-time `transaction` and `alert` events.

Interactive docs: `http://localhost:8000/docs`

## 4) ML Pipeline

### Dataset
- Kaggle credit card fraud dataset expected at `data/creditcard.csv`.

### Workflow
1. Load and preprocess dataset.
2. Handle imbalance with class-weighted models.
3. Train `RandomForest`, `XGBoost`, `IsolationForest`.
4. Evaluate with Accuracy, Precision, Recall, F1, ROC-AUC.
5. Save best model/scaler to `ml-model/artifacts/`.
6. Run SHAP importance generation for explainability.

## 5) Advanced Innovations
1. **Graph-based fraud detection (implemented)**: user-to-location novelty boosts fraud probability.
2. **Adaptive behavioral scoring (implemented)**: amount, velocity, foreign transaction, and merchant risk dynamically adjust score.

## 6) Project Structure

```text
backend/                FastAPI services and tests
frontend/               React + TypeScript + Tailwind dashboard
ml-model/               Training and explainability scripts
data/                   Dataset location (not committed)
scripts/                Simulation utilities
docs/                   Hackathon + architecture docs
.github/workflows/      CI pipeline
```

## 7) Run Locally

### Backend
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cd ..
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend
```bash
cd frontend
npm install
VITE_API_BASE_URL=http://localhost:8000/api/v1 npm run dev -- --host 0.0.0.0 --port 5173
```

### Stream demo data
```bash
python scripts/simulate_transactions.py
```

## 8) Docker Deployment
```bash
docker compose up --build
```

## 9) Security Controls
- Strict schema validation.
- Rate-limiting middleware.
- Structured operational logs.
- Redis-ready anti-replay/risk cache foundation.
- Clear separation of API/risk/model/storage services.

## 10) Hackathon Presentation Support
See `docs/HACKATHON_PITCH.md` for problem statement, talk track, demo walkthrough, and impact analysis.
