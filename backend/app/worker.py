import os
from sqlmodel import Session
from anyio import run
from celery import Celery
from app.core.config import settings
from app.core.db import engine
from app.ops import Op, Computation

app = Celery(__name__,
             broker=str(settings.CELERY_STORE_URI),
             result_backend=str(settings.CELERY_STORE_URI),
             event_serializer = 'pickle',
             task_serializer = 'pickle',
             result_serializer = 'pickle',
             accept_content = ['application/json', 'application/x-python-serialize'],
            )


@app.task(autoretry_for = (Exception,), max_retries = 3, retry_backoff = True)
def evaluate(computation: Computation):
    try:
        with Session(engine) as session:
            #  Define the evaluation method
            async def evaluate_with_context():
                return await computation.evaluate(session=session)
            # Run the evaluation
            result = run(evaluate_with_context)
        return result
    except Exception as e:
        raise e
