from typing import TypeVar
from random import random, randint

from app.ops.computation import Op, Computation
# Utility classes

B = TypeVar('B')

class Const(Op[tuple[()], B]):
    name: str
    value: B

    def __init__(self, value: B):
        super().__init__(name=f"const_{value}", value=value)

    def call(self) -> B:
        return self.value


class Rand(Op[tuple[()], float]):
    name: str = "rand"

    def call(self) -> float:
        return random()


class RandInt(Op[tuple[int, int], int]):
    name: str = "randint"

    def call(self, a: int, b: int) -> int:
        return randint(a, b)