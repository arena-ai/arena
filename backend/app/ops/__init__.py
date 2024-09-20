"""
Ops are composable functions that can be serialized to be executed in the worker.
Not all computations can be structured as ops.
You should use Ops:
* When dealing with text, numbers, lists, dicts, jsons...
* If you want to benefit from asyncio (when preparing/sending HTTP requests)
* For long tasks you want to delegate to the worker
* Ideal case = LLM calling
"""
from app.ops.utils import Var, var, Tup, tup, Const, cst, Rand, rnd, RandInt, rndi
from app.ops.computation import Op, Computation