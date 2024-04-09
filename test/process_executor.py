import multiprocessing.managers
import time
import multiprocessing
import asyncio
import threading
from typing import Any, Callable, Coroutine, List, Dict


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
    def __init__(self, func: Callable) -> None:
        def _run(
            val: multiprocessing.managers.ValueProxy, *args: Any, **kwds: Any
        ) -> Any:
            val.set(func(*args, **kwds))
            return val.get()

        self._event = multiprocessing.Event()
        with multiprocessing.Manager() as manager:
            self._result = manager.Value("i", 0)
        self._process = multiprocessing.Process(target=_run, args=(self._result, 1, 2, 3))
        self._process.start()

    def sync(self) -> None:
        self._process.join()

    async def wait(self) -> None:
        await self._event.wait()

    def is_set(self) -> bool:
        return self._event.is_set()

    def get_result(self) -> Any | None:
        raise NotImplementedError()

    def _run(self) -> None:
        self._result = asyncio.run(self._coro())
        self._event.set()


def my_func(x: int, y: int, z: int) -> int:
    return x + y + z


if __name__ == "__main__":
    ProccessExecutor(my_func).sync()
