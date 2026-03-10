from celery import Celery
from dotenv import load_dotenv
import os

load_dotenv()


BROKER_URL = os.getenv("BROKER_URL_SCHEDULER")
BACKEND_URL = os.getenv("BACKEND_URL_SCHEDULER")

# Initialize Celery app
celery_app = Celery(
    broker=BROKER_URL,
    backend=BACKEND_URL
)
