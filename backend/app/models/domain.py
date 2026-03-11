from dataclasses import dataclass
from datetime import datetime


@dataclass
class FraudAlert:
    alert_id: str
    transaction_id: str
    user_id: str
    risk_level: str
    message: str
    created_at: datetime
