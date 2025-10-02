"""Task status / board CLI commands.

タスクステータス表示情報およびボードカラム構成を参照する独立コマンド群。
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import typer
from rich import box
from rich.console import Console
from rich.table import Table

from cli.utils import elapsed_time, handle_cli_errors, with_spinner

if TYPE_CHECKING:  # [AI GENERATED] 型チェック専用インポート
    from collections.abc import Sequence

    from logic.services.task_status_display_service import TaskStatusDisplay
    from models import TaskStatus

if TYPE_CHECKING:  # pragma: no cover
    from logic.application.task_application_service import TaskApplicationService
    from logic.services.task_status_display_service import TaskStatusDisplay
    from models import TaskStatus

app = typer.Typer(help="タスクステータス表示 / ボード定義参照")
console = Console()


def _get_service() -> TaskApplicationService:  # [AI GENERATED]
    """TaskApplicationService を取得 [AI GENERATED]"""
    from logic.application.task_application_service import TaskApplicationService
    from logic.container import service_container

    return service_container.get_service(TaskApplicationService)


@elapsed_time()
@with_spinner("Loading status displays...")
def _load_all_status_displays() -> list[TaskStatusDisplay]:  # [AI GENERATED]
    service = _get_service()
    return service.get_all_status_displays()


@elapsed_time()
@with_spinner("Loading board mapping...")
def _load_board_mapping() -> dict[str, list[TaskStatus]]:
    service = _get_service()
    return service.get_board_column_mapping()


def _print_status_displays(displays: Sequence[TaskStatusDisplay], elapsed: float) -> None:  # [AI GENERATED]
    table = Table(
        title=" Task Status Displays ",
        caption=f"Count: {len(displays)} Elapsed: {elapsed:.2f}s",
        box=box.SIMPLE_HEAVY,
        show_header=True,
        header_style="bold blue",
    )
    table.add_column("Status")
    table.add_column("Label")
    table.add_column("Icon")
    table.add_column("Description")
    table.add_column("Color")
    for d in displays:
        table.add_row(d.status.value, d.label, d.icon, d.description, d.color)
    console.print(table)


def _print_board_mapping(mapping: dict[str, list[TaskStatus]], elapsed: float) -> None:  # [AI GENERATED]
    table = Table(
        title=" Task Board Columns ",
        caption=f"Elapsed: {elapsed:.2f}s",
        box=box.SIMPLE_HEAVY,
        show_header=True,
        header_style="bold magenta",
    )
    table.add_column("Section")
    table.add_column("Statuses")
    for section, statuses in mapping.items():
        table.add_row(section, ", ".join(s.value for s in statuses))
    console.print(table)


@app.command("displays", help="全タスクステータスの表示情報を一覧")
@handle_cli_errors()
def list_status_displays() -> None:
    """TaskStatusDisplay 一覧を表示するコマンド [AI GENERATED]"""
    res = _load_all_status_displays()
    _print_status_displays(res.result, res.elapsed)


@app.command("board", help="ボードカラム構成を表示")
@handle_cli_errors()
def show_board_mapping() -> None:
    """ボードカラム -> ステータスのマッピングを表示するコマンド [AI GENERATED]"""
    res = _load_board_mapping()
    _print_board_mapping(res.result, res.elapsed)


__all__ = ["app"]
