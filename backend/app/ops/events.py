from typing import Tuple, Mapping, TypeVar, Generic
from copy import copy
from pydantic import BaseModel
from sqlmodel import Session
from app.ops import Op
from app.models import Event, EventCreate, User
from app import crud


E = TypeVar('E')

class LogEvent(Op[Tuple[Session, User, list[Event], E], Tuple[Session, User, list[Event], E]], Generic[E]):
    name: str

    def event_create(self, user: User, previous_events: list[Event], e: E) -> EventCreate:
        raise NotImplementedError

    def log(self, session: Session, user: User, previous_events: list[Event], e: E) -> Event:
        event_create = self.event_create(user, previous_events, e)
        event = crud.create_event(session=session, event_in=event_create, owner_id=user.id)
        return event

    def call(self, input: Tuple[Session, User, list[Event], E]) -> Tuple[Session, User, list[Event], E]:
        session, user, previous_events, e = input
        event = self.log(session, user, previous_events, e)
        previous_events.append(copy(event))
        return (session, user, previous_events, e)


class RequestBase(BaseModel):
    method: str
    url: str
    headers: Mapping[str, str]
    content: str | None
    parent: int | None
    owner: int | None

class RequestCreate(RequestBase):
    content: str
    parent: int | None = None
    owner: int | None = None

class Request(RequestBase):
    method: str
    url: str
    headers: Mapping[str, str]
    content: str
    parent: int | None
    owner: int

class LogRequest(LogEvent[RequestCreate]):
    def event_create(self, user: User, previous_events: list[Event], e: RequestCreate) -> EventCreate:
        parent = None if len(previous_events)==0 else previous_events[0].id
        request = Request(**e.model_dump(exclude_none=True), parent=parent, owner=user.id)
        return EventCreate(name=self.name, content=request.model_dump_json(), parent_id=parent)