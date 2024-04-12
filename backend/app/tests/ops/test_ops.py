from typing import Callable

from sqlmodel import Session, select

from app import crud
from app.models import UserCreate, Event
from app.ops import Op, Var, var, Const, cst, Rand, rnd, rndi
from app.ops.events import LogRequest, Request
from app.ops.session import session, user
from app.tests.utils.utils import random_email, random_lower_string

def test_const_op() -> None:
    c = Const(4)
    d = Const("hello")
    print(f"c = {c.model_dump_json()}")
    print(f"d.call() = {d.call()}")
    print(f"d() = {d()}")

def test_basic_op_def() -> None:
    class Sum(Op[tuple[float, float], float]):
        name: str = "sum"
        
        def call(self, a: float, b: float) -> float:
            return a+b

    s = Sum()
    print(f"Sum = {s.model_dump_json()}")
    print(f"Call Sum 1 2 = {s.call(1,2)}")
    s12 = s(cst(1), cst(2))
    print(f"Sum 1 2 = {s12}")
    s12._evaluate()
    print(f"Sum 1 2 = {s12}")
    s12._clear()
    print(f"Sum 1 2 = {s12}")
    print(f"Sum 1 2 = {s12.evaluate()} {s12}")


def test_random() -> None:
    class Sum(Op[tuple[float, float], float]):
        name: str = "sum"
        
        def call(self, a: float, b: float) -> float:
            return a+b
    
    s = Sum()
    a = cst(20)
    r = rnd()
    b = s(r, a)
    c = s(a, b)
    d = s(c, r)
    print(f"d = {d}")
    d._evaluate()
    print(f"d = {d}")
    print(f"d = {d.evaluate()}")
    print(f"d = {d.evaluate()}")


def test_randint() -> None:
    class Diff(Op[tuple[float, float], float]):
        name: str = "diff"
        
        def call(self, a: float, b: float) -> float:
            return a-b
    
    d = Diff()
    r = rndi(0, 20)
    c = cst(5.5)
    e = d(r, c)
    f = d(e, r)
    print(f"e = {e}")
    e._evaluate()
    print(f"e = {e}")
    print(f"e = {e.evaluate()}")
    print(f"e = {e.evaluate()}")
    print(f"f = {f}")
    f._evaluate()
    print(f"f = {f}")
    print(f"f = {f.evaluate()}")
    print(f"f = {f.evaluate()}")


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
    print(f"event.evaluate() {event.evaluate()}")
    events = db.exec(select(Event)).all()
    print(f"events {[e.model_dump_json() for e in events]}")
    assert(len(events)==2)
    