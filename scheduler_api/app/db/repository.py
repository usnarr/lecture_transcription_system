import psycopg
import logging

logger = logging.getLogger(__name__)

class LectureRepository:
    def __init__(self, connection: psycopg.AsyncConnection):
        self.conn = connection

    async def create_lecture(self, lecture_recording_path: str, lecture_type: str):
        query = """
            INSERT INTO public.lectures (lecture_recording_path, lecture_type)
            VALUES (%s, %s)
            RETURNING lecture_id, lecture_recording_path, lecture_type
        """
        async with self.conn.cursor() as cur:
            await cur.execute(query, (lecture_recording_path, lecture_type))
            result = await cur.fetchone()
            await self.conn.commit()
            if result:
                logger.info(f"Created lecture with ID: {result[0]}")
                return {
                    "lecture_id": result[0],
                    "lecture_recording_path": result[1],
                    "lecture_type": result[2]
                }
            return None