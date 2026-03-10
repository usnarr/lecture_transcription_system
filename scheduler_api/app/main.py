from fastapi import FastAPI, HTTPException, Depends
from app.celery_config.celery_conf import celery_app
from app.tasks import Tasks
from app.schemas import TranscriptionTaskRequest, AiTranscriptionTaskRequest, RegenerateSummaryRequest, CreateLectureRequest
from app.db.database import get_db_connection
from app.db.repository import LectureRepository
from app.db.service import LectureService
import psycopg

app = FastAPI()

async def get_lecture_repository(conn: psycopg.AsyncConnection = Depends(get_db_connection)) -> LectureRepository:
    return LectureRepository(conn)

@app.post("/lectures")
async def create_lecture(
    request: CreateLectureRequest,
    repo: LectureRepository = Depends(get_lecture_repository)
):
    try:
        service = LectureService(repo)
        lecture = await service.create_lecture(
            lecture_recording_path=request.lecture_recording_path,
            lecture_type=request.lecture_type.value
        )
        return {"message": "Lecture created successfully", "lecture": lecture}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating lecture: {str(e)}")

@app.post("/schedule/transcription-task")
async def schedule_transcription_task(task_req: TranscriptionTaskRequest):
    try:
        task_id = celery_app.send_task(
            Tasks.TRANSCRIPTION_TASK.value, 
            args=[task_req.lecture_ids]
        )
        return {"message": "Transcription task scheduled", "task_id": str(task_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error scheduling transcription task: {str(e)}")

@app.post("/schedule/ai-transcription-task")
async def schedule_ai_transcription_task(task_req: AiTranscriptionTaskRequest):
    try:
        task_id = celery_app.send_task(
            Tasks.AI_TRANSCRIPTION_TASK.value, 
            args=[task_req.lecture_ids]
        )
        return {"message": "AI Transcription task scheduled", "task_id": str(task_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error scheduling AI transcription task: {str(e)}")
    
@app.post("/processing/regenerate-summary")
async def regenerate_summary(task_req:RegenerateSummaryRequest):
    try:
        task_id = celery_app.send_task(
            Tasks.REGENERATE_SUMMARY_TASK.value, 
            args=[task_req.task_ids, task_req.prompt]
        )
        return {"message": "Summary regeneration task scheduled", "task_id": str(task_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error scheduling summary regeneration task: {str(e)}")