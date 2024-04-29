from typing import Mapping, Any
import json

from fastapi import APIRouter

from app.api.deps import CurrentUser, SessionDep
from app import crud
from app.models import User, Event, EventCreate
from app.lm.models import Evaluation, Score
from app.ops.session import Session, User, EventIdentifier, Event
from app.ops.events import UserEvaluation



router = APIRouter()


@router.post("/evaluation", response_model=Event)
async def evaluation(
    session: SessionDep, current_user: CurrentUser, evaluation: Evaluation
) -> Event:
    sess = Session()()
    user = User(id=current_user.id)(sess)
    event_identifier = EventIdentifier(id=evaluation.identifier)(sess)
    user_evaluation = UserEvaluation()(sess, user, event_identifier.event, evaluation.score)
    return await user_evaluation.evaluate(session=session)


@router.get("/evaluation/{identifier}/{score}", response_model=Event)
async def evaluation_get(
    session: SessionDep, current_user: CurrentUser, identifier: str, score: float
) -> Event:
    sess = Session()()
    user = User(id=current_user.id)(sess)
    event_identifier = EventIdentifier(id=identifier)(sess)
    user_evaluation = UserEvaluation()(sess, user, event_identifier.event, Score(value=score))
    return await user_evaluation.evaluate(session=session)

