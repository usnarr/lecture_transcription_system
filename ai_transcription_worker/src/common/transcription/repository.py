import os
import logging
import asyncio
from src.celery_app import celery_app
from src.common.exceptions import TaskTimeoutException, TaskFailedException

logger = logging.getLogger(__name__)

TRANSCRIPTION_QUEUE = os.getenv("TRANSCRIPTION_QUEUE", "worker1_queue")


class TranscriptionRepository:

    async def transcribe(self, audio_file_path: str, model_size: str = "large") -> str:
        """Send a transcription task to the GPU worker queue and wait for the result.

        Returns the transcription text on success.
        Raises TaskFailedException or TaskTimeoutException on failure.
        """
        task = celery_app.send_task(
            "transcribe_audio",
            kwargs={"file_path": audio_file_path, "model_size": model_size},
            queue=TRANSCRIPTION_QUEUE,
        )
        logger.info("Dispatched transcription task %s for file: %s", task.id, audio_file_path)
        return await self._wait_for_result(task)

    async def _wait_for_result(
        self, async_result, timeout: int = 900, poll_interval: int = 10
    ) -> str:
        """Poll the Celery AsyncResult until the GPU worker finishes."""
        elapsed = 0
        while elapsed < timeout:
            await asyncio.sleep(poll_interval)
            elapsed += poll_interval

            if async_result.ready():
                if async_result.successful():
                    result = async_result.result
                    return result.get("transcription", "")
                raise TaskFailedException(
                    f"Transcription task {async_result.id} failed: {async_result.result}"
                )

        raise TaskTimeoutException(
            f"Transcription task {async_result.id} did not complete within {timeout}s"
        )