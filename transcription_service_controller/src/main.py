from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
from src.schemas import TranscriptionRequest, TranscriptionInsertRequest, GetTranscriptionOut
from src.service import ControllerService
from src.logger import logger
from src.db.redis import RedisClient
from src.db.repository import TranscriptionRepository
from src.config import REDIS_URL, REDIS_USERNAME, REDIS_PASSWORD

redis_client: RedisClient = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global redis_client
    # Initialize Redis client
    redis_client = RedisClient(
        url=REDIS_URL,
        username=REDIS_USERNAME,
        password=REDIS_PASSWORD
    )
    logger.info("Redis client initialized successfully")
    try:
        yield
    finally:
        # Close Redis connection
        redis_client.close()
        logger.info("Redis client closed")


app = FastAPI(title="Transcription Orchestrator API", lifespan=lifespan)


def get_redis_client() -> RedisClient:
    """Dependency to get Redis client"""
    if redis_client is None:
        raise HTTPException(status_code=503, detail="Redis client not initialized")
    return redis_client


@app.post("/transcribe")
async def orchestrate_transcription_endpoint(req: TranscriptionRequest,dry_run: bool = False):
    if dry_run:
        return {"status": "dry_run", "file_path": req.file_path, "model_size": req.model_size}
    service = ControllerService()
    logger.info("Received transcription request: %s", req.model_dump_json())
    response = await service.orchestrate_transcription(req.file_path, req.model_size)
    logger.info("Dispatched transcription task: %s", response)
    return {
        "job_id": response["task_id"],
        "status": response["status"],
        "worker": response["worker"]
    }


@app.get("/job_status")
async def get_job_status(task_id: str):
    service = ControllerService()
    return await service.get_job_status(task_id)


@app.get("/ping")   
async def ping():
    return {"status": "ok"}


@app.post("/add_transcription")
async def add_transcription(payload: TranscriptionInsertRequest):
    """Store transcription in Redis with 5-minute TTL"""
    try:
        repo = TranscriptionRepository(redis_client=get_redis_client())
        task_id = repo.add_transcription(payload.transcription, payload.task_id)
        logger.info(f"Transcription stored for task {task_id}")
        return {
            "task_id": task_id,
            "status": "stored",
            "ttl_seconds": 300
        }
    except Exception as e:
        logger.error(f"Failed to store transcription: {e}")
        raise HTTPException(status_code=500, detail="Failed to store transcription")


@app.get("/transcriptions/{transcription_id}", response_model=GetTranscriptionOut)
async def get_transcription(transcription_id: str):
    """Retrieve transcription from Redis"""
    try:
        repo = TranscriptionRepository(redis_client=get_redis_client())
        transcription = repo.get_transcription(transcription_id)
        
        if transcription:
            return transcription
        else:
            raise HTTPException(
                status_code=404,
                detail="Transcription not found or expired"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve transcription: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve transcription")


