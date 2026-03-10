import asyncio
import logging
from src.common.transcription.repository import TranscriptionRepository
from src.common.db.repository import LectureDBRepository
from src.common.open_ai.repository import OpenAIRepository
import logging

logger = logging.getLogger(__name__)
class AiTranscriptionService:
    def __init__(self, db_repo: LectureDBRepository):
        self.transcription_repository = TranscriptionRepository()
        self.transcription_id = None
        self.db_repo = db_repo
        self.openai_repo = OpenAIRepository()

    async def run(self, file_path: str, task_id: str,lecture_type_id: int):
        
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
            transcription_id=transcription_record['id']
        )
        
        client_prompt, system_prompt = await asyncio.gather(
            self.db_repo.get_prompt_message(lecture_type_id),
            self.db_repo.get_system_message(lecture_type_id)
        )

        client_prompt += f" Transcription: {transcription_record['transcription_text']}"
        await self.openai_repo.set_messages(
            system_msg=system_prompt,
            prompt_msg=client_prompt
        )
        try:
            open_ai_result = await self.openai_repo.generate_summary()
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            await self.db_repo.update_task(
                task_id=task_id,
                status=2,  
            )
            raise e
        summary = await self.db_repo.save_summary(
            summary=open_ai_result,
        )   
        await self.db_repo.update_task(
            task_id=task_id,
            status=3,
            summary_id=summary['id']
        )



    
        
    
