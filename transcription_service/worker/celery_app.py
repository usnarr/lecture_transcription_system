from celery import Celery
import os
import logging
from dotenv import load_dotenv
from celery.signals import worker_process_init

from whisper import load_model

load_dotenv()

WORKER_ID = os.getenv("WORKER_ID", "worker1")
MODEL_SIZE = os.getenv("WHISPER_MODEL_SIZE", "large")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

celery_app = Celery(
    f"{WORKER_ID}_queue",
    broker=os.getenv("CELERY_BROKER_URL"),
    backend=os.getenv("CELERY_BACKEND_URL"),
)
celery_app.conf.update(
    worker_concurrency=1,
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
)
celery_app.autodiscover_tasks(["worker"])


@worker_process_init.connect
def _on_worker_process_init(**kwargs):
    """Pre-load the Whisper model once when the worker process starts."""
    logger.info("Loading Whisper '%s' model...", MODEL_SIZE)
    celery_app._model = load_model(MODEL_SIZE)
    logger.info("Whisper '%s' model loaded — worker ready", MODEL_SIZE)
