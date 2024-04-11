from typing import TypeVar
from random import random, randint

from app.ops.computation import Op, Computation
# Utility classes

B = TypeVar('B')

class Var(Op[tuple[B], B]):
    """A variable op"""
    name: str = "var"

    def call(self, value: B) -> B:
        return value

def var(value: B) -> Computation[B]:
    return Var()(value)


class Const(Op[tuple[()], B]):
    """A constant op"""
    name: str
    value: B

    def __init__(self, value: B):
        super().__init__(name=f"const_{value}", value=value)

    def call(self) -> B:
        return self.value

def cst(value: B) -> Computation[B]:
    return Const(value)()


class Rand(Op[tuple[()], float]):
    name: str = "rand"

    def call(self) -> float:
        return random()

def rnd() -> Computation[float]:
    return Rand()()


class RandInt(Op[tuple[int, int], int]):
    name: str = "randint"

    def call(self, a: int, b: int) -> int:
        return randint(a, b)

def rndi(a: int, b: int) -> Computation[int]:
    return RandInt()(cst(a), cst(b))