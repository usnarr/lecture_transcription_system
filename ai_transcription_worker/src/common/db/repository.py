import psycopg
import logging

logger = logging.getLogger(__name__)

class LectureDBRepository:
    def __init__(self, connection: psycopg.AsyncConnection):
        self.conn = connection

    async def get_system_message(self, lecture_type: str):
        """Get system prompt by lecture type"""
        query = """
            SELECT prompt_text
            FROM public.prompts
            WHERE type = %s
        """
        async with self.conn.cursor() as cur:
            await cur.execute(query, (f"{lecture_type}_system_prompt",))
            row = await cur.fetchone()
            return row[0] if row else None

    async def get_prompt_message(self, lecture_type: str):
        """Get user prompt by lecture type"""
        query = """
            SELECT prompt_text
            FROM public.prompts
            WHERE type = %s
        """
        async with self.conn.cursor() as cur:
            await cur.execute(query, (f"{lecture_type}_user_prompt",))
            row = await cur.fetchone()
            return row[0] if row else None

    async def save_summary(self, summary: str):
        """Save summary and return the created record"""
        query = """
            INSERT INTO public.summaries (summary_text)
            VALUES (%s)
            RETURNING id, summary_text, last_processing_timestamp
        """
        async with self.conn.cursor() as cur:
            await cur.execute(query, (summary,))
            row = await cur.fetchone()
            await self.conn.commit()
            if row:
                columns = [desc[0] for desc in cur.description]
                return dict(zip(columns, row))
            return None
    
    async def get_lecture_type_by_task_id(self, task_id: str):
        """Get lecture type by task celery_task_id"""
        query = """
            SELECT l.lecture_type
            FROM public.lectures l
            JOIN public.tasks t ON l.task_id = t.id
            WHERE t.celery_task_id = %s
        """
        async with self.conn.cursor() as cur:
            await cur.execute(query, (task_id,))
            row = await cur.fetchone()
            return row[0] if row else None

    async def get_lecture_type_by_db_task_id(self, task_id: int):
        """Get lecture type by task database ID"""
        query = """
            SELECT l.lecture_type
            FROM public.lectures l
            JOIN public.tasks t ON l.task_id = t.id
            WHERE t.id = %s
        """
        async with self.conn.cursor() as cur:
            await cur.execute(query, (task_id,))
            row = await cur.fetchone()
            return row[0] if row else None
    
    async def save_transcription(self, transcription: str):
        """Save transcription and return the created record"""
        query = """
            INSERT INTO public.transcriptions (transcription_text)
            VALUES (%s)
            RETURNING id, transcription_text
        """
        async with self.conn.cursor() as cur:
            await cur.execute(query, (transcription,))
            row = await cur.fetchone()
            await self.conn.commit()
            if row:
                columns = [desc[0] for desc in cur.description]
                return dict(zip(columns, row))
            return None

    async def add_task(self, task_id: str, lecture_id: int):
        """Create a new task and link it to a lecture"""
        query = """
            INSERT INTO public.tasks (celery_task_id, task_status_id)
            VALUES (%s, 1)
            RETURNING id
        """
        async with self.conn.cursor() as cur:
            await cur.execute(query, (task_id,))
            row = await cur.fetchone()
            await self.conn.commit()
            if row:
                task_db_id = row[0]
                await self.update_lecture_task(lecture_id, task_db_id)
                return task_db_id
            return None

    async def update_lecture_task(self, lecture_id: int, task_id: int):
        """Update lecture's task_id"""
        query = """
            UPDATE public.lectures
            SET task_id = %s
            WHERE lecture_id = %s
        """
        async with self.conn.cursor() as cur:
            await cur.execute(query, (task_id, lecture_id))
            await self.conn.commit()

    async def get_lectures_by_ids(self, lecture_ids: list[int]):
        """Get lectures by their IDs"""
        if not lecture_ids:
            return []
        
        query = """
            SELECT 
                lecture_id,
                lecture_recording_path,
                lecture_type,
                is_processed,
                task_id
            FROM public.lectures
            WHERE lecture_id = ANY(%s)
        """
        async with self.conn.cursor() as cur:
            await cur.execute(query, (lecture_ids,))
            rows = await cur.fetchall()
            columns = [desc[0] for desc in cur.description]
            return [dict(zip(columns, row)) for row in rows]

    async def set_lecture_processed(self, lecture_id: int):
        """Mark a lecture as processed"""
        query = """
            UPDATE public.lectures
            SET is_processed = TRUE
            WHERE lecture_id = %s
        """
        async with self.conn.cursor() as cur:
            await cur.execute(query, (lecture_id,))
            await self.conn.commit()
            logger.info(f"Lecture {lecture_id} marked as processed")

    async def get_task_by_id(self, task_id: int):
        """Get task by database ID"""
        query = """
            SELECT id, task_status_id, transcription_id, summary_id, celery_task_id, last_processing_timestamp
            FROM public.tasks
            WHERE id = %s
        """
        async with self.conn.cursor() as cur:
            await cur.execute(query, (task_id,))
            row = await cur.fetchone()
            if row:
                columns = [desc[0] for desc in cur.description]
                return dict(zip(columns, row))
            return None
    
    async def get_transcription_by_id(self, transcription_id: int):
        """Get transcription by ID"""
        query = """
            SELECT id, transcription_text
            FROM public.transcriptions
            WHERE id = %s
        """
        async with self.conn.cursor() as cur:
            await cur.execute(query, (transcription_id,))
            row = await cur.fetchone()
            if row:
                columns = [desc[0] for desc in cur.description]
                return dict(zip(columns, row))
            return None

    async def update_summary(self, summary_id: int, new_summary_text: str):
        """Update an existing summary"""
        query = """
            UPDATE public.summaries
            SET summary_text = %s
            WHERE id = %s
            RETURNING id, summary_text, last_processing_timestamp
        """
        async with self.conn.cursor() as cur:
            await cur.execute(query, (new_summary_text, summary_id))
            row = await cur.fetchone()
            await self.conn.commit()
            if row:
                columns = [desc[0] for desc in cur.description]
                return dict(zip(columns, row))
            return None

    async def update_task(self, task_id: str, status=None, transcription_id=None, summary_id=None):
        """Update task by celery task ID"""
        updates = []
        params = []
        
        if status is not None:
            updates.append("task_status_id = %s")
            params.append(status)
        if transcription_id is not None:
            updates.append("transcription_id = %s")
            params.append(transcription_id)
        if summary_id is not None:
            updates.append("summary_id = %s")
            params.append(summary_id)
        
        if not updates:
            return None
        
        params.append(task_id)
        query = f"""
            UPDATE public.tasks
            SET {', '.join(updates)}
            WHERE celery_task_id = %s
            RETURNING id, task_status_id, transcription_id, summary_id, celery_task_id, last_processing_timestamp
        """
        
        async with self.conn.cursor() as cur:
            await cur.execute(query, params)
            row = await cur.fetchone()
            await self.conn.commit()
            if row:
                columns = [desc[0] for desc in cur.description]
                return dict(zip(columns, row))
            return None
        

    
