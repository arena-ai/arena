from typing import Callable

from sqlmodel import Session

from app import crud
from app.models import UserCreate, EventCreate
from app.ops import Op, Const, Rand, RandInt
from app.ops.events import LogRequest, RequestCreate
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
    s12 = s(Const(1)(), Const(2)())
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
    a = Const(20)()
    r = Rand()()
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
    a = Const(0)()
    b = Const(20)()
    r = RandInt()(a, b)
    c = Const(5.5)()
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


# def test_closure_op_def() -> None:
#     class CallOnX(Op[Callable[[float], float], float]):
#         name: str = "call_on_x"
#         x: float
        
#         def call(self, input: Callable[[float], float]) -> float:
#             return input(self.x)

#     s = CallOnX(x=10)
#     print(f"CallOnX = {s.model_dump_json()}")
#     print(f"CallOnX lambda x: 2*x= {s.call(lambda x: 2*x)}")


# def test_composition() -> None:
#     class PlusX(Op[float, float]):
#         name: str = "plus_x"
#         x: float
        
#         def call(self, input: float) -> float:
#             return input + self.x
    
#     class TimesX(Op[float, float]):
#         name: str = "times_x"
#         x: float
        
#         def call(self, input: float) -> float:
#             return input * self.x

#     s = PlusX(x=10).then(TimesX(x=2).then(PlusX(x=2))).then(PlusX(x=3))
#     print(f"Comp = {s.model_dump()}")
#     print(f"Comp 5 {s.call(5)}")


# def test_log_requests(db: Session) -> None:
#     user = crud.create_user(session=db, user_create=UserCreate(email=random_email(), password=random_lower_string()))
#     log_request = LogRequest(name="log_parent_request").then(LogRequest(name="log_request_again"))
#     (_,_,events,_) = log_request.call((db, user, [], RequestCreate(
#         method="POST", url="http://localhost", headers={}, content='{}'
#         )))
#     assert len(events) == 2
#     print(f"events {events}")