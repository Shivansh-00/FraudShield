from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "FraudShield AI"
    environment: str = "development"
    api_v1_prefix: str = "/api/v1"
    model_path: str = "ml-model/artifacts/fraud_model.joblib"
    scaler_path: str = "ml-model/artifacts/scaler.joblib"
    redis_url: str = "redis://redis:6379/0"
    database_url: str = "postgresql+asyncpg://fraud:fraud@postgres:5432/fraudshield"
    risk_threshold_medium: float = 0.4
    risk_threshold_high: float = 0.7
    risk_threshold_critical: float = 0.9
    enable_rate_limit: bool = True


settings = Settings()
