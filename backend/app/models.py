from typing import Optional, Literal,Any
from datetime import datetime
from sqlmodel import Field, Relationship, UniqueConstraint, SQLModel, func, Column, Integer, ForeignKey
from pydantic import BaseModel

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
    settings: list["Setting"] = Relationship(back_populates="owner", sa_relationship_kwargs={"cascade": "all, delete"})
    events: list["Event"] = Relationship(back_populates="owner", sa_relationship_kwargs={"cascade": "all, delete"})
    document_data_extractors: list["DocumentDataExtractor"] = Relationship(back_populates="owner", sa_relationship_kwargs={"cascade": "all, delete"})


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
    name: Literal[
        "OPENAI_API_KEY",
        "MISTRAL_API_KEY",
        "ANTHROPIC_API_KEY",
        "LM_CONFIG",
    ]
    content: str


# Database model, database table inferred from class name
class Setting(SettingBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    timestamp: datetime | None =  Field(default=func.now())
    owner_id: int | None = Field(default=None, foreign_key="user.id")
    owner: User | None = Relationship(back_populates="settings")


# Properties to return via API, id is always required
class SettingOut(SettingBase):
    id: int
    timestamp: datetime
    owner_id: int


class SettingsOut(SQLModel):
    data: list[SettingOut]
    count: int


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
    owner_id: int | None = Field(sa_column=Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), default=None))
    parent_id: int | None = Field(sa_column=Column(Integer, ForeignKey("event.id", ondelete="CASCADE"), index=True))
    owner: User | None = Relationship(back_populates="events")
    parent: Optional["Event"] = Relationship(back_populates="children", sa_relationship_kwargs={"remote_side": lambda: Event.id})
    children: list["Event"] = Relationship(back_populates="parent", sa_relationship_kwargs={"cascade": "all, delete"})
    identifiers: list["EventIdentifier"] = Relationship(back_populates="event", sa_relationship_kwargs={"cascade": "all, delete"})
    attributes: list["EventAttribute"] = Relationship(back_populates="event", sa_relationship_kwargs={"cascade": "all, delete"})

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
    event_id: int | None = Field(sa_column=Column(Integer, ForeignKey("event.id", ondelete="CASCADE"), default=None))
    event: Event = Relationship(back_populates="identifiers")

class EventIdentifierOut(SQLModel):
    id: str
    event_id: int


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
    event_id: int | None = Field(sa_column=Column(Integer, ForeignKey("event.id", ondelete="CASCADE"), default=None))
    attribute_id: int | None = Field(sa_column=Column(Integer, ForeignKey("attribute.id", ondelete="CASCADE"), default=None))
    value: str | None = Field(default=None)
    event: Event = Relationship(back_populates="attributes")
    attribute: "Attribute" = Relationship(back_populates="events")

# Database model, database table inferred from class name
class Attribute(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    events: EventAttribute = Relationship(back_populates="attribute", sa_relationship_kwargs={"cascade": "all, delete"})


# DocumentDataExtractor

# Shared properties
class DocumentDataExtractorBase(SQLModel):
    name: str = Field(unique=True, index=True)
    prompt: str

class DocumentDataExtractorCreate(DocumentDataExtractorBase):
    name: str
    prompt: str
    response_template:dict[str,tuple[Literal['str','int','bool','float'],Literal['required','optional']]]


# Properties to receive on DocumentDataExtractor update
class DocumentDataExtractorUpdate(DocumentDataExtractorBase):
    name: str | None = None
    prompt: str | None = None
    response_template: dict[str,tuple[Literal['str','int','bool','float'],Literal['required','optional']]] | None = None


class DocumentDataExtractor(DocumentDataExtractorBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    timestamp: datetime | None =  Field(default=func.now())
    owner_id: int | None = Field(sa_column=Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), default=None))
    owner: User | None = Relationship(back_populates="document_data_extractors")
    response_template: str
    document_data_examples: list["DocumentDataExample"] = Relationship(back_populates="document_data_extractor", sa_relationship_kwargs={"cascade": "all, delete"})


# Properties to return via API, id is always required
class DocumentDataExtractorOut(DocumentDataExtractorBase):
    id: int
    timestamp: datetime
    owner_id: int
    document_data_examples: list["DocumentDataExample"]
    response_template:str

class DocumentDataExtractorsOut(SQLModel):
    data: list[DocumentDataExtractorOut]
    count: int


# Examples
class DocumentDataExampleBase(SQLModel):
    document_id: str
    data: dict[str,str]
    document_data_extractor_id: int | None = None

class DocumentDataExampleCreate(DocumentDataExampleBase):
    document_id: str
    data: dict[str,str]
    start_page: int = 0
    end_page: int | None = None

class DocumentDataExampleUpdate(DocumentDataExampleBase):
    document_id: str | None = None
    data: dict[str,str] | None = None
    start_page: int | None = None
    end_page: int | None = None

class DocumentDataExample(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    document_id: str
    data: str
    document_data_extractor_id: int = Field(sa_column=Column(Integer, ForeignKey("documentdataextractor.id", ondelete="CASCADE")))
    document_data_extractor: DocumentDataExtractor | None = Relationship(back_populates="document_data_examples")
    start_page: int = 0
    end_page: int | None = None

class DocumentDataExampleOut(DocumentDataExampleBase):
    id: int
    data: str
    