from typing import Any, TypeVar, Generic
from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from pydantic import BaseModel
import httpx

from app.services.models import Request, Response


Req = TypeVar("Req", bound=BaseModel)
Res = TypeVar("Res", bound=BaseModel)


@dataclass
class Service(ABC, Generic[Req, Res]):
    timeout: httpx.Timeout = field(
        default_factory=lambda: httpx.Timeout(30.0, read=None)
    )

    @abstractmethod
    def request(self, req: Req) -> Request[Req]:
        """Builds a service request from request content"""
        pass

    @abstractmethod
    def from_any(self, a: Any) -> Res:
        """Builds a service request from request content"""
        pass

    async def call(self, req: Req) -> Response[Res]:
        request = self.request(req)
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.request(
                method=request.method,
                url=request.url,
                headers=request.headers,
                json=request.content.model_dump(exclude_none=True),
            )
            if response.status_code == 200:
                return Response(
                    status_code=response.status_code,
                    headers=response.headers,
                    content=self.from_any(response.json()),
                )
            else:
                return Response(
                    status_code=response.status_code,
                    headers=response.headers,
                    content=None,
                )
