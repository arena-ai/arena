from typing import Any

from sqlmodel import Session, select, desc

from app.core.security import get_password_hash, verify_password
from app.models import (
    User,
    UserCreate,
    UserUpdate,
    Setting,
    SettingCreate,
    Event,
    EventCreate,
    EventIdentifier,
    EventAttribute,
    EventAttributeCreate,
    Attribute,
    DocumentDataExtractor,
)


def create_user(*, session: Session, user_create: UserCreate) -> User:
    db_obj = User.model_validate(
        user_create,
        update={"hashed_password": get_password_hash(user_create.password)},
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def update_user(
    *, session: Session, db_user: User, user_in: UserUpdate
) -> Any:
    user_data = user_in.model_dump(exclude_unset=True)
    extra_data = {}
    if "password" in user_data:
        password = user_data["password"]
        hashed_password = get_password_hash(password)
        extra_data["hashed_password"] = hashed_password
    db_user.sqlmodel_update(user_data, update=extra_data)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def get_user_by_email(*, session: Session, email: str) -> User | None:
    statement = select(User).where(User.email == email)
    session_user = session.exec(statement).first()
    return session_user


def authenticate(
    *, session: Session, email: str, password: str
) -> User | None:
    db_user = get_user_by_email(session=session, email=email)
    if not db_user:
        return None
    if not verify_password(password, db_user.hashed_password):
        return None
    return db_user


# Settings
def create_setting(
    *, session: Session, setting_in: SettingCreate, owner_id: int
) -> Setting:
    db_setting = Setting.model_validate(
        setting_in, update={"owner_id": owner_id}
    )
    session.add(db_setting)
    session.commit()
    session.refresh(db_setting)
    return db_setting


def get_setting(
    *, session: Session, setting_name: str, owner_id: int
) -> Setting | None:
    statement = (
        select(Setting)
        .where(Setting.owner_id == owner_id)
        .where(Setting.name == setting_name)
        .order_by(desc(Setting.timestamp))
    )
    setting = session.exec(statement).first()
    return setting


# Events
def get_event(*, session: Session, event_id: int) -> Event:
    db_event = session.get(Event, event_id)
    return db_event


def create_event(
    *, session: Session, event_in: EventCreate, owner_id: int
) -> Event:
    db_event = Event.model_validate(event_in, update={"owner_id": owner_id})
    session.add(db_event)
    session.commit()
    session.refresh(db_event)
    return db_event


def delete_event(*, session: Session, event_id: int) -> None:
    db_event = get_event(session=session, event_id=event_id)
    session.delete(db_event)
    session.commit()


# Event Identifier
def get_event_identifier(
    *, session: Session, event_identifier: str
) -> EventIdentifier | None:
    statement = select(EventIdentifier).where(
        EventIdentifier.id == event_identifier
    )
    db_event_identifier = session.exec(statement).first()
    return db_event_identifier


def get_event_identifiers(
    *, session: Session, event_id: int
) -> list[EventIdentifier]:
    statement = select(EventAttribute).join(Event).where(Event.id == event_id)
    db_event_identifiers = session.exec(statement).all()
    return db_event_identifiers


def create_event_identifier(
    *, session: Session, event_identifier: str, event_id: int
) -> EventIdentifier:
    db_event_identifier = EventIdentifier(
        id=event_identifier, event_id=event_id
    )
    session.add(db_event_identifier)
    session.commit()
    session.refresh(db_event_identifier)
    return db_event_identifier


def delete_event_identifier(
    *, session: Session, event_identifier: str
) -> None:
    db_event_identifier = get_event_identifier(
        session=session, event_identifier=event_identifier
    )
    session.delete(db_event_identifier)
    session.commit()


# Attribute
def get_attribute(*, session: Session, attribute: str) -> Attribute | None:
    statement = select(Attribute).where(Attribute.name == attribute)
    db_attribute = session.exec(statement).first()
    return db_attribute


def create_attribute(*, session: Session, attribute: str) -> Attribute:
    db_attribute = Attribute(name=attribute)
    session.add(db_attribute)
    session.commit()
    session.refresh(db_attribute)
    return db_attribute


def create_attribute_if_not_exist(
    *, session: Session, attribute: str
) -> Attribute:
    db_attribute = get_attribute(session=session, attribute=attribute)
    if db_attribute is None:
        db_attribute = create_attribute(session=session, attribute=attribute)
    return db_attribute


def delete_attribute(*, session: Session, attribute: str) -> None:
    db_attribute = get_attribute(session=session, attribute=attribute)
    session.delete(db_attribute)
    session.commit()


# Event Attribute
def get_event_attribute(
    *, session: Session, attribute: str, event_id: int
) -> EventAttribute | None:
    statement = (
        select(EventAttribute)
        .join(Event)
        .join(Attribute)
        .where(Event.id == event_id)
        .where(Attribute.name == attribute)
    )
    db_event_attribute = session.exec(statement).first()
    return db_event_attribute


def get_event_attributes(
    *, session: Session, event_id: int
) -> list[EventAttribute]:
    statement = select(EventAttribute).join(Event).where(Event.id == event_id)
    db_event_attributes = session.exec(statement).all()
    return db_event_attributes


def create_event_attribute(
    *, session: Session, event_attribute_in: EventAttributeCreate
) -> EventAttribute:
    db_event_attribute = EventAttribute.model_validate(event_attribute_in)
    session.add(db_event_attribute)
    session.commit()
    session.refresh(db_event_attribute)
    return db_event_attribute


def create_event_attribute_from_name_value(
    *,
    session: Session,
    attribute: str,
    value: str | None = None,
    event_id: int,
) -> EventAttribute:
    db_attribute = create_attribute_if_not_exist(
        session=session, attribute=attribute
    )
    db_event_attribute = EventAttributeCreate(
        event_id=event_id, attribute_id=db_attribute.id, value=value
    )
    return create_event_attribute(
        session=session, event_attribute_in=db_event_attribute
    )


def delete_event_attribute(
    *, session: Session, attribute: str, event: int
) -> None:
    db_event_attribute = get_attribute(
        session=session, attribute=attribute, event_id=event
    )
    session.delete(db_event_attribute)
    session.commit()


def get_document_data_extractor(
    *, session: Session, name: str
) -> DocumentDataExtractor | None:
    statement = select(DocumentDataExtractor).where(
        DocumentDataExtractor.name == name
    )
    db_document_data_extractor = session.exec(statement).first()
    return db_document_data_extractor
