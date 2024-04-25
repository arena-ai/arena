from anyio import run
from sqlmodel import Session, select

from app import crud
from app.models import UserCreate, Event
from app.ops.utils import var
from app.ops.events import LogRequest, Request, LogResponse, Response
from app.tests.utils.utils import random_email, random_lower_string


def test_log_requests(db: Session) -> None:
    user = crud.create_user(session=db, user_create=UserCreate(email=random_email(), password=random_lower_string()))
    req = Request(method="POST", url="http://localhost", headers={"x-name": "first"}, content="hello")
    event = LogRequest()(db, user, None, req)
    req = Request(method="POST", url="http://localhost", headers={"x-name": "second"}, content="world")
    event = LogRequest()(db, user, event, req)
    print(f"event {event}")
    events = db.exec(select(Event).where(Event.name=='request')).all()
    print(f"events {[e.model_dump_json() for e in events]}")
    assert(len(events)==0)
    print(f"event.evaluate() {run(event.evaluate)}")
    events = db.exec(select(Event).where(Event.name=='request')).all()
    print(f"events {[e.model_dump_json() for e in events]}")
    assert(len(events)==2)


def test_log_responses(db: Session) -> None:
    user = crud.create_user(session=db, user_create=UserCreate(email=random_email(), password=random_lower_string()))
    resp = Response(status_code=200, headers={"x-name": "first"}, content="hello")
    event = LogResponse()(db, user, None, resp)
    resp = Response(status_code=404, headers={"x-name": "first"}, content="world")
    event = LogResponse()(db, user, event, resp)
    print(f"event {event}")
    events = db.exec(select(Event).where(Event.name=='response')).all()
    print(f"events {[e.model_dump_json() for e in events]}")
    assert(len(events)==0)
    print(f"event.evaluate() {run(event.evaluate)}")
    events = db.exec(select(Event).where(Event.name=='response')).all()
    print(f"events {[e.model_dump_json() for e in events]}")
    assert(len(events)==2)