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
    id: int

    """A basic template for ops"""
    async def call(self, session: sqlmodel.Session) -> models.User:
        return session.get(models.User, self.id)