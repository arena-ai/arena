import os
from anyio import run
from celery import Celery
from app.core.config import settings
from app.ops import Op, Computation

app = Celery(__name__,
             broker=str(settings.CELERY_STORE_URI),
             result_backend=str(settings.CELERY_STORE_URI),
             event_serializer = 'pickle',
             task_serializer = 'pickle',
             result_serializer = 'pickle',
             accept_content = ['application/json', 'application/x-python-serialize'],
            )


@app.task
def evaluate(computation: Computation):
    return run(computation.evaluate)
