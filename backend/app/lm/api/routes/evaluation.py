from typing import Mapping, Any
import json

from fastapi import APIRouter
from sqlmodel import Session, func, select

from app.api.deps import CurrentUser, SessionDep
from app import crud
from app.models import User, Event, EventCreate
from app.lm.models import Evaluation


router = APIRouter()


async def evaluation_event(session: Session, current_user: User, evaluation: Evaluation) -> Event:
    # Create an evaluation event
    print(f"\n\nDEBUG {evaluation}")
    event_identifier = crud.get_event_identifier(session=session, event_identifier=evaluation.identifier)
    event_create = EventCreate(name="evaluation", content=json.dumps(evaluation.score), parent_id=event_identifier.event_id)
    event = crud.create_event(session=session, event_in=event_create, owner_id=current_user.id)
    return event


@router.post("/evaluation", response_model=Event)
async def evaluation(
    session: SessionDep, current_user: CurrentUser, evaluation: Evaluation
) -> Event:
    return await evaluation_event(session=session, current_user=current_user, evaluation=evaluation)


@router.get("/evaluation/{identifier}/{score}", response_model=Event)
async def evaluation_get(
    session: SessionDep, current_user: CurrentUser, identifier: str, score: float
) -> Event:
    evaluation = Evaluation(identifier=identifier, score=score)
    return await evaluation_event(session=session, current_user=current_user, evaluation=evaluation)

