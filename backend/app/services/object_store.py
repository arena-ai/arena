from io import BytesIO
from typing import BinaryIO
from dataclasses import dataclass
from minio import Minio
from minio.helpers import ObjectWriteResult
from urllib3 import BaseHTTPResponse

from app.core.config import settings
from app.core.object_store import store

@dataclass
class Bucket:
    name: str
    object_store: Minio = store

    def put(self, name: str, data: BinaryIO) -> ObjectWriteResult:
        return store.put_object(bucket_name=self.name, object_name=name, data=data, length=-1, part_size=10000000)

    def puts(self, name: str, data: str) -> ObjectWriteResult:
        data = BytesIO(data.encode())
        return self.put(name, data)

    def get(self, name: str) -> BaseHTTPResponse:
        return store.get_object(bucket_name=self.name, object_name=name)
    
    def gets(self, name: str) -> str:
        data = self.get(name)
        print(data)
        return data.decode()

    def list(self, prefix: str | None=None, recursive: bool=False) -> list[str]:
        return [obj.object_name for obj in store.list_objects(bucket_name=self.name, prefix=prefix, recursive=recursive)]
    
    def remove(self, name: str) -> None:
        store.remove_object(bucket_name=self.name, object_name=name)
    
    def remove_all(self, name: str) -> None:
        for obj in store.list_objects(bucket_name=self.name, recursive=True):
            store.remove_object(bucket_name=self.name, object_name=obj.object_name)

@dataclass
class Documents(Bucket):
    name: str = settings.MINIO_DOCUMENT_BUCKET

@dataclass
class Models(Bucket):
    name: str = settings.MINIO_MODEL_BUCKET
