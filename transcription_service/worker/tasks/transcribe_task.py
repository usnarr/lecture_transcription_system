import logging
from pathlib import Path

from worker.celery_app import celery_app
from worker.repository.controller_repo import ControllerRepo

logger = logging.getLogger(__name__)


def _get_manager():
    """Retrieve the per-process TranscriptionManager from the Celery app."""
    get_mgr = getattr(celery_app, "get_transcription_manager", None)
    if get_mgr is None:
        raise RuntimeError("get_transcription_manager is not attached to celery_app")
    return get_mgr()


@celery_app.task(
    bind=True,
    name="transcription_service.worker.tasks.transcribe_task",
    acks_late=True,
    reject_on_worker_lost=True,
    max_retries=2,
)
def transcribe_task(self, file_path: str, model_size: str):
    """Transcribe an audio file using a Whisper model and push the result to the controller."""
    manager = _get_manager()
    file_path = Path(file_path).as_posix()

    if model_size not in manager.model_memory_requirements:
        supported = list(manager.model_memory_requirements.keys())
        logger.error("Invalid model size '%s'. Supported: %s", model_size, supported)
        return {"error": f"Invalid model size: {model_size}. Supported: {supported}"}

    logger.info("Starting transcription – file=%s model=%s", file_path, model_size)
    repo = ControllerRepo()

    try:
        with manager.acquire_model(model_size, timeout=300) as model:
            logger.info("Acquired '%s' model, running transcription...", model_size)
            result = model.transcribe(file_path)
            text = result["text"]
            logger.info("Transcription complete (%d chars)", len(text))

            task_id = self.request.id
            repo.add_transcription(text, task_id)
            return {"result": text}

    except TimeoutError:
        logger.error("Timed out waiting for '%s' model", model_size)
        return {"error": f"Timeout waiting for '{model_size}' model"}
    except Exception as exc:
        logger.exception("Transcription failed for %s", file_path)
        raise self.retry(exc=exc, countdown=30)