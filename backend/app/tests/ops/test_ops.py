from typing import Tuple, Callable

from sqlmodel import Session

from app import crud
from app.models import UserCreate, EventCreate
from app.ops import Op
from app.ops.events import LogEvent, LogRequest, RequestCreate
from app.tests.utils.utils import random_email, random_lower_string


def test_basic_op_def() -> None:
    class Sum(Op[Tuple[float, float], float]):
        name: str = "sum"
        
        def call(self, input: Tuple[float, float]) -> float:
            return input[0]+input[1]

    s = Sum()
    print(f"Sum = {s.model_dump_json()}")
    print(f"Sum 1 2 = {s.call((1,2))}")


def test_closure_op_def() -> None:
    class CallOnX(Op[Callable[[float], float], float]):
        name: str = "call_on_x"
        x: float
        
        def call(self, input: Callable[[float], float]) -> float:
            return input(self.x)

    s = CallOnX(x=10)
    print(f"CallOnX = {s.model_dump_json()}")
    print(f"CallOnX lambda x: 2*x= {s.call(lambda x: 2*x)}")


def test_composition() -> None:
    class PlusX(Op[float, float]):
        name: str = "plus_x"
        x: float
        
        def call(self, input: float) -> float:
            return input + self.x
    
    class TimesX(Op[float, float]):
        name: str = "times_x"
        x: float
        
        def call(self, input: float) -> float:
            return input * self.x

    s = PlusX(x=10).then(TimesX(x=2).then(PlusX(x=2))).then(PlusX(x=3))
    print(f"Comp = {s.model_dump()}")
    print(f"Comp 5 {s.call(5)}")


def test_log_requests(db: Session) -> None:
    user = crud.create_user(session=db, user_create=UserCreate(email=random_email(), password=random_lower_string()))
    log_request = LogRequest(name="log_parent_request").then(LogRequest(name="log_request_again"))
    (_,_,events,_) = log_request.call((db, user, [], RequestCreate(
        method="POST", url="http://localhost", headers={}, content='{}'
        )))
    assert len(events) == 2
    print(f"events {events}")