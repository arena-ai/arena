from time import time
from asyncio import sleep
from anyio import run
from pytest import fixture

from app.ops.computation import Op, Computation
from app.ops.events import LogRequest, Request

T = time()

class SleepConst(Op):
    name: str = "sleep_const"
    value: str
    async def call(self) -> str:
        print(f"\n{time()-T} start const")
        await sleep(1)
        print(f"\n{time()-T} stop const")
        return self.value

class SleepPipe(Op):
    name: str = "sleep_pipe"
    async def call(self, value: str) -> str:
        print(f"\n{time()-T} start pipe")
        await sleep(1)
        print(f"\n{time()-T} stop pipe")
        return f"{value}."

class SleepPipeMany(Op):
    name: str = "sleep_pipe_many"
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
