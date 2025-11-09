"""AsyncExecutor adapter for View layer asynchronous operations.

This module provides a minimal abstraction (`AsyncExecutor`) used by Views to
run synchronous or asynchronous callables without blocking the UI thread.

Design goals (OpenSpec organize-view-layer):
    - Decouple View code from direct asyncio task management
    - Provide a single entry point `run` supporting both sync and awaitable targets
    - Allow future replacement (thread pool policy, cancellation tracking, etc.)

Caveats:
    - Cancellation management is basic; callers owning the returned task must cancel if needed.
    - For CPU-bound heavy sync operations, consider an explicit ProcessPool in later changes.
"""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, TypeVar, overload

if TYPE_CHECKING:  # for typing only
    from collections.abc import Awaitable, Callable

T = TypeVar("T")


class AsyncExecutor:
    """Utility executor for View layer.

    Provides a unified interface for scheduling sync or async work. For sync
    callables it uses the loop's default executor (thread pool). For awaitables
    it wraps them in `asyncio.create_task`.
    """

    @overload
    @staticmethod
    def run(fn_or_coro: Callable[[], T]) -> asyncio.Task[T]:  # pragma: no cover - overload stub
        ...

    @overload
    @staticmethod
    def run(fn_or_coro: Awaitable[T]) -> asyncio.Task[T]:  # pragma: no cover - overload stub
        ...

    @staticmethod
    def run(fn_or_coro: Callable[[], T] | Awaitable[T]) -> asyncio.Task[T]:
        """Schedule a callable or awaitable.

        Args:
            fn_or_coro: A zero-arg synchronous callable or an awaitable.

        Returns:
            The created `asyncio.Task` executing the work.
        """
        loop = asyncio.get_running_loop()
        if callable(fn_or_coro) and not asyncio.iscoroutinefunction(fn_or_coro):  # sync callable

            async def _wrap_sync() -> T:
                return await loop.run_in_executor(None, fn_or_coro)

            return asyncio.create_task(_wrap_sync())
        # Assume awaitable/coroutine
        if callable(fn_or_coro) and asyncio.iscoroutinefunction(fn_or_coro):  # coroutine function
            return asyncio.create_task(fn_or_coro())  # type: ignore[arg-type]
        return asyncio.create_task(fn_or_coro)  # type: ignore[arg-type]
