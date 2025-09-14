from __future__ import annotations

import functools
import sys
import time
import traceback
from dataclasses import dataclass
from typing import TYPE_CHECKING, ParamSpec, TypeVar

from rich.console import Console
from rich.panel import Panel
from rich.status import Status
from rich.text import Text

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


def handle_cli_errors() -> Callable[[Callable[P, T]], Callable[P, T | None]]:  # [AI GENERATED]
    """CLI 向けの一元的な例外表示デコレータ

    ポリシー:
        * ValueError: 警告 (黄色) として短いメッセージのみ表示
        * RuntimeError: エラー (赤) として短いメッセージのみ表示
        * その他の例外: "Unexpected error" 見出し + メッセージ (赤) を表示し終了コード 1

    Traceback はデフォルト非表示 (将来的に --debug/-d で制御予定)。

    Returns:
        Callable: ラップされた関数。例外発生時は None を返す (終了コードは 0 継続; 呼び出し側で制御可)
    """

    def decorator(func: Callable[P, T]) -> Callable[P, T | None]:  # [AI GENERATED]
        @functools.wraps(func)
        def wrapped(*args: P.args, **kwargs: P.kwargs) -> T | None:  # [AI GENERATED]
            try:
                return func(*args, **kwargs)
            except ValueError as exc:  # [AI GENERATED]
                text = Text(str(exc), style="yellow")
                console.print(Panel(text, title="Warning", border_style="yellow"))
                return None
            except RuntimeError as exc:  # [AI GENERATED]
                text = Text(str(exc), style="red")
                console.print(Panel(text, title="Error", border_style="red"))
                return None
            except Exception as exc:  # [AI GENERATED]
                # 予期しない例外。将来的に --debug で traceback 表示切替予定。
                err_text = Text(str(exc), style="bold red")
                console.print(Panel(err_text, title="Unexpected error", border_style="red"))
                # 内部用に標準エラーへ traceback を落としておく (静かに)  [AI GENERATED]
                traceback.print_exception(exc.__class__, exc, exc.__traceback__, file=sys.stderr)
                return None

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
