# FraudShield AI Architecture Details

## Core services
- API Gateway: FastAPI endpoints + OpenAPI docs.
- Transaction Processor: request validation and feature extraction.
- Model Engine: production model loading and inference.
- Risk Engine: weighted probability + anomaly + graph novelty.
- Storage Engine: PostgreSQL transaction + alert persistence.
- Cache Layer: Redis KPI cache for low-latency dashboard reads.
- Real-Time Feed: websocket distribution to dashboard clients.

## End-to-end runtime handshake
1. Frontend posts transaction to backend.
2. Backend computes score and persists output.
3. Alert is created for high-risk outcomes.
4. Redis cache is invalidated and recomputed on demand.
5. WebSocket broadcasts new transaction/alert instantly.
6. Frontend updates KPI widgets/charts/table in near real-time.

## Cloud-ready deployment
- Containerized services: backend, frontend, postgres, redis.
- CI pipeline for dependency install, test, and frontend build.
- Horizontal scaling path with stateless API replicas.

## Observability
- Structured logs in backend.
- Health endpoint for orchestration probes.
- Metrics-ready for Prometheus/Grafana extension.
