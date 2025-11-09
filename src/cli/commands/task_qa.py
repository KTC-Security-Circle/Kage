"""Quick Action Task CLI commands.

QuickActionCommand を利用したタスク生成・一覧表示の補助コマンド群。
既存の `task` コマンドを汚さずにクイックアクション関連機能を疎結合に追加する。
"""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

import questionary
import typer
from rich import box
from rich.console import Console
from rich.table import Table

from cli.utils import elapsed_time, handle_cli_errors, with_spinner
from logic.application.apps import ApplicationServices

if TYPE_CHECKING:  # pragma: no cover - 型チェックのみ
    from logic.application.task_application_service import TaskApplicationService
    from models import TaskRead

app = typer.Typer(help="クイックアクション経由のタスク操作 (list/describe/create)")
console = Console()


def _get_service() -> TaskApplicationService:
    apps = ApplicationServices.create()
    return apps.task

    # return service_container.get_service(TaskApplicationService)


# === Helpers ===
@elapsed_time()
@with_spinner("Loading quick actions...")
def _load_quick_actions() -> list[QuickActionCommand]:  # [AI GENERATED]
    service = _get_service()
    return service.get_available_quick_actions()


@elapsed_time()
@with_spinner("Fetching quick action description...")
def _describe_quick_action(action: QuickActionCommand) -> str:  # [AI GENERATED]
    service = _get_service()
    return service.get_quick_action_description(action)


@elapsed_time()
@with_spinner("Creating task from quick action...")
def _create_task_from_quick_action(
    action: QuickActionCommand, title: str, description: str, due_date: date | None
) -> TaskRead:  # [AI GENERATED]
    """QuickAction からタスクを生成するサービス呼び出しヘルパー [AI GENERATED]

    Args:
        action: アクション種別
        title: タイトル
        description: 説明
        due_date: 期限日

    Returns:
        Any: サービスから返る TaskRead ラッパー (TimingResult)
    """
    service = _get_service()
    return service.create_task_from_quick_action(action=action, title=title, description=description, due_date=due_date)


def _print_quick_actions(actions: list[QuickActionCommand], elapsed: float) -> None:  # [AI GENERATED]
    service = _get_service()
    table = Table(
        title=" Quick Actions ",
        caption=f"Total: {len(actions)}, Elapsed: {elapsed:.2f}s",
        show_header=True,
        header_style="bold magenta",
        box=box.SIMPLE_HEAVY,
    )
    table.add_column("Action")
    table.add_column("Description")
    for a in actions:
        desc = service.get_quick_action_description(a)
        table.add_row(a.value, desc)
    console.print(table)


# === Commands ===


@app.command("list", help="利用可能なクイックアクションを一覧表示")
@handle_cli_errors()
def list_quick_actions() -> None:
    """QuickActionCommand の一覧を表示するコマンド [AI GENERATED]

    利用可能なアクションとその説明文をテーブル形式で表示します。
    """
    actions_res = _load_quick_actions()
    _print_quick_actions(actions_res.result, actions_res.elapsed)


@app.command("describe", help="特定クイックアクションの説明を表示")
@handle_cli_errors()
def describe_quick_action(action: QuickActionCommand) -> None:
    """特定の QuickActionCommand の詳細説明を表示するコマンド [AI GENERATED]

    Args:
        action: 対象クイックアクション
    """
    desc_res = _describe_quick_action(action)
    console.print(f"[bold cyan]{action.value}[/bold cyan]: {desc_res.result} (Elapsed: {desc_res.elapsed:.2f}s)")


@app.command("create", help="クイックアクションを使ってタスク作成")
@handle_cli_errors()
def create_task_from_quick_action(
    action: QuickActionCommand | None = None,
    title: str | None = None,
    description: str | None = None,
    due: str | None = None,
) -> None:
    """QuickAction からタスクを生成するコマンド [AI GENERATED]

    未指定のパラメータは対話的に入力を促します。

    Args:
        action: QuickActionCommand
        title: タイトル
        description: 説明
        due: 期限 (YYYY-MM-DD)
    """
    # 対話入力
    if action is None:
        choice = questionary.select("Select Quick Action", choices=[a.value for a in QuickActionCommand]).ask()
        if choice:
            action = QuickActionCommand(choice)
    if title is None:
        title = questionary.text("Title?").ask()
    if description is None:
        description = questionary.text("Description? (optional)").ask() or ""

    if action is None or title is None:
        msg = "action と title は必須です"  # [AI GENERATED]
        raise typer.BadParameter(msg)

    due_date: date | None = None
    if due:
        try:
            due_date = date.fromisoformat(due)
        except ValueError:
            console.print("[yellow]Invalid date format -> ignore[/yellow]")

    created = _create_task_from_quick_action(
        action=action, title=title, description=description or "", due_date=due_date
    )
    task = created.result
    console.print(
        f"[green]Created via {action.value}:[/green] {task.title} ({task.id}) Elapsed: {created.elapsed:.2f}s"
    )


__all__ = ["app"]
