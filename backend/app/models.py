from typing import Optional
from datetime import datetime
from sqlmodel import Field, Relationship, UniqueConstraint, SQLModel, func

# Shared properties
# TODO replace email str with EmailStr when sqlmodel supports it
class UserBase(SQLModel):
    email: str = Field(unique=True, index=True)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = None


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str


# TODO replace email str with EmailStr when sqlmodel supports it
class UserCreateOpen(SQLModel):
    email: str
    password: str
    full_name: str | None = None


# Properties to receive via API on update, all are optional
# TODO replace email str with EmailStr when sqlmodel supports it
class UserUpdate(UserBase):
    email: str | None = None  # type: ignore
    password: str | None = None


# TODO replace email str with EmailStr when sqlmodel supports it
class UserUpdateMe(SQLModel):
    full_name: str | None = None
    email: str | None = None


class UpdatePassword(SQLModel):
    current_password: str
    new_password: str


# Database model, database table inferred from class name
class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    hashed_password: str
    settings: list["Setting"] = Relationship(back_populates="owner")
    events: list["Event"] = Relationship(back_populates="owner")


# Properties to return via API, id is always required
class UserOut(UserBase):
    id: int


class UsersOut(SQLModel):
    data: list[UserOut]
    count: int


# Generic message
class Message(SQLModel):
    message: str


# JSON payload containing access token
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(SQLModel):
    sub: int | None = None


class NewPassword(SQLModel):
    token: str
    new_password: str


# Settings

# Shared properties
class SettingBase(SQLModel):
    name: str
    content: str


# Properties to receive on event creation
class SettingCreate(SettingBase):
    name: str
    content: str


# Database model, database table inferred from class name
class Setting(SettingBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    timestamp: datetime | None =  Field(default=func.now())
    owner_id: int | None = Field(default=None, foreign_key="user.id", nullable=False)
    owner: User | None = Relationship(back_populates="settings")


# Properties to return via API, id is always required
class SettingOut(SettingBase):
    id: int
    timestamp: datetime
    owner_id: int


# Events

# Shared properties
class EventBase(SQLModel):
    name: str
    content: str
    parent_id: int | None = None


# Properties to receive on event creation
class EventCreate(EventBase):
    name: str
    content: str

# Properties to receive on item update
class EventUpdate(EventBase):
    name: str | None = None
    content: str | None = None
    parent_id: int | None = None


# Database model, database table inferred from class name
class Event(EventBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    timestamp: datetime | None =  Field(default=func.now())
    owner_id: int | None = Field(default=None, foreign_key="user.id", nullable=False)
    parent_id: int | None = Field(index=True, foreign_key="event.id")
    owner: User | None = Relationship(back_populates="events")
    parent: Optional["Event"] = Relationship(back_populates="children", sa_relationship_kwargs={"remote_side": lambda: Event.id})
    children: list["Event"] = Relationship(back_populates="parent")
    identifiers: list["EventIdentifier"] = Relationship(back_populates="event")
    attributes: list["EventAttribute"] = Relationship(back_populates="event")


# Properties to return via API, id is always required
class EventOut(EventBase):
    id: int
    timestamp: datetime
    owner_id: int


class EventsOut(SQLModel):
    data: list[EventOut]
    count: int


# Database model, database table inferred from class name
class EventIdentifier(SQLModel, table=True):
    id: str | None = Field(default=None, primary_key=True)
    event_id: int | None = Field(default=None, foreign_key="event.id", nullable=False)
    event: Event = Relationship(back_populates="identifiers")


# Shared properties
class EventAttributeBase(SQLModel):
    event_id: int
    attribute_id: int
    value: str | None

# Properties to receive on event creation
class EventAttributeCreate(EventAttributeBase):
    event_id: int
    attribute_id: int
    value: str | None = None

# Database model, database table inferred from class name
class EventAttribute(EventAttributeBase, table=True):
    __table_args__ = (UniqueConstraint("event_id", "attribute_id"), )
    id: int | None = Field(default=None, primary_key=True)
    event_id: int | None = Field(default=None, foreign_key="event.id", nullable=False)
    attribute_id: int | None = Field(default=None, foreign_key="attribute.id", nullable=False)
    value: str | None = Field(default=None)
    event: Event = Relationship(back_populates="attributes")
    attribute: "Attribute" = Relationship(back_populates="event")


# Database model, database table inferred from class name
class Attribute(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    event: EventAttribute = Relationship(back_populates="attribute")
