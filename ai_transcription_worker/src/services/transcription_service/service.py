import asyncio
from src.common.transcription.repository import TranscriptionRepository
from src.common.db.repository import LectureDBRepository
import logging

logger = logging.getLogger(__name__)

class TranscriptionService:
    def __init__(self, db_repo: LectureDBRepository):
        self.transcription_repository = TranscriptionRepository()
        self.transcription_id = None
        self.db_repo = db_repo

    async def run(self, file_path, task_id):
        response = await self.transcription_repository.transcribe(file_path)
        self.transcription_id = response.get("job_id")
        try:
            await self.transcription_repository._is_job_done(self.transcription_id)
        except Exception as e:
            await self.db_repo.update_task(
                task_id=task_id,
                status=2,  
            )
            logger.info(f"Task {task_id} failed with error: {e}")
            raise e
        transcription = await self.transcription_repository.get_transcription(self.transcription_id)
        transcription_record = await self.db_repo.save_transcription(
            transcription=transcription.get("transcription", "")
        )
        await self.db_repo.update_task(
            task_id=task_id,
            status=3,
            transcription_id=transcription_record['id']
        )




    
    
        
    
