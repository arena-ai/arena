from typing import Any, Generic, TypeVar, TypeVarTuple, Sequence, Mapping
from abc import ABC, abstractmethod
from collections.abc import Sequence, Mapping
from functools import cached_property
from time import time
from asyncio import TaskGroup, Task
import json
import importlib
import base64
from anyio import run
from pydantic import BaseModel, ConfigDict, Field, computed_field, SerializeAsAny

As = TypeVarTuple('As')
A = TypeVar('A')
B = TypeVar('B')

# A mixin class to add hashability to pydantic models
class Hashable:
    def __eq__(self, other) -> bool:
        if isinstance(other, self.__class__):
            return self.to_immutable(self) == self.to_immutable(other)
        return False
    
    def __hash__(self) -> int:
        return hash(self.to_immutable(self))

    def hash_str(self) -> str:
        return base64.urlsafe_b64encode(hash(self).to_bytes(length=8, byteorder='big', signed=True)).decode('ascii')
    
    @classmethod
    def to_immutable(cls, obj: Any) -> Any:
        if isinstance(obj, BaseModel):
            return (obj.__class__.__name__,) + tuple((key, cls.to_immutable(value)) for key, value in obj)
        elif isinstance(obj, dict):
            return tuple((key, cls.to_immutable(value)) for key, value in obj.items())
        elif isinstance(obj, list | set | tuple):
            return tuple(cls.to_immutable(item) for item in obj)
        elif hasattr(obj, '__dict__'):
            return cls.to_immutable(getattr(obj, '__dict__'))
        else:
            return obj

# A mixin class to add json serializability to pydantic models
class JsonSerializable:
    @classmethod
    def to_dict(cls, obj: Any) -> Any:
        if isinstance(obj, BaseModel):
            return {
                'module': obj.__class__.__module__,
                'type': obj.__class__.__name__,
                'value': {k: cls.to_dict(o) for k,o in obj},
            }
        elif isinstance(obj, dict):
            return {k: cls.to_dict(obj[k]) for k in obj}
        elif isinstance(obj, list | set | tuple):
            return [cls.to_dict(o) for o in obj]
        elif hasattr(obj, '__dict__'):
            return cls.to_dict(getattr(obj, '__dict__'))
        else:
            return obj
    
    @classmethod
    def from_dict(cls, obj: Any) -> Any:
        if isinstance(obj, dict) and 'module' in obj and 'type' in obj:
            module = importlib.import_module(obj['module'])
            obj_cls = getattr(module, obj['type'])
            return obj_cls.model_validate(obj_cls.from_dict(obj['value']))
        elif isinstance(obj, dict):
            return {k: cls.from_dict(obj[k]) for k in obj}
        elif isinstance(obj, list):
            return [cls.from_dict(o) for o in obj]
        else:
            return obj

    def to_json(self) -> str:
        return json.dumps(self.to_dict(self))

    @classmethod
    def from_json(cls, value: str) -> Any:
        return cls.from_dict(json.loads(value))
    
    def __str__(self) -> str:
        return self.to_json()


class Op(Hashable, JsonSerializable, BaseModel, ABC, Generic[*As, B]):
    """Ops are a lazy functions,
    they can be composed together like functions (calling `self.__call__`)
    and evaluated by calling `self.call`."""
    context: dict[str, Any] | None = Field(default=None, exclude=True)

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


class Computation(Hashable, JsonSerializable, BaseModel, Generic[B]):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    """An Op applied to arguments"""
    op: Op
    args: list['Computation']
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
    
    def computation_set(self) -> set['Computation']:
        result = {self}
        for arg in self.args:
            result |= arg.computation_set()
        return result

    def computations(self) -> list['Computation']:
        return sorted(self.computation_set(), key=lambda c: hash(c))
    
    def encoder(self) -> dict['Computation', int]:
        return { c: i for i, c in enumerate(self.computations()) }
    
    def to_json(self) -> str:
        flat_computations = FlatComputations.from_computation(self)
        return json.dumps(self.to_dict(flat_computations))

    @classmethod
    def from_json(cls, value: str) -> Any:
        flat_computations = cls.from_dict(json.loads(value))
        return FlatComputations.to_computation(flat_computations)


class FlatComputation(JsonSerializable, BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    """An Op applied to arguments"""
    index: int
    op: Op
    args: list[int]


class FlatComputations(JsonSerializable, BaseModel):
    flat_computation_list: list[FlatComputation]

    @classmethod
    def from_computation(cls, computation: Computation) -> 'FlatComputations':
        encoder = computation.encoder()
        computations = computation.computations()
        flat_computations = [
            FlatComputation(index=encoder[c], op=c.op, args=[encoder[arg] for arg in c.args])
            for c in computations
            ]
        return FlatComputations(flat_computation_list=flat_computations)
    
    @classmethod
    def to_computation(cls, flat_computations: 'FlatComputations') -> Computation:
        parents = {fc.index for fc in flat_computations.flat_computation_list}
        children = {index for fc in flat_computations.flat_computation_list for index in fc.args}
        maximal_parent = next(iter(parents - children))
        computations = [Computation(op=fc.op, args=[]) for fc in flat_computations.flat_computation_list]
        for fc in flat_computations.flat_computation_list:
            computations[fc.index].args = [computations[index] for index in fc.args]
        return computations[maximal_parent]

