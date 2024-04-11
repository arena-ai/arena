from app.ops.computation import Op, Computation
from app.models import Event, EventCreate, User
from sqlmodel import Session

class SessionOp(Op[tuple[Session], Session]):
    name: str = "session"

    def call(self, db: Session) -> Session:
        return Session

def session(db: Session) -> Computation[Session]:
    return SessionOp()(db)


class UserOp(Op[tuple[User], User]):
    name: str = "user"

    def call(self, u: User) -> User:
        return User

def user(u: User) -> Computation[User]:
    return UserOp()(u)