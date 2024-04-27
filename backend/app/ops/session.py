from sqlmodel import Session
from app.api.deps import get_db
from app.ops.computation import Op, Computation


class GetDB(Op[tuple[()], Session]):
    """A basic template for ops"""
    async def call(self) -> Session:
        """Execute the op"""
        return next(get_db())

def get_db() -> Computation[Session]:
    return GetDB()()