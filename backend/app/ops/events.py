from typing import Any, TypeVar, Generic

from pydantic import BaseModel
from sqlmodel import Session

from app.ops import Op
import app.crud as crud
from app.models import Event, EventCreate, User, EventIdentifier
from app.lm.models import Score
from app.services import Request, Response



A = TypeVar('A', bound=BaseModel)

class LogEvent(Op[tuple[Session, User, Event | None, A], Event], Generic[A]):
    name: str

    def event_create(self, parent: Event | None, a: A) -> EventCreate:
        return EventCreate(name=self.name, content=a.model_dump_json(), parent_id=None if parent is None else parent.id)

    async def call(self, session: Session, user: User, parent: Event | None, a: A) -> Event:
        event_create = self.event_create(parent, a)
        event = crud.create_event(session=session, event_in=event_create, owner_id=user.id)
        # Create a copy to avoid future mutations
        return event.model_copy()

class LogRequest(LogEvent[Request]):
    name: str = "request"

log_request = LogRequest()

class LogResponse(LogEvent[Response]):
    name: str = "response"

log_response = LogResponse()

class LogEventIdentifier(Op[tuple[Session, User, Event, str], EventIdentifier]):
    async def call(self, session: Session, user: User, event: Event, identifier: str) -> EventIdentifier:
        # Add the native identifier to the parent event
        event_identifier = crud.create_event_identifier(session=session, event_identifier=identifier, event_id=event.id)
        # Create a copy to avoid future mutations
        return event_identifier.model_copy()

log_event_identifier = LogEventIdentifier()

class LogLMJudgeEvaluation(LogEvent[Score]):
    name: str = "ll_judge_evaluation"

log_lm_judge_evaluation = LogLMJudgeEvaluation()

class LogUserEvaluation(LogEvent[Score]):
    name: str = "user_evaluation"

log_user_evaluation = LogUserEvaluation()