
import uuid
import os
from src.common.utils.http import http_post,http_get
import logging
import asyncio
from src.common.exceptions import TaskTimeoutException,TaskFailedException

logger = logging.getLogger(__name__)
class TranscriptionRepository:
    def __init__(self):
        self.request_id = str(uuid.uuid4())
        


    async def transcribe(self, audio_file_path):
        resp = await http_post(
            url=f'{os.getenv("TRANSCRIPTION_SCHEDULER_URL")}/transcribe',
            json={
                "file_path": audio_file_path,
               "model_size": "medium",
            }
        )
        logger.info(f"Transcribing audio file: {audio_file_path}")
        return resp
    async def get_job_status(self, job_id):
        resp = await http_get(
            url=f'{os.getenv("TRANSCRIPTION_SCHEDULER_URL")}/job_status',
            params= {"task_id": job_id},   
        )
        logger.info(f"Getting status for job ID: {job_id}")
        return resp
    
    async def get_transcription(self, transcription_id):
        resp = await http_get(
            url=f'{os.getenv("TRANSCRIPTION_SCHEDULER_URL")}/transcriptions/{transcription_id}',
        )
        logger.info(f"Getting transcription for ID: {transcription_id}")
        return resp
    
    async def _is_job_done(self, job_id):
        timeout = 15 * 60  
        poll_interval = 60
        start_time = asyncio.get_event_loop().time()

        while True:
            await asyncio.sleep(15) 
            resp = await self.get_job_status(job_id)
            job_status = resp.get("status", "").lower()

            if job_status == "success":
                return True
            elif job_status == "failure":
                raise  TaskFailedException(f"Job {job_id} failed.")

            elapsed = asyncio.get_event_loop().time() - start_time
            if elapsed > timeout:
                raise TaskTimeoutException(f"Job {job_id} did not complete within 15 minutes.")

            await asyncio.sleep(poll_interval)