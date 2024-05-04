import sqlmodel
import app.models as am
from app.ops.computation import Op

class Session(Op[tuple[()], sqlmodel.Session]):
    """A basic template for ops"""
    async def call(self) -> sqlmodel.Session:
        if "session" in self.context:
            return self.context["session"]
        else:
            return None

session = Session()

class User(Op[sqlmodel.Session, am.User]):
    async def call(self, session: sqlmodel.Session, id: int) -> am.User:
        # Create defensive copy to prevent unexpected mutations
        return session.get(am.User, id).model_copy()

user = User()


class Event(Op[sqlmodel.Session, am.Event]):
    async def call(self, session: sqlmodel.Session, id: int) -> am.Event:
        # Create defensive copy to prevent unexpected mutations
        return session.get(am.Event, id).model_copy()

event = Event()

class EventIdentifier(Op[sqlmodel.Session, am.EventIdentifier]):
    async def call(self, session: sqlmodel.Session, id: str) -> am.EventIdentifier:
        # Create defensive copy to prevent unexpected mutations
        return session.get(am.EventIdentifier, id).model_copy()

event_identifier = EventIdentifier()