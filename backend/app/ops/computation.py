from typing import Generic, TypeVar, TypeVarTuple, Sequence, ClassVar
from abc import ABC, abstractmethod
from functools import cached_property
from dataclasses import dataclass
from asyncio import TaskGroup, Task
from anyio import run
from pydantic import BaseModel, ConfigDict, Field

As = TypeVarTuple('As')
B = TypeVar('B')

class Op(BaseModel, ABC, Generic[*As, B]):
    """A basic template for ops"""
    name: str

    @abstractmethod
    async def call(self, *args: *As) -> B:
        """Execute the op"""
        pass

    def __call__(self, *args: 'Computation') -> 'Computation[B]':
        return Computation(op=self, args=args)


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

