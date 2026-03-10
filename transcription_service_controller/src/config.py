import os
from dotenv import load_dotenv
from celery import Celery

load_dotenv()

WORKER_CONFIG = {
    "worker1": {
        "gpu_status_url": os.getenv("WORKER1_GPU_STATUS_URL"),
        "celery_queue": "worker1_queue",
    },
}

# RabbitMQ configuration
RABBITMQ_USER = os.getenv("RABBITMQ_USER")
RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD")
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST")
RABBITMQ_PORT = os.getenv("RABBITMQ_PORT")

# Celery configuration
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL")
CELERY_BACKEND_URL = os.getenv("CELERY_BACKEND_URL")

# Redis configuration
REDIS_URL = os.getenv("REDIS_URL")
REDIS_USERNAME = os.getenv("REDIS_USERNAME")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")

TRANSCRIPTION_TTL = 300

# Initialize Celery in the API with credentials from config
celery_app = Celery(
    broker=CELERY_BROKER_URL,
    backend=CELERY_BACKEND_URL,
)
celery_app.conf.update(
    task_default_queue="default",
    task_default_exchange="tasks",
    task_default_routing_key="default",
    task_queues={
        "worker1_queue": {
            "exchange": "worker1_queue",
            "routing_key": "worker1_queue",
        },
    },
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    worker_disable_rate_limits=True,
    task_reject_on_worker_lost=True,
)