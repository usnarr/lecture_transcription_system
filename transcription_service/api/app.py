from contextlib import asynccontextmanager
import logging
import os

from fastapi import FastAPI
from dotenv import load_dotenv

from worker.utils.redis import RedisClient

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

REDIS_URL = os.getenv("CELERY_BACKEND_URL")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")
WORKER_ID = os.getenv("WORKER_ID", "worker1")

_redis_client: RedisClient | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _redis_client
    _redis_client = RedisClient(url=REDIS_URL, password=REDIS_PASSWORD)
    logger.info("Redis client initialised for GPU status API")
    try:
        yield
    finally:
        if _redis_client:
            _redis_client.close()
        logger.info("Redis client closed")


gpu_status_api = FastAPI(title="GPU Status API", lifespan=lifespan)


@gpu_status_api.get("/gpu_status")
def gpu_status():
    """Return the total number of available Whisper models on this worker."""
    try:
        pattern = f"available_models:{WORKER_ID}:*"
        keys = _redis_client.keys(pattern)

        if not keys:
            return {"available_models": 0}

        vals = _redis_client.mget(keys)
        total = sum(int(v) for v in vals if v is not None)
        return {"available_models": total}
    except Exception:
        logger.exception("Error reading GPU status from Redis")
        return {"available_models": 0}


@gpu_status_api.get("/health")
def health():
    return {"status": "ok"}