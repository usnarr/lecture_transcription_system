from app.db.models import Lecture
from sqlalchemy import select, insert
from sqlalchemy.dialects import postgresql
import psycopg
import logging

logger = logging.getLogger(__name__)

class LectureRepository:
    def __init__(self, connection: psycopg.AsyncConnection):
        self.conn = connection

    async def create_lecture(self, lecture_recording_path: str, lecture_type: str):
        try:
            stmt = insert(Lecture).values(
                lecture_recording_path=lecture_recording_path,
                lecture_type=lecture_type
            ).returning(Lecture.lecture_id, Lecture.lecture_recording_path, Lecture.lecture_type)
            
            compiled = stmt.compile(dialect=postgresql.dialect(), compile_kwargs={"literal_binds": False})
            query = str(compiled)
            params = compiled.params
            
            async with self.conn.cursor() as cur:
                await cur.execute(query, params)
                result = await cur.fetchone()
                await self.conn.commit()
                logger.info(f"Created lecture with ID: {result[0]}")
                return {
                    "lecture_id": result[0],
                    "lecture_recording_path": result[1],
                    "lecture_type": result[2]
                }
        except Exception as e:
            logger.error(f"Error creating lecture: {str(e)}")
            raise