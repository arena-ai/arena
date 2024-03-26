from sqlmodel import Session

from app import crud
from app.models import Event, EventCreate
from app.tests.utils.user import create_random_user
from app.tests.utils.utils import random_lower_string


def create_random_event(db: Session) -> Event:
    user = create_random_user(db)
    owner_id = user.id
    assert owner_id is not None
    name = random_lower_string()
    content = random_lower_string()
    event_in = EventCreate(name=name, content=content)
    return crud.create_event(session=db, event_in=event_in, owner_id=owner_id)
