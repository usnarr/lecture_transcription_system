from src.common.db.repository import LectureDBRepository
import logging

logger = logging.getLogger(__name__)

class ProcessedLectureService:
    def __init__(self, repo: LectureDBRepository):
        self.repo: LectureDBRepository = repo

    async def set_lecture_as_processed(self, lecture_id):
        logger.info(f"Setting lecture {lecture_id} as processed")
        await self.repo.set_lecture_processed(lecture_id)

class ProcessingPathsCollectorService:

    def __init__(self, repo: LectureDBRepository, lecture_ids: list):
        self.repo: LectureDBRepository = repo
        self.lecture_ids = lecture_ids

    async def fetch_processing_paths(self):
        lectures = await self.repo.get_lectures_by_ids(self.lecture_ids)
        
        unprocessed_lectures = [l for l in lectures if not l['is_processed']]
        processing_data = [
            (lecture['lecture_id'], lecture['lecture_recording_path'], lecture['lecture_type'])
            for lecture in unprocessed_lectures
        ]
        
        return processing_data