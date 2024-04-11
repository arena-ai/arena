from app.ops import Op, Computation, Var
from app.models import Event, EventCreate, User
from sqlmodel import Session

def session(db: Session) -> Computation[Session]:
    return Var("session")(db)

def user(u: User) -> Computation[User]:
    return Var("user")(u)
