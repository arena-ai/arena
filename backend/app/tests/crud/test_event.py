from fastapi.encoders import jsonable_encoder
from sqlmodel import Session

from app import crud
from app.models import UserCreate, Event, EventCreate, Attribute, EventAttribute, EventAttributeCreate
from app.tests.utils.utils import random_email, random_lower_string

def test_create_event(db: Session) -> None:
    user = crud.create_user(session=db, user_create=UserCreate(email=random_email(), password=random_lower_string()))
    event = crud.create_event(session=db, event_in=EventCreate(name="test_request", content=random_lower_string()), owner_id=user.id)
    assert event.owner.id == user.id
    assert len(user.events) == 1

def test_create_attribute(db: Session) -> None:
    attribute = crud.create_attribute_if_not_exist(session=db, attribute_in="test")
    assert attribute.name == "test"
    assert hasattr(attribute, "id")

def test_create_event_attribute(db: Session) -> None:
    user = crud.create_user(session=db, user_create=UserCreate(email=random_email(), password=random_lower_string()))
    event = crud.create_event(session=db, event_in=EventCreate(name="test_request", content=random_lower_string()), owner_id=user.id)
    attribute = crud.create_attribute_if_not_exist(session=db, attribute_in="test")
    event_attribute_db = crud.create_event_attribute(session=db, event_attribute_in=EventAttributeCreate(event_id=event.id, attribute_id=attribute.id, value="hello"))
    db.delete(event_attribute_db)
    db.commit()
    db.refresh(event_attribute_db)
    db.delete(event)
    db.commit()
    db.refresh(event)
    # crud.create_event_attribute_from_name_value(session=db, attribute_in="test", value_in="hello", event=event)
    # crud.create_event_attribute_from_name_value(session=db, attribute_in="test2", value_in="world", event=event)
    # assert len(event.attributes) == 2
    # assert event.attributes[0].value == "hello" 

