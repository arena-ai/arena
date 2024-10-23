from dataclasses import dataclass

from anyio import run

from app.ops import Op, cst, rnd, rndi, Computation


def test_const_op() -> None:
    c = cst(4).op
    d = cst("hello").op
    print(f"c = {c.model_dump_json()}")
    print(f"d.call() = {run(d.call)}")
    print(f"d() = {d()}")


def test_basic_op_def() -> None:
    class Sum(Op[tuple[float, float], float]):
        name: str = "sum"

        async def call(self, a: float, b: float) -> float:
            return a + b

    s = Sum()
    print(f"Sum = {s.model_dump_json()}")
    print(f"Call Sum 1 2 = {run(s.call, 1,2)}")
    s12 = s(cst(1), cst(2))
    print(f"Sum 1 2 = {s12}")
    s12.clear()
    print(f"Sum 1 2 = {s12}")
    print(f"Sum 1 2 = {run(s12.evaluate)} {s12}")


def test_random() -> None:
    class Sum(Op[tuple[float, float], float]):
        name: str = "sum"

        async def call(self, a: float, b: float) -> float:
            return a + b

    s = Sum()
    a = cst(20)
    r = rnd()
    b = s(r, a)
    c = s(a, b)
    d = s(c, r)
    print(f"d = {d}")
    print(f"d = {run(d.evaluate)}")
    print(f"d = {run(d.evaluate)}")


def test_randint() -> None:
    class Diff(Op[tuple[float, float], float]):
        name: str = "diff"

        async def call(self, a: float, b: float) -> float:
            return a - b

    d = Diff()
    r = rndi(0, 20)
    c = cst(5.5)
    e = d(r, c)
    f = d(e, r)
    print(f"e = {e}")
    print(f"e = {run(e.evaluate)}")
    print(f"e = {run(e.evaluate)}")
    print(f"f = {f}")
    print(f"f = {run(f.evaluate)}")
    print(f"f = {run(f.evaluate)}")


def test_access() -> None:
    @dataclass
    class A:
        rep: int
        txt: str

    @dataclass
    class B:
        a: list[A]
        b: str
        c: int

    class AToB(Op[A, B]):
        name: str = "atob"

        async def call(self, a: A) -> B:
            return B(a=[a for _ in range(a.rep)], b=a.txt, c=a.rep)

    f = AToB()
    b = f(A(5, "hello"))
    print(b.c)
    print(run((b.c).evaluate))
    print(run((b.a[2].txt.upper()).evaluate))


def test_from_json() -> None:
    from app.ops.settings import LMConfigSetting
    from app.ops.session import session, user

    s = LMConfigSetting()(session(), user())
    print(f"BEFORE {s}")
    value = s.to_json()
    s = Computation.from_json(value)
    print(f"AFTER {s}")


def test_to_json() -> None:
    class Sum(Op[tuple[float, float], float]):
        name: str = "sum"

        async def call(self, a: float, b: float) -> float:
            return a + b

    s = Sum()
    s12 = s(cst(1), cst(2))
    print(s12.to_json())


def test_flatten() -> None:
    pass
