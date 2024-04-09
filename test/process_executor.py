import multiprocessing.managers
import time
import multiprocessing
import asyncio
import threading
from typing import Any, Callable, Coroutine, List, Dict

class ProccessSafeFunction:
    def __init__(self, func: Callable) -> None:
        self._func = func
    def __call__(self, *args: Any, **kwds: Any) -> Any:
        self._func(*args, **kwds)


class ABCExecutor:
    def __init__(self, coro: Coroutine) -> None:
        raise NotImplementedError

    async def wait(self) -> None:
        raise NotImplementedError
    
    def is_set(self) -> bool:
        raise NotImplementedError

    def get_result(self) -> Any | None:
        raise NotImplementedError

class ProccessExecutor(ABCExecutor):
    def __init__(self, coro: Coroutine) -> None:
        self._event = multiprocessing.Event()

    async def wait(self) -> None:
        await self._event.wait()

    def is_set(self) -> bool:
        return self._event.is_set()

    def get_result(self) -> Any | None:
        raise NotImplementedError()

    def _run(self) -> None:
        self._result = asyncio.run(self._coro())
        self._event.set()
