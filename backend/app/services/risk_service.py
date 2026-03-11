from collections import defaultdict
from typing import Dict, Set

from app.core.config import settings


class RiskService:
    def __init__(self) -> None:
        self.user_merchant_graph: Dict[str, Set[str]] = defaultdict(set)

    def classify_risk(self, fraud_probability: float, anomaly_score: float) -> str:
        score = (0.75 * fraud_probability) + (0.25 * anomaly_score)
        if score >= settings.risk_threshold_critical:
            return "Critical"
        if score >= settings.risk_threshold_high:
            return "High"
        if score >= settings.risk_threshold_medium:
            return "Medium"
        return "Low"

    def graph_signal(self, user_id: str, merchant: str) -> float:
        edges = self.user_merchant_graph[user_id]
        novelty = 1.0 if merchant not in edges and len(edges) > 3 else 0.0
        edges.add(merchant)
        return novelty


risk_service = RiskService()
