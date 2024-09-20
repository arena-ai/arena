from typing import Mapping, Any
import json

from fastapi import APIRouter

from app.api.deps import CurrentUser, SessionDep
from app import models
from app.lm.models import Evaluation, Score
from app.ops.session import Session, User, EventIdentifier, Event
from app.ops.events import LogUserEvaluation
from app.services import crud



router = APIRouter()


@router.post("/evaluation", response_model=models.Event)
async def evaluation(
    session: SessionDep, current_user: CurrentUser, evaluation: Evaluation
) -> models.Event:
    sess = Session()()
    user = User()(sess, current_user.id)
    event_identifier = EventIdentifier()(sess, evaluation.identifier)
    event = Event()(sess, event_identifier.event_id)
    user_evaluation = LogUserEvaluation()(sess, user, event, evaluation.value)
    return await user_evaluation.evaluate(session=session)


@router.get("/evaluation/{identifier}/{score}", response_model=models.Event)
async def evaluation_get(
    session: SessionDep, current_user: CurrentUser, identifier: str, score: float
) -> models.Event:
    sess = Session()()
    user = User()(sess, current_user.id)
    event_identifier = EventIdentifier()(sess, identifier)
    event = Event()(sess, event_identifier.event_id)
    user_evaluation = LogUserEvaluation()(sess, user, event, Score(value=score))
    return await user_evaluation.evaluate(session=session)

