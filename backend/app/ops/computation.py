from typing import Any, Generic, TypeVar, TypeVarTuple, Sequence
from abc import ABC, abstractmethod
from dataclasses import dataclass
from asyncio import TaskGroup, Task
from anyio import run
from pydantic import BaseModel, ConfigDict, Field


As = TypeVarTuple('As')
A = TypeVar('A')
B = TypeVar('B')

class Op(BaseModel, ABC, Generic[*As, B]):
    """A basic template for ops"""
    name: str

    @abstractmethod
    async def call(self, *args: *As) -> B:
        """Execute the op"""
        pass

    def __call__(self, *args: Any) -> 'Computation[B]':
        """Compose Ops into Computations"""
        return Computation(op=self, args=[Computation.from_any(arg) for arg in args])


class Const(Op[tuple[()], B], Generic[B]):
    """A constant op"""
    name: str
    value: B

    def __init__(self, value: B):
        super().__init__(name=f"const_{value}", value=value)

    async def call(self) -> B:
        return self.value


class Getattr(Op[A, B], Generic[A, B]):
    """A getattr op"""
    name: str = "getattr"
    attr: str

    async def call(self, a: A) -> B:
        return a.__getattribute__(self.attr)


class Getitem(Op[*As, B], Generic[*As, B]):
    """A getitem op"""
    name: str = "getitem"
    index: int

    async def call(self, a: A) -> B:
        return a.__getitem__(self.index)


class Call(Op[*As, B], Generic[*As, B]):
    """A call op"""
    name: str = "call"
    args: tuple

    async def call(self, a: A) -> B:
        return a.__call__(*self.args)


class Computation(BaseModel, Generic[B]):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    """An Op applied to arguments"""
    op: Op
    args: Sequence['Computation']
    task: Task | None = Field(None, exclude=True)
    
    def _clear(self):
        """Clear the values
        Clears only if value is set
        The following invariant MUST holds:
        If a value is set, all its parents are
        """
        if self.task is not None:
            for arg in self.args:
                arg._clear()
            self.task = None

    async def _call(self):
        args = [await arg.task for arg in self.args]
        return await self.op.call(*args)

    async def _evaluate(self, task_group: TaskGroup):
        """Execute the ops"""
        if self.task is None:
            for arg in self.args:
                await arg._evaluate(task_group)
            self.task = task_group.create_task(self._call())
    
    async def evaluate(self) -> B:
        """Execute the ops and clear all"""
        async with TaskGroup() as task_group:
            await self._evaluate(task_group)
            value = await self.task
        self._clear()
        return value
    
    def __getattr__(self, name: str) -> 'Computation':
        return Getattr(attr=name)(self)
    
    def __getitem__(self, name: str) -> 'Computation':
        return Getitem(index=name)(self)

    def __call__(self, *args) -> 'Computation':
        return Call(args=args)(self)
    
    @classmethod
    def from_any(cls, arg: Any) -> 'Computation':
        if isinstance(arg, Computation):
            return arg
        else:
            return Const(arg)()


class Tup(Op[*As, tuple[*As]], Generic[*As]):
    """A tuple op"""
    name: str = "tup"

    async def call(self, *tup: *As) -> tuple[*As]:
        return tup

def tup(*tup: Computation) -> Computation[tuple[*As]]:
    return Tup()(*tup)