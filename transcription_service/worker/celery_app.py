from celery import Celery
import os
import logging
from dotenv import load_dotenv
from celery.signals import worker_process_init, worker_process_shutdown

from worker.utils.transcription_manager import TranscriptionManager
from worker.utils.redis import RedisClient

load_dotenv()

REDIS_URL = os.getenv("CELERY_BACKEND_URL")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")
WORKER_ID = os.getenv("WORKER_ID", "worker1")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

celery_app = Celery(
    f"{WORKER_ID}_queue",
    broker=os.getenv("CELERY_BROKER_URL"),
    backend=REDIS_URL,
)
celery_app.autodiscover_tasks(["worker"])


# ── worker lifecycle hooks ──────────────────────────────────────────

def _cleanup_stale_keys():
    """Remove leftover Redis keys from previous runs of this worker."""
    try:
        client = RedisClient(url=REDIS_URL, password=REDIS_PASSWORD)
        pattern = f"available_models:{WORKER_ID}:*"
        stale_keys = client.keys(pattern)
        for key in stale_keys:
            client.delete(key)
        client.close()
        logger.info("Cleaned up %d stale Redis keys for '%s'", len(stale_keys), pattern)
    except Exception:
        logger.exception("Failed to cleanup stale Redis keys")


def _init_manager():
    """Lazily initialise the TranscriptionManager once per process."""
    if getattr(celery_app, "_manager", None) is not None:
        return
    celery_app._manager = TranscriptionManager(
        redis_url=REDIS_URL,
        manager_id=os.getpid(),
    )
    logger.info("Initialised TranscriptionManager for pid=%d", os.getpid())


@worker_process_init.connect
def _on_worker_process_init(**kwargs):
    _cleanup_stale_keys()
    _init_manager()
    logger.info("Worker process ready – model loaded, Redis initialised")


@worker_process_shutdown.connect
def _on_worker_process_shutdown(**kwargs):
    manager = getattr(celery_app, "_manager", None)
    if manager is None:
        return
    try:
        manager.cleanup()
        logger.info("Cleaned up TranscriptionManager on shutdown")
    except Exception:
        logger.exception("Error during TranscriptionManager cleanup")
    finally:
        celery_app._manager = None


def get_transcription_manager() -> TranscriptionManager:
    """Return the per-process TranscriptionManager, initialising if needed."""
    _init_manager()
    return celery_app._manager


celery_app.get_transcription_manager = get_transcription_manager