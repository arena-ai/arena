from typing import Mapping, TypeVar, Generic
from copy import copy
from pydantic import BaseModel
from sqlmodel import Session
from app.ops import Op
from app.models import Event, EventCreate, User
from app import crud


A = TypeVar('A', bound=BaseModel)

class LogEvent(Op[tuple[Session, User, Event | None, A], Event], Generic[A]):
    name: str

    def event_create(self, parent: Event | None, a: A) -> EventCreate:
        return EventCreate(name=self.name, content=a.model_dump_json(), parent_id=None if parent is None else parent.id)

    async def call(self, session: Session, user: User, parent: Event | None, a: A) -> Event:
        event_create = self.event_create(parent, a)
        event = crud.create_event(session=session, event_in=event_create, owner_id=user.id)
        return event


class Request(BaseModel):
    method: str
    url: str
    headers: Mapping[str, str]
    content: str


class LogRequest(LogEvent[Request]):
    name: str = "request"


class BuildRequest(Op[tuple[str, str, Mapping[str, str], str], Request]):
    name: str = "build_request"

    async def call(self, method: str, url: str, headers: Mapping[str, str], content: str) -> Request:
        return Request(method=method, url=url, headers=headers, content=content)


class Response(BaseModel):
    status_code: int
    headers: Mapping[str, str]
    content: str


class LogResponse(LogEvent[Response]):
    name: str = "response"


class BuildResponse(Op[tuple[int, Mapping[str, str], str], Response]):
    name: str = "build_response"

    async def call(self, status_code: int, headers: Mapping[str, str], content: str) -> Request:
        return Request(status_code=status_code, headers=headers, content=content)