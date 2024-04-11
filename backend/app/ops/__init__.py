from typing import Generic, TypeVar, TypeVarTuple, Sequence, Any
from abc import ABC, abstractmethod
from functools import cached_property
from random import random
from pydantic import BaseModel, computed_field

As = TypeVarTuple('As')
B = TypeVar('B')

class Op(BaseModel, ABC, Generic[*As, B]):
    """A basic template for ops"""
    name: str

    @abstractmethod
    def call(self, *args: *As) -> B:
        """Execute the op"""
        pass

    def __call__(self, *args: 'Node[Any]') -> 'Node[B]':
        print(f"self = {self} ({type(self)})")
        print(f"args = {args} ({type(args)})")
        return Node(op=self, args=args, value=None)


class Node(BaseModel, Generic[B]):
    """An Op applied to arguments"""
    op: Op
    args: Sequence['Node']
    value: B | None = None
    
    def _clear(self):
        """Clear the values
        Clears only if value is set
        The following invariant MUST holds:
        If a value is set, all its parents are
        """
        if self.value is not None:
            for arg in self.args:
                arg._clear()
            self.value = None

    def _evaluate(self):
        """Execute the ops"""
        if self.value is None:
            for arg in self.args:
                arg._evaluate()
            self.value = self.op.call(*[arg.value for arg in self.args])
    
    def evaluate(self) -> B:
        """Execute the ops"""
        self._evaluate()
        value = self.value
        self._clear()
        return value


# Utility classes

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

# OpAB = TypeVar('OpAB', bound=Op)
# OpBC = TypeVar('OpBC', bound=Op)

# class Composed(Op[A, C]):
#     """An op composed of 2 other ops"""
#     name: str = "composed"
#     left: OpBC
#     right: OpAB

#     def call(self, input: A) -> C:
#         return self.left.call(self.right.call(input))

