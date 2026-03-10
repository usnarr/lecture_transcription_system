from src.common.open_ai.repository import OpenAIRepository
from src.common.db.repository import LectureDBRepository
from typing import Dict
class RegenerateSummaryService:
    def __init__(self, db_repo: LectureDBRepository):
        self.db_repo = db_repo
        self.openai_repo = OpenAIRepository()

    async def regenerate_summary(self, task_id: str, messages: Dict[str, str]):
        task = await self.db_repo.get_task_by_id(task_id)
        if not task:
            raise ValueError(f"Task with ID {task_id} not found.")

        transcription = await self.db_repo.get_transcription_by_id(task['transcription_id'])
        
        user = messages.get("user", "") + f"\nTranscription: {transcription['transcription_text']}"
        
        await self.openai_repo.set_messages(
            system_msg=messages.get("system"),
            prompt_msg=user
        )
        new_summary = await self.openai_repo.generate_summary()
        await self.db_repo.update_summary(
            summary_id=task['summary_id'],
            new_summary_text=new_summary
        )
        return {"status": "Summary regenerated successfully!"}