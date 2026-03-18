import logging
from pathlib import Path

from worker.celery_app import celery_app

logger = logging.getLogger(__name__)

SUPPORTED_MODELS = ("large",)


@celery_app.task(
    bind=True,
    name="transcribe_audio",
    acks_late=True,
    reject_on_worker_lost=True,
    max_retries=2,
)
def transcribe_task(self, file_path: str, model_size: str = "large"):
    """Transcribe an audio file using the pre-loaded Whisper model."""
    model = getattr(celery_app, "_model", None)
    if model is None:
        raise RuntimeError("Whisper model not loaded — worker not initialised")

    if model_size not in SUPPORTED_MODELS:
        raise ValueError(
            f"Invalid model size '{model_size}'. Supported: {list(SUPPORTED_MODELS)}"
        )

    file_path = Path(file_path).as_posix()
    logger.info("Starting transcription — file=%s model=%s", file_path, model_size)

    try:
        result = model.transcribe(file_path)
        text = result["text"]
        logger.info("Transcription complete (%d chars)", len(text))
        return {"transcription": text}
    except Exception as exc:
        logger.exception("Transcription failed for %s", file_path)
        raise self.retry(exc=exc, countdown=30)