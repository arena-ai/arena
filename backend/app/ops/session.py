from typing import Callable, TypeVar
from sqlmodel import Session
from app.core.db import engine
from app.api.deps import get_db
from app.ops.computation import Op, Computation

B = TypeVar('B')

class WithSession(Op[Callable[[Session], B], B]):
    """A basic template for ops"""
    async def call(self, require_session: Callable[[Session], B]) -> B:
        """Execute the op"""
        with Session(engine) as session:
            result = require_session(session)
        return result
