from __future__ import annotations

import functools
import time
from dataclasses import dataclass
from typing import TYPE_CHECKING, ParamSpec, TypeVar

from rich.console import Console
from rich.status import Status

if TYPE_CHECKING:
    from collections.abc import Callable


P = ParamSpec("P")
T = TypeVar("T")

console = Console()


@dataclass(slots=True)
class TimingResult[T]:
    """計測結果を表すデータ構造

    Args:
        result (T): 元関数の戻り値
        elapsed (float): 経過秒数
    """

    result: T
    elapsed: float


class SpinnerError(RuntimeError):
    """スピナー付き処理内で発生した例外をラップするエラー。"""

    def __init__(self, func_name: str) -> None:
        super().__init__(f"{func_name} failed")


def with_spinner(message: str) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """スピナーを表示しつつ関数を実行するデコレータ

    Args:
        message (str): スピナー横に表示するメッセージ

    Returns:
        Callable[[Callable[P, R]], Callable[P, R]]: デコレータ
    """

    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @functools.wraps(func)
        def wrapped(*args: P.args, **kwargs: P.kwargs) -> T:
            with Status(f"[bold green]{message}", spinner="bouncingBall"):
                try:
                    return func(*args, **kwargs)
                except Exception as exc:
                    raise SpinnerError(func.__name__) from exc

        return wrapped

    return decorator


def elapsed_time() -> Callable[[Callable[P, T]], Callable[P, TimingResult[T]]]:
    """関数の実行時間を計測するデコレータ

    Returns:
        Callable[[Callable[P, T]], Callable[P, TimingResult[T]]]: 計測付きラッパー
    """

    def decorator(func: Callable[P, T]) -> Callable[P, TimingResult[T]]:
        @functools.wraps(func)
        def wrapped(*args: P.args, **kwargs: P.kwargs) -> TimingResult[T]:
            start = time.perf_counter()
            result = func(*args, **kwargs)
            elapsed = time.perf_counter() - start
            return TimingResult(result=result, elapsed=elapsed)

        return wrapped

    return decorator


if __name__ == "__main__":
    # テスト用コード
    @elapsed_time()
    @with_spinner("Testing spinner")
    def test_function() -> None:
        time.sleep(3)
        # raise NotImplementedError("Test error")

    result = test_function()
    console.log(f"Elapsed: {result.elapsed:.2f} seconds")
