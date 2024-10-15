from typing import Mapping, TypeVar, Generic, Literal
from pydantic import BaseModel, Field


C = TypeVar("C", bound=BaseModel)


class Request(BaseModel, Generic[C]):
    method: Literal["GET", "POST"]
    url: str
    headers: Mapping[str, str] = Field(default_factory=lambda: {})
    content: C


class Response(BaseModel, Generic[C]):
    status_code: int = 500
    headers: Mapping[str, str] = Field(default_factory=lambda: {})
    content: C | None = None
