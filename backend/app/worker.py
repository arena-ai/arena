import json
from sqlmodel import Session
from pydantic import BaseModel
from anyio import run
from kombu.utils.json import register_type
from celery import Celery
from app.core.config import settings
from app.core.db import engine
from app.ops import Computation
from app.ops.computation import JsonSerializable

# Register Computations
register_type(
    Computation,
    'computation',
    lambda o: o.to_json(),
    lambda o: Computation.from_json(o),
)
register_type(
    JsonSerializable,
    'json_serializable',
    lambda o: o.to_json(),
    lambda o: JsonSerializable.from_json(o),
)
register_type(
    BaseModel,
    'base_model',
    lambda o: json.dumps(JsonSerializable.to_json_dict(o)),
    lambda o: JsonSerializable.from_json(o),
)

# Modify computation to avoid infinite loops
Computation.__json__ = None

app = Celery(__name__,
             broker=str(settings.CELERY_STORE_URI),
             result_backend=str(settings.CELERY_STORE_URI),
             serializer = 'json',
             accept_content = ['application/json'],
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
