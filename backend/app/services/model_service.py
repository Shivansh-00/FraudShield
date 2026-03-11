from __future__ import annotations

from pathlib import Path
from typing import Dict, List
import joblib
import numpy as np

from app.core.config import settings
from app.schemas.transaction import TransactionIn


class ModelService:
    def __init__(self) -> None:
        self.model = None
        self.scaler = None
        self.feature_order = [
            "amount",
            "velocity_1h",
            "account_age_days",
            "is_foreign_txn",
            "merchant_risk_score",
            "device_mobile",
            "channel_card",
        ]
        self._load()

    def _load(self) -> None:
        model_path = Path(settings.model_path)
        scaler_path = Path(settings.scaler_path)
        if model_path.exists() and scaler_path.exists():
            self.model = joblib.load(model_path)
            self.scaler = joblib.load(scaler_path)

    def _encode(self, tx: TransactionIn) -> np.ndarray:
        row = np.array(
            [
                tx.amount,
                tx.velocity_1h,
                tx.account_age_days,
                tx.is_foreign_txn,
                tx.merchant_risk_score,
                1 if tx.device_type.lower() in {"android", "ios", "mobile"} else 0,
                1 if tx.channel.lower() == "card" else 0,
            ],
            dtype=float,
        )
        return row.reshape(1, -1)

    def predict(self, tx: TransactionIn) -> Dict[str, float]:
        encoded = self._encode(tx)
        if self.model is None or self.scaler is None:
            # Heuristic fallback for first-run demo.
            heuristic = min(
                1.0,
                (tx.amount / 2000) * 0.4
                + (tx.velocity_1h / 20) * 0.3
                + tx.is_foreign_txn * 0.2
                + tx.merchant_risk_score * 0.1,
            )
            anomaly_score = float(max(0.0, heuristic - 0.15))
            return {"fraud_probability": float(heuristic), "anomaly_score": anomaly_score}

        scaled = self.scaler.transform(encoded)
        probability = float(self.model.predict_proba(scaled)[0][1])

        anomaly_score = float(np.clip(np.abs(scaled).mean() / 5, 0, 1))
        return {"fraud_probability": probability, "anomaly_score": anomaly_score}

    @staticmethod
    def explain(tx: TransactionIn, fraud_probability: float) -> str:
        reasons: List[str] = []
        if tx.amount > 1200:
            reasons.append("amount is unusually high")
        if tx.is_foreign_txn:
            reasons.append("transaction location differs from user baseline")
        if tx.velocity_1h >= 8:
            reasons.append("transaction frequency is abnormal")
        if tx.merchant_risk_score > 0.7:
            reasons.append("merchant carries elevated risk")

        if not reasons:
            reasons.append("pattern slightly deviates from behavioral profile")

        return (
            f"Transaction risk {fraud_probability:.2f}; flagged because "
            + ", ".join(reasons)
            + "."
        )


model_service = ModelService()
