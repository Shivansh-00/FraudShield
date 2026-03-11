from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.schemas.transaction import AlertOut, PredictionOut, TransactionIn
from app.services.model_service import model_service
from app.services.realtime_service import realtime_manager
from app.services.risk_service import risk_service
from app.services.storage_service import store

router = APIRouter()


@router.post("/transaction", response_model=PredictionOut)
async def ingest_transaction(payload: TransactionIn) -> Any:
    signals = model_service.predict(payload)
    graph_novelty = risk_service.graph_signal(payload.user_id, payload.location)
    fraud_probability = min(1.0, signals["fraud_probability"] + 0.05 * graph_novelty)
    risk_level = risk_service.classify_risk(fraud_probability, signals["anomaly_score"])
    explanation = model_service.explain(payload, fraud_probability)

    tx = await store.add_transaction(
        {
            **payload.model_dump(),
            "fraud_probability": fraud_probability,
            "anomaly_score": signals["anomaly_score"],
            "risk_level": risk_level,
            "explanation": explanation,
        }
    )

    response = PredictionOut(
        transaction_id=tx["transaction_id"],
        fraud_probability=fraud_probability,
        anomaly_score=signals["anomaly_score"],
        risk_level=risk_level,
        explanation=explanation,
    )

    await realtime_manager.broadcast({"event": "transaction", "data": tx})

    if risk_level in {"High", "Critical"}:
        alert = await store.add_alert(tx, f"{risk_level} risk transaction detected for user {payload.user_id}")
        await realtime_manager.broadcast({"event": "alert", "data": alert.__dict__})

    return response


@router.post("/predict-fraud", response_model=PredictionOut)
async def predict_fraud(payload: TransactionIn) -> Any:
    return await ingest_transaction(payload)


@router.get("/transactions")
async def list_transactions() -> Any:
    return await store.list_transactions(200)


@router.get("/fraud-alerts", response_model=list[AlertOut])
async def list_alerts() -> Any:
    return [AlertOut(**a.__dict__) for a in await store.list_alerts(200)]


@router.get("/fraud-stats")
async def fraud_stats() -> Any:
    return await store.fraud_stats()


@router.websocket("/ws/live")
async def ws_live(websocket: WebSocket) -> None:
    await realtime_manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        realtime_manager.disconnect(websocket)
