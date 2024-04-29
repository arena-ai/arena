from typing import Any, TypeVar, Generic

from pydantic import BaseModel
from sqlmodel import Session

from app.ops import Op
from app import crud
from app.models import Event, EventCreate, User, EventIdentifier
from app.lm.models import Score
from app.services import Request, Response



A = TypeVar('A', bound=BaseModel)

class LogEvent(Op[tuple[Session, User, Event | None, A], Event], Generic[A]):
    def event_create(self, parent: Event | None, a: A) -> EventCreate:
        return EventCreate(name=self.opname, content=a.model_dump_json(), parent_id=None if parent is None else parent.id)

    async def call(self, session: Session, user: User, parent: Event | None, a: A) -> Event:
        event_create = self.event_create(parent, a)
        event = crud.create_event(session=session, event_in=event_create, owner_id=user.id)
        return event


class LogRequest(LogEvent[Request]):
    pass

class LogResponse(LogEvent[Response]):
    pass

class EventIdentifier(Op[tuple[Session, User, Event, str], EventIdentifier]):
    async def call(self, session: Session, user: User, event: Event, identifier: str) -> EventIdentifier:
        # Add the native identifier to the parent event
        event_identifier = crud.create_event_identifier(session=session, event_identifier=identifier, event_id=event.id)
        return event_identifier



class LMJudgeEvaluation(LogEvent[Score]):
    pass

class UserEvaluation(LogEvent[Score]):
    pass