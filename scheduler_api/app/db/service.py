from app.db.repository import LectureRepository
import logging

logger = logging.getLogger(__name__)

class LectureService:
    def __init__(self, repo: LectureRepository):
        self.repo = repo

    async def create_lecture(self, lecture_recording_path: str, lecture_type: str):
        """Create a new lecture"""
        return await self.repo.create_lecture(lecture_recording_path, lecture_type)

