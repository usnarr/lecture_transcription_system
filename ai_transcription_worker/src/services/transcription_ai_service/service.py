import asyncio
import logging
from src.common.transcription.repository import TranscriptionRepository
from src.common.db.repository import LectureDBRepository
from src.common.open_ai.repository import OpenAIRepository
from src.common.db.models import TaskStatusID
from src.common.exceptions import TaskFailedException, TaskTimeoutException

logger = logging.getLogger(__name__)

class AiTranscriptionService:
    def __init__(self, db_repo: LectureDBRepository):
        self.transcription_repository = TranscriptionRepository()
        self.db_repo = db_repo
        self.openai_repo = OpenAIRepository()

    async def run(self, file_path: str, task_id: str, lecture_type_id: int):
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
            transcription_id=transcription_record['id']
        )
        
        client_prompt, system_prompt = await asyncio.gather(
            self.db_repo.get_prompt_message(lecture_type_id),
            self.db_repo.get_system_message(lecture_type_id)
        )

        client_prompt += f" Transcription: {transcription_record['transcription_text']}"
        try:
            open_ai_result = await self.openai_repo.generate_summary(
                prompt_msg=client_prompt,
                system_msg=system_prompt,
            )
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            await self.db_repo.update_task(
                task_id=task_id,
                status=TaskStatusID.FAIL,
            )
            raise

        summary = await self.db_repo.save_summary(
            summary=open_ai_result,
        )   
        await self.db_repo.update_task(
            task_id=task_id,
            status=TaskStatusID.SUCCESS,
            summary_id=summary['id']
        )



    
        
    
