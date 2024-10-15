from typing import TypeVar, Generic, Callable, TypeVarTuple, Any
from random import random, randint

from app.ops.computation import Op, Computation, Const
# Utility classes

A = TypeVar("A")
B = TypeVar("B")
As = TypeVarTuple("As")


def cst(value: B) -> Computation[B]:
    return Const(value=value)()


class Var(Op[tuple[B], B], Generic[B]):
    """A variable op"""

    async def call(self, value: B) -> B:
        return value


def var(name: str, value: B) -> Computation[B]:
    return Var(name=name)(cst(value))


class Tup(Op[*As, tuple[*As]], Generic[*As]):
    """A tuple op"""

    async def call(self, *tup: *As) -> tuple[*As]:
        return tup


def tup(*tup: Any) -> Computation[tuple[*As]]:
    return Tup()(*tup)


class Fun(Op[tuple[A], B], Generic[A, B]):
    """A variable op"""

    fun: Callable[[A], B]

    async def call(self, a: A) -> B:
        return self.fun(a)


def fun(f: Callable[[A], B], a: Computation[A]) -> Computation[B]:
    return Fun(f)(a)


class Rand(Op[tuple[()], float]):
    async def call(self) -> float:
        return random()


def rnd() -> Computation[float]:
    return Rand()()


class RandInt(Op[tuple[int, int], int]):
    async def call(self, a: int, b: int) -> int:
        return randint(a, b)


def rndi(a: int, b: int) -> Computation[int]:
    return RandInt()(cst(a), cst(b))
