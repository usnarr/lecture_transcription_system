import logging

from fastapi import FastAPI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Transcription Worker API")


@app.get("/health")
def health():
    return {"status": "ok"}