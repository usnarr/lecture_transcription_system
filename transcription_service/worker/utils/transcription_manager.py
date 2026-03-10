import threading
import logging
import os
from contextlib import contextmanager

from whisper import load_model
from worker.utils.redis import RedisClient
from dotenv import load_dotenv

load_dotenv()

WORKER_ID = os.getenv("WORKER_ID", "worker1")

logger = logging.getLogger(__name__)


class TranscriptionManager:
    """Thread-safe pool for pre-loaded Whisper models with Redis-backed availability tracking."""

    SUPPORTED_MODELS = {
        "large": {"vram_gb": 10.5},
    }

    def __init__(self, redis_url: str | None = None, manager_id: int | None = None):
        redis_url = redis_url or os.getenv("CELERY_BACKEND_URL")
        redis_password = os.getenv("REDIS_PASSWORD")

        self.redis_client = RedisClient(url=redis_url, password=redis_password)

        self._lock = threading.Lock()
        self._models: dict[str, list] = {"large": []}
        self.model_memory_requirements = {k: v["vram_gb"] for k, v in self.SUPPORTED_MODELS.items()}

        if manager_id is None:
            manager_id = os.getpid()
        self.manager_id = manager_id
        self.redis_key = f"available_models:{WORKER_ID}:{self.manager_id}"

        self._preload_models()
        self._sync_redis()

    # ── model lifecycle ──────────────────────────────────────────────

    def _preload_models(self):
        """Load models into memory at startup."""
        for model_size in self.SUPPORTED_MODELS:
            logger.info("Preloading '%s' model...", model_size)
            model = load_model(model_size)
            self._models[model_size].append(model)
            logger.info("Preloaded '%s' model successfully", model_size)

    def _sync_redis(self):
        """Push current pool sizes to Redis so the controller sees availability."""
        total = sum(len(pool) for pool in self._models.values())
        try:
            self.redis_client.set(self.redis_key, str(total))
            logger.info("Synced Redis key %s = %d", self.redis_key, total)
        except Exception:
            logger.exception("Failed to sync Redis key %s", self.redis_key)

    def get_model(self, model_size: str):
        """Pop a model from the pool (thread-safe). Returns None if none available."""
        if model_size not in self.SUPPORTED_MODELS:
            return None

        with self._lock:
            pool = self._models[model_size]
            if not pool:
                return None
            model = pool.pop()

        try:
            self.redis_client.decrby(self.redis_key, 1)
        except Exception:
            logger.exception("Failed to decrement Redis key %s", self.redis_key)

        logger.info("Checked out '%s' model, remaining: %d", model_size, len(self._models[model_size]))
        return model

    def return_model(self, model, model_size: str):
        """Return a model to the pool after use (thread-safe)."""
        with self._lock:
            self._models[model_size].append(model)

        try:
            self.redis_client.incrby(self.redis_key, 1)
        except Exception:
            logger.exception("Failed to increment Redis key %s", self.redis_key)

        logger.info("Returned '%s' model, available: %d", model_size, len(self._models[model_size]))

    @contextmanager
    def acquire_model(self, model_size: str, timeout: int = 300, poll_interval: float = 2.0):
        """Context manager that waits for an available model, yields it, and auto-returns it.

        Usage::

            with manager.acquire_model("large") as model:
                result = model.transcribe(file_path)
        """
        import time

        model = None
        start = time.monotonic()

        while model is None:
            elapsed = time.monotonic() - start
            if elapsed > timeout:
                raise TimeoutError(f"No '{model_size}' model available after {timeout}s")
            model = self.get_model(model_size)
            if model is None:
                logger.debug("Waiting for '%s' model (%.0fs elapsed)...", model_size, elapsed)
                time.sleep(poll_interval)

        try:
            yield model
        finally:
            self.return_model(model, model_size)

    def cleanup(self):
        """Delete the Redis availability key and close the client."""
        try:
            self.redis_client.delete(self.redis_key)
        except Exception:
            logger.exception("Failed to delete Redis key %s", self.redis_key)
        self.redis_client.close()