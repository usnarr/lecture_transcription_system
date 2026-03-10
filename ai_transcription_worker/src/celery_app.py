from celery import Celery
import os
from dotenv import load_dotenv

load_dotenv()

celery_app = Celery(
    "scheduler",
    broker=os.getenv("BROKER_URL", "amqp://user:pass@rabbitmq:5672//"),
    backend=os.getenv("BACKEND_URL", "redis://redis:6379/0")
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)
celery_app.autodiscover_tasks(['src'], force=True)