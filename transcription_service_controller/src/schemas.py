from pydantic import BaseModel, Field, field_validator


class TranscriptionRequest(BaseModel):
    file_path: str = Field(..., min_length=1, max_length=500)
    model_size: str = "large"

    @field_validator("file_path")
    @classmethod
    def validate_path(cls, v: str) -> str:
        if ".." in v:
            raise ValueError("Path traversal is not allowed")
        return v


class TranscriptionInsertRequest(BaseModel):
    transcription: str
    task_id: str


class GetTranscriptionOut(BaseModel):
    id: str
    transcription: str
    ttl: int