from sqlmodel import Session

from app import crud
from app.models import UserCreate, Event, EventCreate, Attribute, EventAttribute, EventAttributeCreate
from app.tests.utils.utils import random_email, random_lower_string

def test_create_event(db: Session) -> None:
    user = crud.create_user(session=db, user_create=UserCreate(email=random_email(), password=random_lower_string()))
    event = crud.create_event(session=db, event_in=EventCreate(name="test_request", content=random_lower_string()), owner_id=user.id)
    assert event.owner.id == user.id
    assert len(user.events) == 1

def test_create_event_identifier(db: Session) -> None:
    user = crud.create_user(session=db, user_create=UserCreate(email=random_email(), password=random_lower_string()))
    event = crud.create_event(session=db, event_in=EventCreate(name="test_request_id", content=random_lower_string()), owner_id=user.id)
    identifier_1 = crud.create_event_identifier(session=db, event_identifier="test-1234", event_id=event.id)
    identifier_2 = crud.create_event_identifier(session=db, event_identifier="other-1234", event_id=event.id)
    assert len(event.identifiers) == 2
    assert identifier_1.event.name == "test_request_id"
    assert identifier_2.event.name == "test_request_id"
    assert identifier_2.id == "other-1234"

def test_create_attribute(db: Session) -> None:
    attribute = crud.create_attribute_if_not_exist(session=db, attribute="test")
    assert attribute.name == "test"
    assert hasattr(attribute, "id")

def test_create_event_attribute(db: Session) -> None:
    user = crud.create_user(session=db, user_create=UserCreate(email=random_email(), password=random_lower_string()))
    event = crud.create_event(session=db, event_in=EventCreate(name="test_request", content=random_lower_string()), owner_id=user.id)
    crud.create_event_attribute_from_name_value(session=db, attribute="test", value="hello", event_id=event.id)
    crud.create_event_attribute_from_name_value(session=db, attribute="test2", value="world", event_id=event.id)
    assert len(event.attributes) == 2
    assert event.attributes[0].value == "hello"
