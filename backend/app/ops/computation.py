from typing import Any, Generic, TypeVar, TypeVarTuple, Sequence
from abc import ABC, abstractmethod
from dataclasses import dataclass
from asyncio import TaskGroup, Task
from anyio import run
from pydantic import BaseModel, ConfigDict, Field, computed_field, SerializeAsAny


As = TypeVarTuple('As')
A = TypeVar('A')
B = TypeVar('B')

class Op(BaseModel, ABC, Generic[*As, B]):
    """A basic template for ops"""
    
    @computed_field
    @property
    def opname(self) -> str:
        return self.__class__.__name__

    @abstractmethod
    async def call(self, *args: *As) -> B:
        """Execute the op"""
        pass

    def __call__(self, *args: Any) -> 'Computation[B]':
        """Compose Ops into Computations"""
        return Computation(op=self, args=[Computation.from_any(arg) for arg in args])


class Const(Op[tuple[()], B], Generic[B]):
    """A constant op"""
    value: B

    async def call(self) -> B:
        return self.value


class Getattr(Op[A, B], Generic[A, B]):
    """A getattr op"""
    attr: str

    async def call(self, a: A) -> B:
        return a.__getattribute__(self.attr)


class Getitem(Op[*As, B], Generic[*As, B]):
    """A getitem op"""
    index: int

    async def call(self, a: A) -> B:
        return a.__getitem__(self.index)


class Call(Op[*As, B], Generic[*As, B]):
    """A call op"""
    args: tuple

    async def call(self, a: A) -> B:
        return a.__call__(*self.args)


class Then(Op[tuple[A, B], B], Generic[A, B]):
    """A then op"""
    async def call(self, a: A, b: B) -> B:
        return b


class Computation(BaseModel, Generic[B]):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    """An Op applied to arguments"""
    op: SerializeAsAny[Op]
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

    def then(self, other: 'Computation') -> 'Computation':
        return Then()(self, other)
    
    @classmethod
    def from_any(cls, arg: Any) -> 'Computation':
        if isinstance(arg, Computation):
            return arg
        else:
            return Const(value=arg)()

