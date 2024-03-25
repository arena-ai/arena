from typing import Any

from sqlmodel import Session, select

from app.models import User
from app.events.models import Event, EventCreate

def create_event(*, session: Session, event_in: EventCreate, owner_id: int) -> Event:
    db_event = Event.model_validate(event_in, update={"owner_id": owner_id})
    session.add(db_event)
    session.commit()
    session.refresh(db_event)
    return db_event
