from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep
from app.models import Message, Event, EventCreate, EventOut, EventsOut, EventUpdate, EventIdentifier

router = APIRouter()


@router.get("/", response_model=EventsOut)
def read_events(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve Events.
    """

    if current_user.is_superuser:
        statement = select(func.count()).select_from(Event)
        count = session.exec(statement).one()
        statement = select(Event).offset(skip).limit(limit)
        events = session.exec(statement).all()
    else:
        statement = (
            select(func.count())
            .select_from(Event)
            .where(Event.owner_id == current_user.id)
        )
        count = session.exec(statement).one()
        statement = (
            select(Event)
            .where(Event.owner_id == current_user.id)
            .offset(skip)
            .limit(limit)
        )
        events = session.exec(statement).all()

    return EventsOut(data=events, count=count)


@router.get("/{id}", response_model=EventOut)
def read_event(session: SessionDep, current_user: CurrentUser, id: int) -> Any:
    """
    Get event by ID.
    """
    event = session.get(Event, id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    if not current_user.is_superuser and (event.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return event


@router.post("/", response_model=EventOut)
def create_event(
    *, session: SessionDep, current_user: CurrentUser, event_in: EventCreate
) -> Any:
    """
    Create new event.
    """
    event = Event.model_validate(event_in, update={"owner_id": current_user.id})
    session.add(event)
    session.commit()
    session.refresh(event)
    return event


@router.put("/{id}", response_model=EventOut)
def update_event(
    *, session: SessionDep, current_user: CurrentUser, id: int, event_in: EventUpdate
) -> Any:
    """
    Update an event.
    """
    event = session.get(Event, id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    if not current_user.is_superuser and (event.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    update_dict = event_in.model_dump(exclude_unset=True)
    event.sqlmodel_update(update_dict)
    session.add(event)
    session.commit()
    session.refresh(event)
    return event


@router.delete("/{id}")
def delete_event(session: SessionDep, current_user: CurrentUser, id: int) -> Message:
    """
    Delete an event.
    """
    event = session.get(Event, id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    if not current_user.is_superuser and (event.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    session.delete(event)
    session.commit()
    return Message(message="Event deleted successfully")


@router.get("/identifier/{identifier}", response_model=EventIdentifier)
def read_event_by_identifier(
    *, session: SessionDep, current_user: CurrentUser, id: int, identifier: str
) -> Any:
    """
    Get event by identifier.
    """
    statement = select(Event).join(EventIdentifier).where(EventIdentifier.id == identifier)
    event = session.exec(statement).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    if not current_user.is_superuser and (event.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return event

@router.get("/{id}/identifier/{identifier}", response_model=EventIdentifier)
def create_event_identifier_get(
    *, session: SessionDep, current_user: CurrentUser, id: int, identifier: str
) -> Any:
    """
    Create new event identifier.
    """
    event_identifier = EventIdentifier(id=identifier, event_id=id)
    session.add(event_identifier)
    session.commit()
    session.refresh(event_identifier)
    return event_identifier


@router.post("/identifier", response_model=EventIdentifier)
def create_event_identifier(
    *, session: SessionDep, current_user: CurrentUser, event_identifier: EventIdentifier
) -> Any:
    """
    Create new event identifier.
    """
    session.add(event_identifier)
    session.commit()
    session.refresh(event_identifier)
    return event_identifier


@router.post("/attribute", response_model=EventIdentifier)
def create_event_identifier(
    *, session: SessionDep, current_user: CurrentUser, event_identifier: EventIdentifier
) -> Any:
    """
    Create new event identifier.
    """
    session.add(event_identifier)
    session.commit()
    session.refresh(event_identifier)
    return event_identifier