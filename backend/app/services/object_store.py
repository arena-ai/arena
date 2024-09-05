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

    def get(self, name: str ) -> BaseHTTPResponse:
        return store.get_object(bucket_name=self.name, object_name=name)

@dataclass
class Documents(Bucket):
    name: str = settings.MINIO_DOCUMENT_BUCKET

@dataclass
class Models(Bucket):
    name: str = settings.MINIO_MODEL_BUCKET
