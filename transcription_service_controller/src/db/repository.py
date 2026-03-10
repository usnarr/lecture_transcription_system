from src.db.redis import RedisClient
from src.config import TRANSCRIPTION_TTL
from src.logger import logger


class TranscriptionRepository:
    def __init__(self, redis_client: RedisClient):
        self.redis_client = redis_client
        
    def add_transcription(self, transcription: str, task_id: str) -> str:
        """Store transcription in Redis with TTL"""
        key = f"transcription:{task_id}"
        try:
            self.redis_client.set(key, transcription, ex=TRANSCRIPTION_TTL)
            logger.info(f"Stored transcription for task {task_id} with {TRANSCRIPTION_TTL}s TTL")
            return task_id
        except Exception as e:
            logger.error(f"Failed to store transcription for task {task_id}: {e}")
            raise
    
    def get_transcription(self, task_id: str) -> dict:
        """Retrieve transcription from Redis"""
        key = f"transcription:{task_id}"
        try:
            transcription = self.redis_client.get(key)
            if transcription:
                ttl = self.redis_client.ttl(key)
                logger.info(f"Retrieved transcription for task {task_id}, TTL: {ttl}s")
                return {
                    "id": task_id,
                    "transcription": transcription,
                    "ttl": ttl
                }
            else:
                logger.warning(f"Transcription not found for task {task_id}")
                return None
        except Exception as e:
            logger.error(f"Failed to retrieve transcription for task {task_id}: {e}")
            raise
    
    def delete_transcription(self, task_id: str) -> bool:
        """Delete transcription from Redis"""
        key = f"transcription:{task_id}"
        try:
            result = self.redis_client.delete(key)
            logger.info(f"Deleted transcription for task {task_id}")
            return result > 0
        except Exception as e:
            logger.error(f"Failed to delete transcription for task {task_id}: {e}")
            raise
    
    def transcription_exists(self, task_id: str) -> bool:
        """Check if transcription exists in Redis"""
        key = f"transcription:{task_id}"
        return self.redis_client.exists(key)