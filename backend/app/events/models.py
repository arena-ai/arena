from datetime import datetime
from sqlmodel import Field, Relationship, SQLModel, func
from app.models import User


# Shared properties
class Event(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    timestamp: datetime =  Field(default=func.now())
    content: str
    owner_id: int = Field(index=True, foreign_key="user.id")
    parent_id: int | None = Field(index=True, foreign_key="event.id")


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


# Properties to receive on event update
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
    parent: Event | None = Relationship(back_populates="events")


# Properties to return via API, id is always required
class EventOut(EventBase):
    id: int
    timestamp: datetime
    owner_id: int


class EventsOut(SQLModel):
    data: list[EventOut]
    count: int