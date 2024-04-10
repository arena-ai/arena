from typing import Type, TypeVar, Generic
from abc import ABC, abstractmethod
from pydantic import BaseModel

A = TypeVar('A')
B = TypeVar('B')
C = TypeVar('C')


class Op(BaseModel, ABC, Generic[A, B]):
    """A vasic template for ops"""
    name: str

    @abstractmethod
    def call(self, input: A) -> B:
        """Execute the op"""
        pass

    def then(self, left: 'Op[B, C]') -> 'Composed[A, C]':
        """Compose with another op"""
        return Composed(left=left, right=self)

OpAB = TypeVar('OpAB', bound=Op)
OpBC = TypeVar('OpBC', bound=Op)


class Composed(Op[A, C]):
    """An op composed of 2 other ops"""
    name: str = "composed"
    left: OpBC
    right: OpAB

    def call(self, input: A) -> C:
        return self.left.call(self.right.call(input))

