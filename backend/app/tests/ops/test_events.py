from anyio import run
from sqlmodel import Session, select

from app import crud
from app.models import UserCreate, Event
from app.ops.events import LogRequest, Request
from app.ops.session import session, user
from app.tests.utils.utils import random_email, random_lower_string


def test_log_requests(db: Session) -> None:
    user = crud.create_user(session=db, user_create=UserCreate(email=random_email(), password=random_lower_string()))
    req = Request(method="POST", url="http://localhost", headers={"x-name": "first"}, content="hello")
    event = LogRequest()(var("session", db), var("user", user), var("parent", None), var("request", req))
    req = Request(method="POST", url="http://localhost", headers={"x-name": "second"}, content="world")
    event = LogRequest()(var("session", db), var("user", user), event, var("request", req))
    print(f"event {event}")
    events = db.exec(select(Event)).all()
    print(f"events {[e.model_dump_json() for e in events]}")
    assert(len(events)==0)
    print(f"event.evaluate() {run(event.evaluate)}")
    events = db.exec(select(Event)).all()
    print(f"events {[e.model_dump_json() for e in events]}")
    assert(len(events)==2)
    