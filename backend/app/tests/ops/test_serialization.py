from app.ops.computation import Op
from app.ops.utils import cst, rndi


def test_ab():
    class Diff(Op[tuple[float, float], float]):
        async def call(self, a: float, b: float) -> float:
            return a - b

    d = Diff()
    r = rndi(0, 20)
    c = cst(5.5)
    e = d(r, c)
    f = d(e, r)
    g = f.model_dump_json()
    print(g)
