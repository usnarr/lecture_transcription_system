from src.celery_app import celery_app
from .api import Tasks
from src.common.controller import Controller
import asyncio


@celery_app.task(name=Tasks.SAMPLE_TASK.value)
def sample_task():
    return "Sample task executed successfully!"

@celery_app.task(name=Tasks.TRANSCRIPTION_TASK.value)
def transcription_task(lecture_ids: list):
    """
    Celery task to execute transcription for lectures.
    Args:
        lecture_ids: List of lecture IDs to process
    """
    task_uuid = transcription_task.request.id 
    controller = Controller()
    result = asyncio.run(controller.run_transcription_task(task_uuid, lecture_ids))
    return result

@celery_app.task(name=Tasks.AI_TRANSCRIPTION_TASK.value)
def ai_transcription_task(lecture_ids: list):
    """
    Celery task to execute AI transcription for lectures.
    Args:
        lecture_ids: List of lecture IDs to process
    """
    task_uuid = ai_transcription_task.request.id
    controller = Controller()
    result = asyncio.run(controller.run_ai_transcription_task(task_uuid, lecture_ids))
    return result

@celery_app.task(name=Tasks.REGENERATE_SUMMARY_TASK.value)
def regenerate_summary_task( task_ids: list, prompt: str):
    """
    Celery task to regenerate summaries.
    Args:
        task_ids: List of task IDs to regenerate
        prompt: New prompt for regeneration
    """
    task_uuid = regenerate_summary_task.request.id
    controller = Controller()
    result = asyncio.run(controller.regenerate_summary_task(
        task_uuid=task_uuid,
        task_ids=task_ids,
        new_prompt=prompt
    ))
    return result