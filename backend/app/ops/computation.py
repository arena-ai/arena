from typing import Generic, TypeVar, TypeVarTuple, Sequence
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pydantic import BaseModel, ConfigDict

As = TypeVarTuple('As')
B = TypeVar('B')

class Op(BaseModel, ABC, Generic[*As, B]):
    """A basic template for ops"""
    name: str

    @abstractmethod
    def call(self, *args: *As) -> B:
        """Execute the op"""
        pass

    def __call__(self, *args: 'Computation') -> 'Computation[B]':
        print(f"self = {self} ({type(self)})")
        print(f"args = {args} ({type(args)})")
        return Computation(op=self, args=args, value=None)


class Computation(BaseModel, Generic[B]):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    """An Op applied to arguments"""
    op: Op
    args: Sequence['Computation']
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
        """Execute the ops and clear all"""
        self._evaluate()
        value = self.value
        self._clear()
        return value

