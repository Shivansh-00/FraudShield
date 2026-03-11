import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from redis.asyncio import from_url
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

from app.api.routes import router
from app.core.config import settings
from app.core.database import AsyncSessionLocal, init_db
from app.services.storage_service import store

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


@asynccontextmanager
async def lifespan(_: FastAPI):
    redis_client = None
    try:
        await init_db()
        try:
            redis_client = from_url(settings.redis_url, decode_responses=True)
            await redis_client.ping()
        except Exception:
            redis_client = None
        store.bind(AsyncSessionLocal, redis_client)
        logging.info("Storage initialized with PostgreSQL%s", " + Redis" if redis_client else "")
    except Exception as exc:
        logging.warning("Falling back to in-memory mode due to init failure: %s", exc)
    yield
    if redis_client:
        await redis_client.close()


limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title=settings.app_name, version="1.1.0", lifespan=lifespan)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
if settings.enable_rate_limit:
    app.add_middleware(SlowAPIMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router, prefix=settings.api_v1_prefix)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "service": settings.app_name, "version": "1.1.0"}
