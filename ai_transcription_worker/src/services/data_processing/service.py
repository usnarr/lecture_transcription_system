from src.common.open_ai.repository import OpenAIRepository
from src.common.db.repository import LectureDBRepository
from typing import Dict

class RegenerateSummaryService:
    def __init__(self, db_repo: LectureDBRepository):
        self.db_repo = db_repo
        self.openai_repo = OpenAIRepository()

    async def regenerate_summary(self, task_id: int, messages: Dict[str, str]):
        task = await self.db_repo.get_task_by_id(task_id)
        if not task:
            raise ValueError(f"Task with ID {task_id} not found.")

        transcription = await self.db_repo.get_transcription_by_id(task['transcription_id'])
        if not transcription:
            raise ValueError(f"Transcription not found for task {task_id}.")
        
        user_msg = messages.get("user", "") + f"\nTranscription: {transcription['transcription_text']}"
        
        new_summary = await self.openai_repo.generate_summary(
            prompt_msg=user_msg,
            system_msg=messages.get("system"),
        )
        await self.db_repo.update_summary(
            summary_id=task['summary_id'],
            new_summary_text=new_summary
        )
        return {"status": "Summary regenerated successfully!"}