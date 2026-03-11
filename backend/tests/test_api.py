import os

os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./fraudshield_test.db"
os.environ["REDIS_URL"] = "redis://localhost:6379/15"

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health() -> None:
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_transaction_flow() -> None:
    payload = {
        "user_id": "user-001",
        "amount": 1750,
        "location": "NG",
        "device_type": "ios",
        "velocity_1h": 12,
        "is_foreign_txn": 1,
        "merchant_risk_score": 0.81,
    }
    response = client.post('/api/v1/transaction', json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["risk_level"] in {"High", "Critical", "Medium", "Low"}
    assert 0 <= body["fraud_probability"] <= 1

    stats = client.get('/api/v1/fraud-stats')
    assert stats.status_code == 200
    assert stats.json()["total_transactions"] >= 1

    transactions = client.get('/api/v1/transactions')
    assert transactions.status_code == 200
    assert len(transactions.json()) >= 1
