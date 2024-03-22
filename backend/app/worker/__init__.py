import os
from celery import Celery
from app.core.config import settings

app = Celery(__name__, broker=str(settings.CELERY_STORE_URI), result_backend=str(settings.CELERY_STORE_URI))
