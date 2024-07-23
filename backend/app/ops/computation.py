from typing import Any, Generic, TypeVar, TypeVarTuple, Sequence
from abc import ABC, abstractmethod
from dataclasses import dataclass
from time import time
from asyncio import TaskGroup, Task
from anyio import run
from pydantic import BaseModel, ConfigDict, Field, computed_field, SerializeAsAny

As = TypeVarTuple('As')
A = TypeVar('A')
B = TypeVar('B')

class Op(BaseModel, ABC, Generic[*As, B]):
    """Ops are a lazy functions,
    they can be composed together like functions (calling `self.__call__`)
    and evaluated by calling `self.call`."""
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
    
    def __str__(self) -> str:
        return self.opname


class Const(Op[tuple[()], B], Generic[B]):
    """A constant op"""
    value: B

    async def call(self) -> B:
        return self.value

    def __str__(self) -> str:
        return f"{self.opname} ({str(self.value) if len(str(self.value)) < 16 else str(self.value)[:16]+'...'})"


class Getattr(Op[A, B], Generic[A, B]):
    """A getattr op"""
    attr: str

    async def call(self, a: A) -> B:
        return a.__getattribute__(self.attr)

    def __str__(self) -> str:
        return f"{self.opname} ({self.attr})"


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
    
    def __str__(self) -> str:
        return f"{self.opname}"


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
    
    def clear(self):
        """Clear the values
        Clears only if value is set
        The following invariant MUST holds:
        If a value is set, all its parents are
        """
        if self.task or self.op.context:
            for arg in self.args:
                arg.clear()
            self.task = None
            self.op.context = None
    
    def contexts(self, **context: Any):
        """Set the context in each op
        """
        if not self.op.context:
            for arg in self.args:
                arg.contexts(**context)
            self.op.context = context

    async def call(self) -> B:
        """Wait for all the args and calls the op.
        All tasks should have been created
        """
        args = [await arg.task for arg in self.args]
        return await self.op.call(*args)

    def tasks(self, task_group: TaskGroup):
        """Create all tasks
        """
        if not self.task:
            for arg in self.args:
                arg.tasks(task_group)
            self.task = task_group.create_task(self.call())
    
    async def evaluate(self, **context: Any) -> B:
        """Execute the ops and clears all"""
        self.contexts(**context)
        try:
            async with TaskGroup() as task_group:
                self.tasks(task_group)
            result = await self.task
        except Exception:
            from app.ops.dot import dot
            name = f"/tmp/dump_{time()}.dot"
            with open(name, "w+") as f:
                f.write(dot(self).to_string())
            raise RuntimeError(f'The computation failed. A dump is written there {name}')
        self.clear()
        return result
    
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

