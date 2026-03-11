from __future__ import annotations

from datetime import datetime
import json
from typing import Any, Dict, List
import uuid

from redis.asyncio import Redis
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.models.domain import FraudAlert
from app.models.orm import AlertRecord, TransactionRecord


class StorageService:
    def __init__(self) -> None:
        self.redis: Redis | None = None
        self.session_factory: async_sessionmaker | None = None
        self.in_memory_transactions: List[Dict[str, Any]] = []
        self.in_memory_alerts: List[FraudAlert] = []

    def bind(self, session_factory: async_sessionmaker, redis_client: Redis | None) -> None:
        self.session_factory = session_factory
        self.redis = redis_client

    async def add_transaction(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        payload["transaction_id"] = str(uuid.uuid4())
        payload["created_at"] = datetime.utcnow()

        if self.session_factory is None:
            self.in_memory_transactions.append(payload)
            return payload

        async with self.session_factory() as session:
            record = TransactionRecord(**payload)
            session.add(record)
            await session.commit()

        if self.redis:
            await self.redis.delete("fraud_stats")
        return payload

    async def add_alert(self, transaction: Dict[str, Any], message: str) -> FraudAlert:
        alert = FraudAlert(
            alert_id=str(uuid.uuid4()),
            transaction_id=transaction["transaction_id"],
            user_id=transaction["user_id"],
            risk_level=transaction["risk_level"],
            message=message,
            created_at=datetime.utcnow(),
        )

        if self.session_factory is None:
            self.in_memory_alerts.append(alert)
            return alert

        async with self.session_factory() as session:
            session.add(AlertRecord(**alert.__dict__))
            await session.commit()

        return alert

    async def list_transactions(self, limit: int = 200) -> List[Dict[str, Any]]:
        if self.session_factory is None:
            return self.in_memory_transactions[-limit:]

        async with self.session_factory() as session:
            query = select(TransactionRecord).order_by(TransactionRecord.created_at.desc()).limit(limit)
            rows = (await session.execute(query)).scalars().all()

        return [
            {
                "transaction_id": row.transaction_id,
                "user_id": row.user_id,
                "amount": row.amount,
                "location": row.location,
                "device_type": row.device_type,
                "channel": row.channel,
                "velocity_1h": row.velocity_1h,
                "account_age_days": row.account_age_days,
                "is_foreign_txn": row.is_foreign_txn,
                "merchant_risk_score": row.merchant_risk_score,
                "fraud_probability": row.fraud_probability,
                "anomaly_score": row.anomaly_score,
                "risk_level": row.risk_level,
                "explanation": row.explanation,
                "created_at": row.created_at,
            }
            for row in rows
        ]

    async def list_alerts(self, limit: int = 200) -> List[FraudAlert]:
        if self.session_factory is None:
            return self.in_memory_alerts[-limit:]

        async with self.session_factory() as session:
            query = select(AlertRecord).order_by(AlertRecord.created_at.desc()).limit(limit)
            rows = (await session.execute(query)).scalars().all()

        return [
            FraudAlert(
                alert_id=row.alert_id,
                transaction_id=row.transaction_id,
                user_id=row.user_id,
                risk_level=row.risk_level,
                message=row.message,
                created_at=row.created_at,
            )
            for row in rows
        ]

    async def fraud_stats(self) -> Dict[str, Any]:
        if self.redis:
            cached = await self.redis.get("fraud_stats")
            if cached:
                return json.loads(cached)

        if self.session_factory is None:
            total = len(self.in_memory_transactions)
            flagged = len([t for t in self.in_memory_transactions if t["risk_level"] in {"High", "Critical"}])
            suspicious = len({t["user_id"] for t in self.in_memory_transactions if t["risk_level"] != "Low"})
        else:
            async with self.session_factory() as session:
                total = (await session.execute(select(func.count()).select_from(TransactionRecord))).scalar_one()
                flagged = (
                    await session.execute(
                        select(func.count()).select_from(TransactionRecord).where(
                            TransactionRecord.risk_level.in_(["High", "Critical"])
                        )
                    )
                ).scalar_one()
                suspicious = (
                    await session.execute(
                        select(func.count(func.distinct(TransactionRecord.user_id))).where(
                            TransactionRecord.risk_level != "Low"
                        )
                    )
                ).scalar_one()

        percentage = (flagged / total * 100) if total else 0
        payload = {
            "total_transactions": int(total),
            "fraud_transactions": int(flagged),
            "fraud_percentage": round(percentage, 2),
            "suspicious_accounts": int(suspicious),
        }

        if self.redis:
            await self.redis.setex("fraud_stats", 20, json.dumps(payload))
        return payload


store = StorageService()
