from typing import Optional
from datetime import datetime
from sqlmodel import Field, Relationship, SQLModel, func

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
    # events: list["Event"] = Relationship(back_populates="owner")


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


# Shared properties
class EventBase(SQLModel):
    name: str
    content: str
    parent_id: int | None


# Properties to receive on event creation
class EventCreate(EventBase):
    name: str
    content: str
    parent_id: int | None


# Properties to receive on item update
class EventUpdate(EventBase):
    name: str | None
    content: str | None
    parent_id: int | None


# Database model, database table inferred from class name
class Event(EventBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    timestamp: datetime =  Field(default=func.now())
    owner_id: int | None = Field(default=None, foreign_key="user.id", nullable=False)
    parent_id: int | None = Field(index=True, foreign_key="event.id")
    owner: User | None = Relationship(back_populates="events")
    parent: Optional["Event"] = Relationship(back_populates="children")
    children: list["Event"] = Relationship(back_populates="parent")


# Properties to return via API, id is always required
class EventOut(EventBase):
    id: int
    timestamp: datetime
    owner_id: int


class EventsOut(SQLModel):
    data: list[EventOut]
    count: int