from pydantic import BaseModel


class TranscriptionRequest(BaseModel):
    file_path: str
    model_size: str = "large"


class TranscriptionInsertRequest(BaseModel):
    transcription: str
    task_id: str


class GetTranscriptionOut(BaseModel):
    id: str
    transcription: str
    ttl: int