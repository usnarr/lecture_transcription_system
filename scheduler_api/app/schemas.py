from typing import List
from pydantic import BaseModel, Field, field_validator
from app.db.models import LectureTypeEnum

class TranscriptionTaskRequest(BaseModel):
    lecture_ids: List[int] = Field(..., min_length=1, max_length=100)

class AiTranscriptionTaskRequest(BaseModel):
    lecture_ids: List[int] = Field(..., min_length=1, max_length=100)

class RegenerateSummaryRequest(BaseModel):
    task_ids: List[int] = Field(..., min_length=1, max_length=10)
    prompt: str = Field(..., min_length=1, max_length=5000)

class CreateLectureRequest(BaseModel):
    lecture_recording_path: str = Field(..., min_length=1, max_length=500)
    lecture_type: LectureTypeEnum

    @field_validator("lecture_recording_path")
    @classmethod
    def validate_path(cls, v: str) -> str:
        if ".." in v:
            raise ValueError("Path traversal is not allowed")
        return v