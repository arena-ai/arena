from typing import Mapping, Sequence, Literal, BinaryIO, Any
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pydantic import BaseModel, Field, TypeAdapter
from minio import Minio
from minio.helpers import ObjectWriteResult
from urllib3 import BaseHTTPResponse

from app.lm.models import ChatCompletionResponse, ChatCompletionRequest, openai, mistral, anthropic
from app.core.config import settings
from app.core.object_store import store

@dataclass
class Bucket:
    name: str
    object_store: Minio = store

    def put(self, name: str, data: BinaryIO) -> ObjectWriteResult:
        return store.put_object(bucket_name=self.name, object_name=name, data=data, length=-1, part_size=10000000)

    def get(self, name: str) -> BaseHTTPResponse:
        return store.get_object(bucket_name=self.name, object_name=name)

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
