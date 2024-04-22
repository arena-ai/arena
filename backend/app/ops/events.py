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
    name: str = "log_request"