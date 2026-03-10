from typing import List
from pydantic import BaseModel,Field
from app.db.models import LectureTypeEnum

class TranscriptionTaskRequest(BaseModel):
    lecture_ids: List[int]

class AiTranscriptionTaskRequest(BaseModel):
    lecture_ids: List[int]

class RegenerateSummaryRequest(BaseModel):
    task_ids: List[int]= Field(..., max_items=10)
    prompt: str

class CreateLectureRequest(BaseModel):
    lecture_recording_path: str
    lecture_type: LectureTypeEnum