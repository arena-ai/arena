from anyio import run
from sqlmodel import Session, select
from pydantic import BaseModel
from rich import print

from app import crud
from app.models import UserCreate, Event
from app.ops.events import LogRequest, Request, LogResponse, Response
from app.ops.session import session as session_op, user as user_op
from app.ops import tup
from app.tests.utils.utils import random_email, random_lower_string


class Text(BaseModel):
    text: str


def test_log_requests(db: Session) -> None:
    ses = session_op()
    user = crud.create_user(session=db, user_create=UserCreate(email=random_email(), password=random_lower_string()))
    usr = user_op(ses, user.id)
    req = Request(method="POST", url="http://localhost", headers={"x-name": "first"}, content=Text(text="hello"))
    event = LogRequest()(ses, usr, None, req)
    req = Request(method="POST", url="http://localhost", headers={"x-name": "second"}, content=Text(text="world"))
    event = LogRequest()(ses, usr, event, req)
    print(f"event {event}")
    events = db.exec(select(Event).where(Event.name=='request')).all()
    print(f"events {[e.model_dump_json() for e in events]}")
    assert(len(events)==0)
    async def event_eval():
        return await event.evaluate(session=db)
    res = run(event_eval)
    print(f"event.evaluate() {res}")
    events = db.exec(select(Event).where(Event.name=='request')).all()
    print(f"events {[e.model_dump_json() for e in events]}")
    assert(len(events)==2)
    # Cleanup
    for event in events:
        db.delete(event)
    db.commit()


def test_log_responses(db: Session) -> None:
    ses = session_op()
    user = crud.create_user(session=db, user_create=UserCreate(email=random_email(), password=random_lower_string()))
    usr = user_op(ses, user.id)
    resp = Response(status_code=200, headers={"x-name": "first"}, content=Text(text="hello"))
    event = LogResponse()(ses, usr, None, resp)
    resp = Response(status_code=404, headers={"x-name": "first"}, content=Text(text="world"))
    event = LogResponse()(ses, usr, event, resp)
    print(f"event {event}")
    events = db.exec(select(Event).where(Event.name=='response')).all()
    print(f"events {[e.model_dump_json() for e in events]}")
    assert(len(events)==0)
    async def event_eval():
        return await event.evaluate(session=db)
    res = run(event_eval)
    print(f"event.evaluate() {res}")
    events = db.exec(select(Event).where(Event.name=='response')).all()
    print(f"events {[e.model_dump_json() for e in events]}")
    assert(len(events)==2)
    # Cleanup
    for event in events:
        db.delete(event)
    db.commit()


def test_log_many_requests(db: Session) -> None:
    ses = session_op()
    user = crud.create_user(session=db, user_create=UserCreate(email=random_email(), password=random_lower_string()))
    usr = user_op(ses, user.id)
    req = Request(method="POST", url="http://localhost", headers={"x-name": "first"}, content=Text(text="hello"))
    log_event = LogRequest()(ses, usr, None, req)
    req = Request(method="POST", url="http://localhost", headers={"x-name": "second"}, content=Text(text="world"))
    log_req = LogRequest()(ses, usr, log_event, req)
    resp = Response(status_code=200, content=Text(text="resp"))
    log_resp = LogResponse()(ses, usr, log_event, resp)
    res = tup(log_event, log_req, log_resp)
    print(f"\nres {res.model_dump(exclude_none=True)}")
    events = db.exec(select(Event)).all()
    assert(len(events)==0)
    async def event_eval():
        return await res.evaluate(session=db)
    res = run(event_eval)
    print(f"\nres eval {res}")
    events = db.exec(select(Event)).all()
    print(f"\nevents {[e.model_dump(exclude_none=True) for e in events]}")
    assert(len(events)==3)
    # Cleanup
    for event in events:
        db.delete(event)
    db.commit()
