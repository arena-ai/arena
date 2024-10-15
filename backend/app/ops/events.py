from typing import TypeVar, Generic

from pydantic import BaseModel
from sqlmodel import Session

from app.ops import Op
import app.services.crud as crud
from app.models import EventCreate, EventOut, User, EventIdentifier
from app.lm.models import Score, LMConfig
from app.services import Request, Response


A = TypeVar("A", bound=BaseModel)


class LogEvent(
    Op[tuple[Session, User, EventOut | None, A], EventOut], Generic[A]
):
    name: str

    def event_create(self, parent: EventOut | None, a: A) -> EventCreate:
        return EventCreate(
            name=self.name,
            content=a.model_dump_json(),
            parent_id=None if parent is None else parent.id,
        )

    async def call(
        self, session: Session, user: User, parent: EventOut | None, a: A
    ) -> EventOut:
        event_create = self.event_create(parent, a)
        event = crud.create_event(
            session=session, event_in=event_create, owner_id=user.id
        )
        # Create a copy to avoid future mutations
        return EventOut.model_validate(event)


class LogRequest(LogEvent[Request]):
    name: str = "request"


log_request = LogRequest()


class LogResponse(LogEvent[Response]):
    name: str = "response"


log_response = LogResponse()


class CreateEventIdentifier(
    Op[tuple[Session, User, EventOut, str], EventIdentifier]
):
    async def call(
        self, session: Session, user: User, event: EventOut, identifier: str
    ) -> EventIdentifier:
        # Add the native identifier to the parent event
        event_identifier = crud.create_event_identifier(
            session=session, event_identifier=identifier, event_id=event.id
        )
        # Create a copy to avoid future mutations
        return event_identifier.model_copy()


create_event_identifier = CreateEventIdentifier()


class LogLMJudgeEvaluation(LogEvent[Score]):
    name: str = "lm_judge_evaluation"


log_lm_judge_evaluation = LogLMJudgeEvaluation()


class LogUserEvaluation(LogEvent[Score]):
    name: str = "user_evaluation"


log_user_evaluation = LogUserEvaluation()


class LogLMConfig(LogEvent[LMConfig]):
    name: str = "lm_config"


log_lm_config = LogLMConfig()
