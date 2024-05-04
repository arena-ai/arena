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
    async def call(self, session: sqlmodel.Session, id: int) -> am.User | None:
        # Create defensive copy to prevent unexpected mutations
        result = session.get(am.User, id)
        if result:
            return result.model_copy()
        else:
            return result

user = User()


class Event(Op[sqlmodel.Session, am.Event]):
    async def call(self, session: sqlmodel.Session, id: int) -> am.Event | None:
        # Create defensive copy to prevent unexpected mutations
        result = session.get(am.Event, id)
        if result:
            return result.model_copy()
        else:
            return result

event = Event()

class EventIdentifier(Op[sqlmodel.Session, am.EventIdentifier]):
    async def call(self, session: sqlmodel.Session, id: str) -> am.EventIdentifier | None:
        # Create defensive copy to prevent unexpected mutations
        result = session.get(am.EventIdentifier, id)
        if result:
            return result.model_copy()
        else:
            return result

event_identifier = EventIdentifier()