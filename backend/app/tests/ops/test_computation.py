from time import time
from asyncio import sleep
from anyio import run
from pytest import fixture

from app.ops.computation import Op, Computation, FlatComputation, FlatComputations
from app.ops.events import LogRequest, Request
from app.ops.dot import dot

T = time()

class SleepConst(Op):
    value: str
    async def call(self) -> str:
        print(f"\n{time()-T} start const")
        await sleep(1)
        print(f"\n{time()-T} stop const")
        return self.value

class SleepPipe(Op):
    async def call(self, value: str) -> str:
        print(f"\n{time()-T} start pipe")
        await sleep(1)
        print(f"\n{time()-T} stop pipe")
        return f"{value}."

class SleepPipeMany(Op):
    async def call(self, *args: str) -> str:
        print(f"\n{time()-T} start pipe many")
        await sleep(1)
        print(f"\n{time()-T} stop pipe many")
        return f"{'.'.join(args)}."

@fixture
def sleep_hello() -> SleepConst:
    return SleepConst(value="Hello")

@fixture
def sleep_world() -> SleepConst:
    return SleepConst(value="World")

@fixture
def sleep_pipe() -> SleepPipe:
    return SleepPipe()

@fixture
def sleep_pipe_many() -> SleepPipeMany:
    return SleepPipeMany()


def test_const_pipe(sleep_hello, sleep_pipe):
    comp = sleep_pipe(sleep_hello())
    value = run(comp.evaluate)
    print(value)


def test_many_const_pipe(sleep_hello, sleep_world, sleep_pipe_many):
    comp = sleep_pipe_many(sleep_hello(), sleep_world())
    value = run(comp.evaluate)
    print(value)


def test_const_many_pipe(sleep_hello, sleep_pipe):
    comp = sleep_pipe(sleep_pipe(sleep_hello()))
    value = run(comp.evaluate)
    print(value)


def test_to_json(sleep_hello, sleep_pipe):
    comp = sleep_pipe(sleep_pipe(sleep_hello()))
    print(comp.to_json())


def test_from_json(sleep_hello, sleep_pipe):
    comp = sleep_pipe(sleep_pipe(sleep_hello()))
    print(f'BEFORE {comp}')
    value = comp.to_json()
    comp = Computation.from_json(value)
    print(f'AFTER {comp}')


def test_flat_computations(sleep_hello, sleep_world, sleep_pipe, sleep_pipe_many):
    init_comp = sleep_pipe_many(sleep_hello(), sleep_world())
    comp = sleep_pipe_many(init_comp, sleep_pipe(init_comp))
    print(f'comp = {dot(comp)}')
    print(f'comps = {[c.op.__class__.__name__ for c in comp.computations()]}')
    flat_comps = FlatComputations.from_computation(comp)
    print(f'flat_comps = {flat_comps}')