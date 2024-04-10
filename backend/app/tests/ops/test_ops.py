from typing import Tuple, Callable
from app.ops import Op


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