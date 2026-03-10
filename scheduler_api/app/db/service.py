from app.db.repository import LectureRepository
import logging

logger = logging.getLogger(__name__)

class LectureService:
    def __init__(self, repo: LectureRepository):
        self.repo = repo

    async def create_lecture(self, lecture_recording_path: str, lecture_type: str):
        """Create a new lecture"""
        try:
            
            lecture = await self.repo.create_lecture( lecture_recording_path, lecture_type)
            logger.info(f"Created lecture: {lecture}")
            return lecture
        except Exception as e:
            logger.error(f"Error creating lecture: {str(e)}")
            raise

