from src.services.transcription_service.service import TranscriptionService
from src.services.transcription_ai_service.service import AiTranscriptionService
from src.common.db.database import get_db_connection
from src.common.db.repository import LectureDBRepository
from src.common.db.service import ProcessedLectureService, ProcessingPathsCollectorService
from src.services.data_processing.service import RegenerateSummaryService
import logging
import asyncio
from dotenv import load_dotenv
import os

load_dotenv()

logger = logging.getLogger(__name__)

class Controller:

    def __init__(self):
        self.regeneration_semaphore = asyncio.Semaphore(2)
        self.task_semaphore = asyncio.Semaphore(2)
        self.ai_task_semaphore = asyncio.Semaphore(2)

    async def run_transcription_task(self, task_id: str, lecture_ids: list):
        async with get_db_connection() as connection:
            db_repo = LectureDBRepository(connection)
            processing_data = await ProcessingPathsCollectorService(
                repo=db_repo, 
                lecture_ids=lecture_ids
            ).fetch_processing_paths()
        
        if not processing_data:
            logger.warning(f"No processing data found for task_id: {task_id} and lecture_ids: {lecture_ids}")
            return {"status": "No processing data found."}
        
        tasks = [
            self.process_single_lecture(
                file_path=file_path, 
                task_id=f"{task_id}_{lecture_id}", 
                lecture_id=lecture_id
            )
            for lecture_id, file_path, _ in processing_data
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        failed = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                lecture_id = processing_data[i][0]
                logger.error(f"Failed to process lecture {lecture_id}: {result}")
                failed.append({"lecture_id": lecture_id, "error": str(result)})
        
        return {
            "status": "Transcription task completed." if not failed else "Transcription task completed with errors.",
            "failed": failed,
        }
    
    async def run_ai_transcription_task(self, task_id: str, lecture_ids: list):
        async with get_db_connection() as connection:
            db_repo = LectureDBRepository(connection)
            processing_data = await ProcessingPathsCollectorService(
                repo=db_repo, 
                lecture_ids=lecture_ids
            ).fetch_processing_paths()
        
        if not processing_data:
            logger.warning(f"No processing data found for task_id: {task_id} and lecture_ids: {lecture_ids}")
            return {"status": "No processing data found."}
        
        tasks = [
            self.process_single_ai_lecture(
                file_path=file_path, 
                task_id=f"{task_id}_{lecture_id}",
                lecture_type_id=lecture_type_id, 
                lecture_id=lecture_id
            )
            for lecture_id, file_path, lecture_type_id in processing_data
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        failed = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                lecture_id = processing_data[i][0]
                logger.error(f"Failed to process AI lecture {lecture_id}: {result}")
                failed.append({"lecture_id": lecture_id, "error": str(result)})
        
        return {
            "status": "AI Transcription task completed." if not failed else "AI Transcription task completed with errors.",
            "failed": failed,
        }
    
    async def process_single_lecture(self, file_path: str, task_id: str, lecture_id: int):
        async with self.task_semaphore:
            async with get_db_connection() as connection:
                logger.info(f"Starting processing for Lecture {task_id} with file {file_path}")
                db_repo = LectureDBRepository(connection)
                transcription_service = TranscriptionService(db_repo=db_repo)
                processed_lecture_service = ProcessedLectureService(repo=db_repo)
                
                await db_repo.add_task(task_id=task_id, lecture_id=lecture_id)
                await transcription_service.run(file_path=file_path, task_id=task_id)
                await processed_lecture_service.set_lecture_as_processed(lecture_id)
                
                return {"status": f"Lecture {task_id} processed successfully."}

    async def process_single_ai_lecture(self, file_path: str, task_id: str, lecture_id: int, lecture_type_id: int):
        async with self.ai_task_semaphore:
            async with get_db_connection() as connection:
                logger.info(f"Starting AI processing for Lecture {task_id} with file {file_path}")
                db_repo = LectureDBRepository(connection)
                ai_transcription_service = AiTranscriptionService(db_repo=db_repo)
                processed_lecture_service = ProcessedLectureService(repo=db_repo)
                
                await db_repo.add_task(task_id=task_id, lecture_id=lecture_id)
                await ai_transcription_service.run(file_path=file_path, task_id=task_id, lecture_type_id=lecture_type_id)
                await processed_lecture_service.set_lecture_as_processed(lecture_id)
                
                return {"status": f"AI Lecture {task_id} processed successfully."}
            
    async def _regenerate_single_summary(self, task_id: int, new_prompt: str):
        async with get_db_connection() as connection:
            db_repo = LectureDBRepository(connection)
            service = RegenerateSummaryService(db_repo=db_repo)
            lecture_type = await db_repo.get_lecture_type_by_db_task_id(task_id)
            
            messages = {
                "system": await db_repo.get_system_message(lecture_type_id=lecture_type),
                "user": new_prompt
            }
            return await service.regenerate_summary(task_id=task_id, messages=messages)

    async def regenerate_summary_task(self, task_uuid: str, task_ids: list, new_prompt: str):
        tasks = [
            self._regenerate_single_summary(task_id=task_id, new_prompt=new_prompt) 
            for task_id in task_ids
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)

        successful_results = []
        failed_results = []
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Failed to regenerate summary for task_id {task_ids[i]}: {result}")
                failed_results.append({"task_id": task_ids[i], "error": str(result)})
            else:
                successful_results.append({"task_id": task_ids[i], "result": result})
        
        return {
            "task_id": task_uuid,
            "successful": len(successful_results),
            "failed": len(failed_results),
            "errors": failed_results
        }