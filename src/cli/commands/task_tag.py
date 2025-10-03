"""Task-Tag relation CLI commands.

タスクとタグの関連付け管理コマンド。
"""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

import typer
from rich import box
from rich.console import Console
from rich.table import Table

from cli.utils import elapsed_time, handle_cli_errors, with_spinner

if TYPE_CHECKING:
    from logic.application.task_tag_application_service import TaskTagApplicationService
    from logic.commands.task_tag_commands import (
        CreateTaskTagCommand,
        DeleteTaskTagCommand,
        DeleteTaskTagsByTagCommand,
        DeleteTaskTagsByTaskCommand,
    )
    from logic.queries.task_tag_queries import (
        CheckTaskTagExistsQuery,
        GetAllTaskTagsQuery,
        GetTaskTagByTaskAndTagQuery,
        GetTaskTagsByTagIdQuery,
        GetTaskTagsByTaskIdQuery,
    )
    from models import TaskTagRead

app = typer.Typer(help="タスクとタグ関連操作")
console = Console()


def _get_service() -> TaskTagApplicationService:  # type: ignore[name-defined]
    from logic.application.task_tag_application_service import TaskTagApplicationService
    from logic.container import service_container

    return service_container.get_service(TaskTagApplicationService)


# ==== Helpers ====
@elapsed_time()
@with_spinner("Linking tag to task...")
def _create_relation(cmd: CreateTaskTagCommand) -> TaskTagRead:  # [AI GENERATED]
    service = _get_service()
    return service.create_task_tag(cmd)


@elapsed_time()
@with_spinner("Removing relation...")
def _delete_relation(cmd: DeleteTaskTagCommand) -> None:  # [AI GENERATED]
    service = _get_service()
    service.delete_task_tag(cmd)


@elapsed_time()
@with_spinner("Clearing task relations...")
def _clear_task(cmd: DeleteTaskTagsByTaskCommand) -> None:  # [AI GENERATED]
    service = _get_service()
    service.delete_task_tags_by_task_id(cmd)


@elapsed_time()
@with_spinner("Clearing tag relations...")
def _clear_tag(cmd: DeleteTaskTagsByTagCommand) -> None:  # [AI GENERATED]
    service = _get_service()
    service.delete_task_tags_by_tag_id(cmd)


@elapsed_time()
@with_spinner("Loading relations...")
def _list_all(query: GetAllTaskTagsQuery) -> list[TaskTagRead]:  # [AI GENERATED]
    service = _get_service()
    return service.get_all_task_tags(query)


@elapsed_time()
@with_spinner("Filtering by task...")
def _list_by_task(query: GetTaskTagsByTaskIdQuery) -> list[TaskTagRead]:  # [AI GENERATED]
    service = _get_service()
    return service.get_task_tags_by_task_id(query)


@elapsed_time()
@with_spinner("Filtering by tag...")
def _list_by_tag(query: GetTaskTagsByTagIdQuery) -> list[TaskTagRead]:  # [AI GENERATED]
    service = _get_service()
    return service.get_task_tags_by_tag_id(query)


@elapsed_time()
@with_spinner("Checking relation...")
def _get_single(query: GetTaskTagByTaskAndTagQuery) -> TaskTagRead | None:  # [AI GENERATED]
    service = _get_service()
    return service.get_task_tag_by_task_and_tag(query)


@elapsed_time()
@with_spinner("Checking existence...")
def _exists(query: CheckTaskTagExistsQuery) -> bool:  # [AI GENERATED]
    service = _get_service()
    return service.check_task_tag_exists(query)


def _print_relations(rows: list[TaskTagRead], title: str, elapsed: float) -> None:  # [AI GENERATED]
    table = Table(
        title=f"Task-Tag Relations - {title}",
        box=box.SIMPLE,
        caption=f"Total: {len(rows)} Elapsed: {elapsed:.2f}s",
    )
    table.add_column("Task ID")
    table.add_column("Tag ID")
    for r in rows:
        table.add_row(str(r.task_id), str(r.tag_id))
    console.print(table)


# ==== Commands ====
@app.command("add", help="タスクへタグ付与")
@handle_cli_errors()
def add(task_id: str, tag_id: str) -> None:  # [AI GENERATED]
    """タスクにタグを関連付けるコマンド [AI GENERATED]

    Args:
        task_id: タスク UUID
        tag_id: タグ UUID
    """
    from logic.commands.task_tag_commands import CreateTaskTagCommand

    t_uuid = uuid.UUID(task_id)
    tag_uuid = uuid.UUID(tag_id)
    created = _create_relation(CreateTaskTagCommand(task_id=t_uuid, tag_id=tag_uuid))
    console.print(
        f"[green]Linked:[/green] task={created.result.task_id} tag={created.result.tag_id} "
        f"Elapsed: {created.elapsed:.2f}s"
    )


@app.command("remove", help="タスクの特定タグ解除")
@handle_cli_errors()
def remove(task_id: str, tag_id: str) -> None:  # [AI GENERATED]
    """タスクから指定タグ関連を削除するコマンド [AI GENERATED]

    Args:
        task_id: タスク UUID
        tag_id: タグ UUID
    """
    from logic.commands.task_tag_commands import DeleteTaskTagCommand

    t_uuid = uuid.UUID(task_id)
    tag_uuid = uuid.UUID(tag_id)
    deleted = _delete_relation(DeleteTaskTagCommand(task_id=t_uuid, tag_id=tag_uuid))
    console.print(f"[red]Removed:[/red] task={t_uuid} tag={tag_uuid} Elapsed: {deleted.elapsed:.2f}s")


@app.command("list", help="関連一覧 (フィルタ対応)")
@handle_cli_errors()
def list_relations(
    task: str | None = typer.Option(None, "--task", help="特定タスクIDで絞り込み"),
    tag: str | None = typer.Option(None, "--tag", help="特定タグIDで絞り込み"),
) -> None:  # [AI GENERATED]
    """タスク-タグ関連を一覧表示 (タスク or タグでフィルタ可) するコマンド [AI GENERATED]

    Args:
        task: タスク UUID (フィルタ)
        tag: タグ UUID (フィルタ)
    """
    from logic.queries.task_tag_queries import (
        GetAllTaskTagsQuery,
        GetTaskTagsByTagIdQuery,
        GetTaskTagsByTaskIdQuery,
    )

    if task and tag:
        console.print("[yellow]--task と --tag は同時指定できません[/yellow]")
        raise typer.Exit(code=1)

    if task:
        rows = _list_by_task(GetTaskTagsByTaskIdQuery(task_id=uuid.UUID(task)))
        _print_relations(rows.result, f"task={task}", rows.elapsed)
        return
    if tag:
        rows = _list_by_tag(GetTaskTagsByTagIdQuery(tag_id=uuid.UUID(tag)))
        _print_relations(rows.result, f"tag={tag}", rows.elapsed)
        return

    rows = _list_all(GetAllTaskTagsQuery())
    _print_relations(rows.result, "all", rows.elapsed)


@app.command("clear-task", help="タスクの全タグ関連削除")
@handle_cli_errors()
def clear_task(task_id: str) -> None:  # [AI GENERATED]
    """指定タスクに紐づく全てのタグ関連を削除するコマンド [AI GENERATED]

    Args:
        task_id: タスク UUID
    """
    from logic.commands.task_tag_commands import DeleteTaskTagsByTaskCommand

    t_uuid = uuid.UUID(task_id)
    cleared = _clear_task(DeleteTaskTagsByTaskCommand(task_id=t_uuid))
    console.print(f"[red]Cleared task relations:[/red] task={t_uuid} Elapsed: {cleared.elapsed:.2f}s")


@app.command("clear-tag", help="タグの全タスク関連削除")
@handle_cli_errors()
def clear_tag(tag_id: str) -> None:  # [AI GENERATED]
    """指定タグが付与された全タスクとの関連を削除するコマンド [AI GENERATED]

    Args:
        tag_id: タグ UUID
    """
    from logic.commands.task_tag_commands import DeleteTaskTagsByTagCommand

    tag_uuid = uuid.UUID(tag_id)
    cleared = _clear_tag(DeleteTaskTagsByTagCommand(tag_id=tag_uuid))
    console.print(f"[red]Cleared tag relations:[/red] tag={tag_uuid} Elapsed: {cleared.elapsed:.2f}s")


@app.command("exists", help="特定タスク-タグ関連が存在するか (exit code 0/1)")
@handle_cli_errors()
def exists(task_id: str, tag_id: str) -> None:  # [AI GENERATED]
    """タスク-タグ関連の存在を確認し exit code を返すコマンド [AI GENERATED]

    Args:
        task_id: タスク UUID
        tag_id: タグ UUID
    """
    from logic.queries.task_tag_queries import CheckTaskTagExistsQuery

    t_uuid = uuid.UUID(task_id)
    tag_uuid = uuid.UUID(tag_id)
    res = _exists(CheckTaskTagExistsQuery(task_id=t_uuid, tag_id=tag_uuid))
    console.print(
        f"[blue]Exists:[/blue] task={t_uuid} tag={tag_uuid} -> {'YES' if res.result else 'NO'} "
        f"Elapsed: {res.elapsed:.2f}s"
    )
    raise typer.Exit(code=0 if res.result else 1)
