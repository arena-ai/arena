from typing import Tuple, Mapping, TypeVar, Generic, Any
from pydantic import BaseModel
from sqlmodel import Session
from app.ops import Op
from app.models import Event, EventCreate, User
from app import crud


E = TypeVar('E')

class LogEvent(Op[Tuple[Session, User, list[Event]], Tuple[Session, User, list[Event]]], Generic[E]):
    name: str
    event: E
    
    def event_create(self, user: User, events: list[Event]) -> EventCreate:
        parent_id = None if len(events)==0 else events[0].parent_id
        return EventCreate(name=self.name, content=self.event, parent_id=parent_id)

    def log(self, session: Session, user: User, events: list[Event]) -> Event:
        event_create = self.event_create(user, events)
        return crud.create_event(session=session, event_in=event_create, owner_id=user.id)

    def call(self, input: Tuple[Session, User, list[Event]]) -> Tuple[Session, User, list[Event]]:
        session, user, events = input
        return events.append(self.log(session, user, events))


class RequestBase(BaseModel):
    method: str
    url: str
    headers: Mapping[str, str]
    content: Any | None
    parent: int | None
    owner: int | None

class RequestCreate(RequestBase):
    method: str
    url: str
    headers: Mapping[str, str]
    content: Any

class Request(RequestBase):
    method: str
    url: str
    headers: Mapping[str, str]
    content: Any
    parent: int | None
    owner: int

class LogRequest(LogEvent[RequestCreate]):
    def event_create(self, user: User, events: list[Event]) -> EventCreate:
        parent = None if len(events)==0 else events[0].parent_id
        request = Request(**self.event.model_dump(), parent=parent, owner=user.id)
        return EventCreate(name=self.name, content=request, parent_id=parent)