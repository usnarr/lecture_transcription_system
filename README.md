# Lecture Transcription + AI Summary System

A distributed microservices architecture for processing lecture recordings with transcription and AI-powered summarization.

## System Architecture

```
┌─────────────────┐
│ Scheduler API   │  ← Schedule tasks & manage lectures
└────────┬────────┘
         │
         ▼
┌─────────────────────────────┐
│ AI Transcription Worker     │  ← Process tasks & orchestrate
│ (Celery-based)              │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│ Transcription Controller    │  ← Load balance across GPU workers
│ (Celery + Redis)            │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│ Transcription Workers       │  ← Execute Whisper on GPU machines
│ (GPU Celery Workers)        │
└─────────────────────────────┘
```

## Components

### 1. **Scheduler API** (`scheduler_api/`)
- REST API for scheduling transcription tasks
- Manages lecture metadata in database
- Triggers AI transcription pipeline


### 2. **AI Transcription Worker** (`ai_transcription_worker/`)
- Celery worker that orchestrates the transcription workflow
- Fetches custom AI prompts per lecture type from database
- Coordinates between transcription and AI summarization
- Writes final results to database


### 3. **Transcription Controller** (`transcription_service_controller/`)
- Distributes transcription tasks across available GPU workers
- Load balances based on GPU availability and model capacity
- Stores transcription results in Redis with TTL


### 4. **Transcription Service** (`transcription_service/`)
- GPU-accelerated Whisper transcription workers
- Celery workers deployed on GPU machines
- Processes audio files with OpenAI Whisper models
- Reports GPU status and available models



## Tech Stack

- **Languages**: Python 3.11+
- **Frameworks**: FastAPI, Celery
- **Message Broker**: RabbitMQ
- **Caching**: Redis
- **Database**: PostgreSQL
- **ML Models**: OpenAI Whisper
- **Containerization**: Docker, Docker Compose
- **Package Manager**: Poetry


## Workflow
1. **Add Lecture** - add a lecture record into the database via scheduler api
2. **Schedule** a lecture transcription + summary via Scheduler API
3. **AI Worker** creates task and schedules transcription
4. **Controller** receives transcription request and selects optimal GPU worker
5. **GPU Worker** transcribes audio using Whisper and sends back the result
6. **Controller** stores result in Redis
7. **AI Worker** retrieves transcription, applies AI summary, writes  results to DB


## Docker compose and setup

### Full system launch
1. Copy `.env.template` to `.env` in the project root and fill in your values
2. Run `docker compose up -d` from the project root to start all services

### Standalone services
Each service also has its own `docker-compose.yml` for standalone development.
Refer to `.env.template` files in each service directory.

### Database
Docker compose automatically creates the tables via `scheduler_api/init.sql`.
Fill in the `prompts` table for the lecture types:
- Add `_user_prompt` after the type for the user prompt
- Add `_system_prompt` after the type for the system instructions

## Author
Kamil Pyszek