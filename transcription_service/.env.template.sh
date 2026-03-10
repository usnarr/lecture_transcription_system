WORKER_ID=gpux
CELERY_BROKER_URL=amqp://guest:guest@xxx:5672//
CELERY_BACKEND_URL=redis://xxxx:6379/0


CONTROLLER_ADRESS=xxxx


celery -A worker.celery_app:celery_app worker \
  --loglevel=info \
  --queues=worker1_queue \
  --pool=solo \


  ExecStart=/projects/transcription_service/venv/bin/celery -A worker.celery_app:celery_app worker --pool=prefork --loglevel=info --hostname=worker1@%h --queues=worker1_queue --without-gossip --without-mingle --concurrency=2