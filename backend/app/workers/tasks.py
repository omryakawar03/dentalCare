from app.workers.celery_app import celery_app


@celery_app.task(name="system.healthcheck")
def healthcheck() -> dict[str, str]:
    """Verify the worker process can receive and execute a task."""
    return {"status": "ok"}
