import sqlmodel
from app import models
from app.ops.computation import Op

class Session(Op[tuple[()], sqlmodel.Session]):
    """A basic template for ops"""
    async def call(self) -> sqlmodel.Session:
        if "session" in self.context:
            return self.context["session"]
        else:
            return None


class User(Op[sqlmodel.Session, models.User]):
    async def call(self, session: sqlmodel.Session, id: int) -> models.User:
        return session.get(models.User, id)

class Event(Op[sqlmodel.Session, models.Event]):
    async def call(self, session: sqlmodel.Session, id: int) -> models.Event:
        return session.get(models.Event, id)


class EventIdentifier(Op[sqlmodel.Session, models.EventIdentifier]):
    async def call(self, session: sqlmodel.Session, id: str) -> models.EventIdentifier:
        return session.get(models.EventIdentifier, id)