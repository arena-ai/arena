from minio import Minio
from app.core.config import settings

store = Minio(
    f"{settings.MINIO_SERVER}:{settings.MINIO_PORT}",
    access_key=settings.MINIO_ACCESS_KEY,
    secret_key=settings.MINIO_SECRET_KEY,
)

def init_store(object_storage: Minio) -> None:
    for bucket in [
        settings.MINIO_DOCUMENT_BUCKET,
        settings.MINIO_MODEL_BUCKET,
    ]:
        if not object_storage.bucket_exists(bucket):
            object_storage.make_bucket(bucket)