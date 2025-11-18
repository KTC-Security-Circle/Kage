"""Memo CLI commands.

メモ CRUD / 検索用コマンド。
"""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

import questionary
import typer
from rich import box
from rich.console import Console
from rich.markdown import Markdown
from rich.table import Table

from cli.utils import elapsed_time, handle_cli_errors, with_spinner
from logic.application.apps import ApplicationServices
from models import MemoStatus, MemoUpdate

if TYPE_CHECKING:  # import grouping for type checking only
    from logic.application.memo_application_service import MemoApplicationService
    from models import MemoRead

app = typer.Typer(help="メモ CRUD / 検索")
console = Console()

# Typer Option definitions (lint 対応: デフォルト評価を関数外で実行)
CONTENT_OPT = typer.Option(None, "--content", "-c", help="新しい内容")
STATUS_OPT = typer.Option(None, "--status", "-s", help="新しいステータス")


def _get_service() -> MemoApplicationService:
    apps = ApplicationServices.create()
    return apps.memo


# ==== Helpers ====
@elapsed_time()
@with_spinner("Creating memo...")
def _create_memo(title: str, content: str) -> MemoRead:  # [AI GENERATED]
    service = _get_service()
    return service.create(title, content)


@elapsed_time()
@with_spinner("Updating memo...")
def _update_memo(memo_id: str, data: MemoUpdate) -> MemoRead:  # [AI GENERATED]
    memo_uuid = uuid.UUID(memo_id)
    service = _get_service()
    return service.update(memo_uuid, data)


@elapsed_time()
@with_spinner("Deleting memo...")
def _delete_memo(memo_id: str) -> bool:  # [AI GENERATED]
    memo_uuid = uuid.UUID(memo_id)
    service = _get_service()
    return service.delete(memo_uuid)


@elapsed_time()
@with_spinner("Fetching memo...")
def _get_memo(memo_id: uuid.UUID, *, with_details: bool = False) -> MemoRead | None:  # [AI GENERATED]
    service = _get_service()
    return service.get_by_id(memo_id, with_details=with_details)


@elapsed_time()
@with_spinner("Listing memos...")
def _list_all() -> list[MemoRead]:  # [AI GENERATED]
    service = _get_service()
    return service.get_all_memos()


@elapsed_time()
@with_spinner("Listing all memos...")
def _list_by_task() -> list[MemoRead]:  # [AI GENERATED]
    service = _get_service()
    return service.get_all_memos(with_details=True)


@elapsed_time()
@with_spinner("Searching memos...")
def _search_memos(query: str, status: MemoStatus | None = None) -> list[MemoRead]:  # [AI GENERATED]
    service = _get_service()
    return service.search(query, with_details=True, status=status)


MAX_PREVIEW_LEN = 43  # [AI GENERATED] content preview cutoff
DETAIL_PREVIEW_LEN = 40  # [AI GENERATED] single-line preview length


def _print_memos(memos: list[MemoRead], title: str, elapsed: float) -> None:  # [AI GENERATED]
    """メモ一覧をテーブル形式で表示する

    Args:
        memos: 表示対象のメモリスト
        title: テーブルのタイトル
        elapsed: 処理に要した時間（秒）
    """
    table = Table(
        title=f"Memos - {title}",
        box=box.SIMPLE_HEAVY,
        caption=f"Total: {len(memos)} Elapsed: {elapsed:.2f}s",
    )
    table.add_column("ID")
    table.add_column("Content")
    table.add_column("Status")
    for m in memos:
        content = (m.content[:MAX_PREVIEW_LEN] + "...") if len(m.content) > MAX_PREVIEW_LEN else m.content
        table.add_row(str(m.id), content, m.status.value)
    console.print(table)


# ==== Commands ====
@app.command("create", help="メモ作成")
@handle_cli_errors()
def create(
    title: str = typer.Option(..., "--title", "-t", help="メモタイトル"),
    task_id: str = typer.Option(..., "--task", help="対象タスクID"),
    content: str | None = typer.Option(None, "--content", "-c", help="メモ内容"),
) -> None:  # [AI GENERATED]
    """新しいメモを作成するコマンド [AI GENERATED]

    Args:
        title: メモタイトル
        task_id: 紐づけるタスク UUID
        content: メモ本文 (未指定で対話入力)
    """
    _ = uuid.UUID(task_id)  # タスクID の妥当性チェック
    if content is None:
        content = questionary.text("Memo content?").ask()
    if not content:
        console.print("[red]content 必須[/red]")
        raise typer.Exit(code=1)
    created = _create_memo(title=title, content=content)
    console.print(
        f"[green]Created:[/green] {created.result.id} (title={created.result.title}) Elapsed: {created.elapsed:.2f}s"
    )


@app.command("update", help="メモ更新")
@handle_cli_errors()
def update(
    memo_id: str = typer.Argument(...),
    content: str | None = CONTENT_OPT,
    status: MemoStatus | None = STATUS_OPT,
) -> None:  # [AI GENERATED]
    """既存メモの内容を更新するコマンド [AI GENERATED]

    Args:
        memo_id: 対象メモ UUID
        content: 新しい本文 (未指定で対話入力)
        status: 新しいステータス
    """
    _ = uuid.UUID(memo_id)  # メモID の妥当性チェック
    if content is None:
        content = questionary.text("New content?").ask()
    if not content:
        console.print("[yellow]Cancelled[/yellow]")
        raise typer.Exit(code=1)
    # status can be provided as Enum or as string from the interactive prompt
    if status is None:
        status_choice = questionary.select("Status?", choices=[e.value for e in MemoStatus]).ask()
        status = MemoStatus(status_choice) if status_choice else None
    elif isinstance(status, str):
        # ensure it's an Enum when provided as a string
        status = MemoStatus(status)

    update_payload = MemoUpdate(content=content, status=status)
    updated = _update_memo(memo_id, update_payload)
    console.print(f"[green]Updated:[/green] {updated.result.id} Elapsed: {updated.elapsed:.2f}s")


@app.command("delete", help="メモ削除")
@handle_cli_errors()
def delete(
    memo_id: str,
    force: bool = typer.Option(
        default=False,
        help="確認なし",
        rich_help_panel="Danger",
    ),
) -> None:  # [AI GENERATED]
    """メモを削除するコマンド [AI GENERATED]

    Args:
        memo_id: 対象メモ UUID
        force: 確認を省略するか
    """
    m_uuid = uuid.UUID(memo_id)
    if (not force) and not questionary.confirm("Delete this memo?").ask():
        console.print("[yellow]Cancelled[/yellow]")
        raise typer.Exit(code=1)
    deleted = _delete_memo(memo_id)
    console.print(f"[red]Deleted:[/red] {m_uuid} ({'OK' if deleted.result else 'NG'}) Elapsed: {deleted.elapsed:.2f}s")


@app.command("get", help="IDで取得")
@handle_cli_errors()
def get_memo(memo_id: str) -> None:  # [AI GENERATED]
    """ID 指定でメモ詳細 (Markdown レンダリング含む) を取得するコマンド [AI GENERATED]

    Args:
        memo_id: メモ UUID
    """
    # from logic.queries.memo_queries import GetMemoByIdQuery

    m_uuid = uuid.UUID(memo_id)
    memo = _get_memo(m_uuid, with_details=True)
    if memo.result is None:
        console.print("[yellow]Not found[/yellow]")
        raise typer.Exit(code=1)
    mr = memo.result
    table = Table(title="Memo Detail", box=box.MINIMAL_DOUBLE_HEAD, caption=f"Elapsed: {memo.elapsed:.2f}s")
    table.add_column("Field")
    table.add_column("Value")
    table.add_row("ID", str(mr.id))
    # tasks relation may be present when with_details=True
    tasks = getattr(mr, "tasks", None)
    if tasks:
        table.add_row("Tasks", ", ".join(str(t.id) for t in tasks))
    # 本文は Markdown として別レンダリング (テーブル内は省略)
    snippet = mr.content.splitlines()[0][:DETAIL_PREVIEW_LEN] + ("..." if len(mr.content) > DETAIL_PREVIEW_LEN else "")
    table.add_row("Content (preview)", snippet)
    console.print(table)
    console.print(Markdown(mr.content))


@app.command("list", help="メモ一覧 (フィルタ対応)")
@handle_cli_errors()
def list_memos(
    task: str | None = typer.Option(None, "--task", help="特定タスクIDで絞り込み"),
) -> None:  # [AI GENERATED]
    """メモ一覧を表示 (タスクIDフィルタ対応) するコマンド [AI GENERATED]

    Args:
        task: タスク UUID フィルタ
    """
    if task:
        _ = uuid.UUID(task)  # タスクID の妥当性チェック
        rows = _list_by_task()
        _print_memos(rows.result, f"task={task}", rows.elapsed)
        return
    rows = _list_all()
    _print_memos(rows.result, "all", rows.elapsed)


@app.command("search", help="メモ全文検索 (部分一致)")
@handle_cli_errors()
def search(query: str) -> None:  # [AI GENERATED]
    """メモ本文の部分一致検索を行うコマンド [AI GENERATED]

    Args:
        query: 検索語
    """
    results = _search_memos(query)
    if not results.result:
        console.print("[yellow]No results[/yellow]")
        raise typer.Exit(code=0)
    _print_memos(results.result, f"search='{query}'", results.elapsed)
