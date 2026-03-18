from src.common.transcription.repository import TranscriptionRepository
from src.common.db.repository import LectureDBRepository
from src.common.db.models import TaskStatusID
from src.common.exceptions import TaskFailedException, TaskTimeoutException
import logging

logger = logging.getLogger(__name__)

class TranscriptionService:
    def __init__(self, db_repo: LectureDBRepository):
        self.transcription_repository = TranscriptionRepository()
        self.db_repo = db_repo

    async def run(self, file_path: str, task_id: str):
        try:
            transcription_text = await self.transcription_repository.transcribe(file_path)
        except (TaskFailedException, TaskTimeoutException) as e:
            await self.db_repo.update_task(
                task_id=task_id,
                status=TaskStatusID.FAIL,
            )
            logger.error(f"Task {task_id} failed: {e}")
            raise

        transcription_record = await self.db_repo.save_transcription(
            transcription=transcription_text
        )
        await self.db_repo.update_task(
            task_id=task_id,
            status=TaskStatusID.SUCCESS,
            transcription_id=transcription_record['id']
        )




    
    
        
    
