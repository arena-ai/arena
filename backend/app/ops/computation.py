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
    context: dict[str, Any] | None = Field(default=None, exclude=True)
    
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
    computed: B | None = Field(None, exclude=True)
    
    def clear(self):
        """Clear the values
        Clears only if value is set
        The following invariant MUST holds:
        If a value is set, all its parents are
        """
        if self.task or self.computed or self.op.context:
            for arg in self.args:
                arg.clear()
            self.task = None
            self.computed = None
            self.op.context = None
    
    def context(self, **context: Any):
        """Set the context in each op
        """
        if not self.op.context:
            for arg in self.args:
                arg.context(**context)
            self.op.context = context

    async def compute(self) -> B:
        """Compute the value if not already done
        """
        if not self.computed: # Todo ERROR we can call this many times
            args = [await arg.compute() for arg in self.args]
            self.computed = await self.op.call(*args)
        return self.computed

    def tasks(self, task_group: TaskGroup):
        """Create all tasks
        """
        if not self.task:
            for arg in self.args:
                arg.tasks(task_group)
            self.task = task_group.create_task(self.compute())
            from rich import print
            print(f"\nDEBUG no self.task {self.op.opname} {self.task}")
        else:
            from rich import print
            print(f"\nDEBUG self.task {self.op.opname} {self.task}")
    
    async def evaluate(self, **context: Any) -> B:
        """Execute the ops and clear all"""
        self.context(**context)
        async with TaskGroup() as task_group:
            self.tasks(task_group)
            from rich import print
            print(f"\nDEBUG task_group {task_group}")
            print(f"\nDEBUG task_group._tasks {task_group._tasks}")
        computed = self.computed
        self.clear()
        return computed
    
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

