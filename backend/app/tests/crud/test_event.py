from sqlmodel import Session, select

from app.services import crud
from app.models import UserCreate, EventCreate, User, Event
from app.tests.utils.utils import random_email, random_lower_string


def test_create_event(db: Session) -> None:
    user = crud.create_user(
        session=db,
        user_create=UserCreate(
            email=random_email(), password=random_lower_string()
        ),
    )
    event = crud.create_event(
        session=db,
        event_in=EventCreate(
            name="test_request", content=random_lower_string()
        ),
        owner_id=user.id,
    )
    assert event.owner.id == user.id
    assert len(user.events) == 1
    # Cleanup
    db.delete(user)
    db.delete(event)
    db.commit()


def test_create_event_identifier(db: Session) -> None:
    user = crud.create_user(
        session=db,
        user_create=UserCreate(
            email=random_email(), password=random_lower_string()
        ),
    )
    event = crud.create_event(
        session=db,
        event_in=EventCreate(
            name="test_request_id", content=random_lower_string()
        ),
        owner_id=user.id,
    )
    identifier_1 = crud.create_event_identifier(
        session=db, event_identifier="test-1234", event_id=event.id
    )
    identifier_2 = crud.create_event_identifier(
        session=db, event_identifier="other-1234", event_id=event.id
    )
    assert len(event.identifiers) == 2
    assert identifier_1.event.name == "test_request_id"
    assert identifier_2.event.name == "test_request_id"
    assert identifier_2.id == "other-1234"
    # Cleanup
    db.delete(user)
    db.delete(event)
    db.commit()


def test_create_attribute(db: Session) -> None:
    attribute = crud.create_attribute_if_not_exist(
        session=db, attribute="test"
    )
    assert attribute.name == "test"
    assert hasattr(attribute, "id")


def test_create_event_attribute(db: Session) -> None:
    user = crud.create_user(
        session=db,
        user_create=UserCreate(
            email=random_email(), password=random_lower_string()
        ),
    )
    event = crud.create_event(
        session=db,
        event_in=EventCreate(
            name="test_request", content=random_lower_string()
        ),
        owner_id=user.id,
    )
    crud.create_event_attribute_from_name_value(
        session=db, attribute="test", value="hello", event_id=event.id
    )
    crud.create_event_attribute_from_name_value(
        session=db, attribute="test2", value="world", event_id=event.id
    )
    assert len(event.attributes) == 2
    assert event.attributes[0].value == "hello"
    # Cleanup
    db.delete(user)
    db.delete(event)
    db.commit()


def test_delete_event(db: Session) -> None:
    alice = crud.create_user(
        session=db,
        user_create=UserCreate(
            email=random_email(), password=random_lower_string()
        ),
    )
    bob = crud.create_user(
        session=db,
        user_create=UserCreate(
            email=random_email(), password=random_lower_string()
        ),
    )
    parent_event = crud.create_event(
        session=db,
        event_in=EventCreate(name="parent", content=random_lower_string()),
        owner_id=alice.id,
    )
    _ = [
        crud.create_event(
            session=db,
            event_in=EventCreate(
                name="test_request",
                content=random_lower_string(),
                parent_id=parent_event.id,
            ),
            owner_id=alice.id,
        )
        for _ in range(10)
    ]
    assert len(db.exec(select(User)).all()) == 3  # Superuser, Alice and Bob
    assert len(db.exec(select(Event)).all()) == 11  # parent and children
    db.delete(parent_event)
    db.commit()
    assert len(db.exec(select(User)).all()) == 3  # Should not change
    assert len(db.exec(select(Event)).all()) == 0  # None
    # Cleanup
    db.delete(alice)
    db.delete(bob)
    db.commit()


def test_delete_owner(db: Session) -> None:
    alice = crud.create_user(
        session=db,
        user_create=UserCreate(
            email=random_email(), password=random_lower_string()
        ),
    )
    bob = crud.create_user(
        session=db,
        user_create=UserCreate(
            email=random_email(), password=random_lower_string()
        ),
    )
    parent_event = crud.create_event(
        session=db,
        event_in=EventCreate(name="parent", content=random_lower_string()),
        owner_id=alice.id,
    )
    _ = [
        crud.create_event(
            session=db,
            event_in=EventCreate(
                name="test_request",
                content=random_lower_string(),
                parent_id=parent_event.id,
            ),
            owner_id=alice.id,
        )
        for _ in range(10)
    ]
    assert len(db.exec(select(User)).all()) == 3  # Superuser, Alice and Bob
    assert len(db.exec(select(Event)).all()) == 11  # parent and children
    db.delete(alice)
    db.commit()
    assert len(db.exec(select(User)).all()) == 2  # Should not change
    assert len(db.exec(select(Event)).all()) == 0  # None
    # Cleanup
    db.delete(bob)
    db.delete(parent_event)
    db.commit()
