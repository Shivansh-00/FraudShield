from datetime import datetime
from pydantic import BaseModel, Field


class TransactionIn(BaseModel):
    user_id: str = Field(..., min_length=3)
    amount: float = Field(..., gt=0)
    location: str
    device_type: str
    channel: str = "card"
    velocity_1h: int = Field(default=1, ge=1)
    account_age_days: int = Field(default=365, ge=0)
    is_foreign_txn: int = Field(default=0, ge=0, le=1)
    merchant_risk_score: float = Field(default=0.2, ge=0, le=1)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class PredictionOut(BaseModel):
    transaction_id: str
    fraud_probability: float
    anomaly_score: float
    risk_level: str
    explanation: str


class AlertOut(BaseModel):
    alert_id: str
    transaction_id: str
    user_id: str
    risk_level: str
    message: str
    created_at: datetime
