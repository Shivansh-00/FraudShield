import asyncio
import random
from datetime import datetime
import httpx

LOCATIONS = ["US", "UK", "NG", "IN", "SG", "DE"]
DEVICES = ["ios", "android", "web"]


async def generate_transaction(idx: int) -> dict:
    return {
        "user_id": f"user-{random.randint(1, 75):03d}",
        "amount": round(random.uniform(5, 2500), 2),
        "location": random.choice(LOCATIONS),
        "device_type": random.choice(DEVICES),
        "channel": random.choice(["card", "bank_transfer", "wallet"]),
        "velocity_1h": random.randint(1, 14),
        "account_age_days": random.randint(5, 2000),
        "is_foreign_txn": random.randint(0, 1),
        "merchant_risk_score": round(random.uniform(0.05, 0.95), 2),
        "timestamp": datetime.utcnow().isoformat(),
    }


async def main(count: int = 100) -> None:
    async with httpx.AsyncClient(timeout=30) as client:
        for i in range(count):
            payload = await generate_transaction(i)
            response = await client.post(
                "http://localhost:8000/api/v1/transaction", json=payload
            )
            print(i, response.status_code, response.json().get("risk_level"))
            await asyncio.sleep(0.2)


if __name__ == "__main__":
    asyncio.run(main())
