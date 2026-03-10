import logging
import os

from dotenv import load_dotenv

from worker.repository.http import http_post

load_dotenv()

logger = logging.getLogger(__name__)


class ControllerRepo:
    """Client for pushing transcription results to the Transcription Controller."""

    def __init__(self):
        self.controller_url = os.getenv("CONTROLLER_URL")
        if not self.controller_url:
            raise ValueError("CONTROLLER_URL environment variable is not set")

    def add_transcription(self, transcription_result: str, task_id: str):
        url = f"{self.controller_url}/add_transcription"
        payload = {"transcription": transcription_result, "task_id": task_id}
        logger.info("Pushing transcription for task %s to %s", task_id, url)
        return http_post(url, json=payload)