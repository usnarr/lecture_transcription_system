from src.config import celery_app, WORKER_CONFIG
from fastapi import HTTPException

from src.logger import logger
from src.http import http_get


class ControllerService:
    def __init__(self):
        pass

    async def get_worker_gpu(self, gpu_status_url: str) -> int:
        """Call a worker's /gpu_status endpoint to get the available GPU memory."""
        if not gpu_status_url:
            logger.warning("GPU status URL is not configured")
            return 0
        try:
            response = await http_get(gpu_status_url, timeout=5)
            return response.get("available_models", 0)
        except Exception as e:
            logger.warning("Failed to get GPU status from %s: %s", gpu_status_url, e)
            return 0

    async def orchestrate_transcription(self, file_path: str, model_size: str):
        worker_statuses = {}
        for worker, config in WORKER_CONFIG.items():
            available_gpu = await self.get_worker_gpu(config["gpu_status_url"])
            worker_statuses[worker] = available_gpu

        # Check if any worker has GPU available
        if not any(worker_statuses.values()):
            logger.error("No GPU workers available.")
            raise HTTPException(status_code=503, detail="No GPU workers available.")

        selected_worker = max(worker_statuses, key=worker_statuses.get)
        selected_queue = WORKER_CONFIG[selected_worker]["celery_queue"]

        logger.info(
            "Dispatching task to %s (queue: %s) with available GPU: %s",
            selected_worker,
            selected_queue,
            worker_statuses[selected_worker],
        )

        task = celery_app.send_task(
            "transcribe_audio",
            kwargs={
                "file_path": file_path,
                "model_size": model_size,             
            },
            queue=selected_queue,
            routing_key=selected_queue,
        )
        logger.info("Queued task %s for worker %s", task.id, selected_worker)
        return {"status": "queued", "worker": selected_worker, "task_id": task.id}

    async def get_job_status(self, task_id: str):
        try:
            async_result = celery_app.AsyncResult(task_id)
            
            if not hasattr(async_result.backend, '_get_task_meta_for'):
                logger.warning("Celery result backend is disabled for task %s", task_id)
                raise HTTPException(
                    status_code=404,
                    detail=f"Task '{task_id}' not found."
                )
            
            status = async_result.status
            
         
            if status == 'PENDING':
                try:
                    meta = async_result.backend.get_task_meta(task_id)
                    if meta.get('status') == 'PENDING' and meta.get('result') is None:
                        raise HTTPException(
                            status_code=404,
                            detail=f"Task '{task_id}' not found"
                        )
                except HTTPException:
                    raise
                except Exception:
                    raise HTTPException(
                        status_code=404,
                        detail=f"Task '{task_id}' not found"
                    )
            
            result = async_result.result if async_result.ready() else None
            
            return {
                "task_id": task_id,
                "status": status,
                "result": result,
            }
        except HTTPException:
            raise
        except AttributeError as e:
            logger.error("Celery backend error for task %s: %s", task_id, e)
            raise HTTPException(
                status_code=404,
                detail=f"Task '{task_id}' not found. Result backend may not be configured."
            )
        except Exception as e:
            logger.error("Failed to get job status for task %s: %s", task_id, e)
            raise HTTPException(
                status_code=500,
                detail=f"Failed to retrieve job status: {str(e)}"
            )
            
    
