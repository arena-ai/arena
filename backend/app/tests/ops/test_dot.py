from app.ops.dot import dot
from app.ops.computation import Op
from app.ops.utils import cst, rndi


def test_basic() -> None:
    class Diff(Op[tuple[float, float], float]):
        async def call(self, a: float, b: float) -> float:
            return a - b

    d = Diff()
    r = rndi(0, 20)
    c = cst(5.5)
    e = d(r, c)
    f = d(e, r)
    print(dot(f).to_string())
