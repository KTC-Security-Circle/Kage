"""Task related CLI commands.

Application Serviceを介したタスク操作。
"""

from __future__ import annotations

import uuid
from datetime import date
from typing import TYPE_CHECKING

import questionary
import typer
from rich import box
from rich.console import Console
from rich.table import Table

from cli.utils import elapsed_time, with_spinner
from models import TaskRead, TaskStatus

if TYPE_CHECKING:
    from logic.application.task_application_service import TaskApplicationService
    from logic.commands.task_commands import CreateTaskCommand, DeleteTaskCommand, UpdateTaskCommand
    from logic.queries.task_queries import GetTaskByIdQuery

app = typer.Typer(help="タスク CRUD / ステータス操作")
console = Console()


def _get_service() -> TaskApplicationService:
    from logic.container import service_container

    return service_container.get_task_application_service()


@elapsed_time()
@with_spinner("Loading tasks...")
def _load_tasks(status: TaskStatus) -> list[TaskRead]:
    from logic.queries.task_queries import GetTasksByStatusQuery

    service = _get_service()
    return service.get_tasks_by_status(GetTasksByStatusQuery(status=status))


@elapsed_time()
@with_spinner("Loading all tasks...")
def _list_all_tasks() -> dict[TaskStatus, list[TaskRead]]:
    from logic.queries.task_queries import GetAllTasksByStatusDictQuery

    service = _get_service()
    return service.get_all_tasks_by_status_dict(GetAllTasksByStatusDictQuery())


@elapsed_time()
@with_spinner("Creating task...")
def _create_task(cmd: CreateTaskCommand) -> TaskRead:
    """タスク作成サービス呼び出し [AI GENERATED]

    Args:
        cmd (CreateTaskCommand): タスク作成コマンド

    Returns:
        TaskRead: 作成されたタスク
    """
    service = _get_service()
    return service.create_task(cmd)


@elapsed_time()
@with_spinner("Fetching task...")
def _get_task(query: GetTaskByIdQuery) -> TaskRead | None:
    """IDでタスク取得サービス呼び出し [AI GENERATED]

    Args:
        query (GetTaskByIdQuery): タスク取得クエリ

    Returns:
        TaskRead | None: 取得結果（存在しない場合 None）
    """
    service = _get_service()
    return service.get_task_by_id(query)


@elapsed_time()
@with_spinner("Updating task...")
def _update_task(cmd: UpdateTaskCommand) -> TaskRead:
    """タスク更新サービス呼び出し [AI GENERATED]

    Args:
        cmd (UpdateTaskCommand): 更新コマンド

    Returns:
        TaskRead: 更新後タスク
    """
    service = _get_service()
    return service.update_task(cmd)


@elapsed_time()
@with_spinner("Deleting task...")
def _delete_task(cmd: DeleteTaskCommand) -> None:
    """タスク削除サービス呼び出し [AI GENERATED]

    Args:
        cmd (DeleteTaskCommand): 削除コマンド
    """
    service = _get_service()
    service.delete_task(cmd)


@elapsed_time()
@with_spinner("Changing status...")
def _change_status(cmd: UpdateTaskCommand) -> TaskRead:
    """ステータス変更（更新再利用）サービス呼び出し [AI GENERATED]

    Args:
        cmd (UpdateTaskCommand): 更新コマンド

    Returns:
        TaskRead: 更新後タスク
    """
    service = _get_service()
    return service.update_task(cmd)


def _print_tasks_table(tasks: list[TaskRead], title: str, elapsed: float, add_caption: str | None = None) -> None:
    title = f" Tasks - {title} "
    caption = f"Total: {len(tasks)}, Elapsed: {elapsed:.2f}s" + (f" | {add_caption}" if add_caption else "")
    table = Table(
        title=title,
        caption=caption,
        show_header=True,
        header_style="bold blue",
        box=box.SIMPLE_HEAVY,
        row_styles=["none", "dim"],
    )
    for key in TaskRead.model_fields:
        table.add_column(key.capitalize())  # カラム追加
    for t in tasks:
        table.add_row(
            *(
                # TaskReadのフィールドを動的に取得して表示
                # Noneまたは空文字の場合はN/A表示
                str(getattr(t, key))
                if getattr(t, key) is not None and getattr(t, key) != ""
                else "[yellow]N/A[/yellow]"
                for key in TaskRead.model_fields
            )
        )
    console.print(table)


@app.command("list", help="ステータスで一覧表示")
def list_tasks(
    status: TaskStatus = TaskStatus.INBOX,
    *,
    all_: bool = typer.Option(None, "--all", "-a", help="flagを付けると全てのタスクを表示"),
) -> None:
    if all_:
        all_tasks = _list_all_tasks()
        # all_tasksからtaskを取り出して表示
        tasks = []
        for task_list in all_tasks.result.values():
            tasks.extend(task_list)
        _print_tasks_table(tasks, "all", elapsed=all_tasks.elapsed)
        return

    tasks = _load_tasks(status)
    _print_tasks_table(tasks.result, status.value, elapsed=tasks.elapsed)


@app.command("create", help="タスク作成")
def create_task(
    title: str | None = typer.Option(None, "--title", "-t"),
    description: str | None = typer.Option(None, "--desc", "-d"),
    status: TaskStatus = TaskStatus.INBOX,
    due: str | None = typer.Option(None, "--due", help="YYYY-MM-DD"),
) -> None:
    from logic.commands.task_commands import CreateTaskCommand

    if title is None:
        title = questionary.text("Title?").ask()
    if description is None:
        description = questionary.text("Description? (optional)").ask()
    due_date: date | None = None
    if due:
        try:
            due_date = date.fromisoformat(due)
        except ValueError:
            console.print("[red]Invalid date format[/red]")
    if title is None:
        msg = "title 必須"
        raise typer.BadParameter(msg)
    cmd = CreateTaskCommand(title=title, description=description or "", status=status, due_date=due_date)
    task = _create_task(cmd)
    console.print(f"[green]Created:[/green] {task.result.title} ({task.result.id}) Elapsed: {task.elapsed:.2f}s")


@app.command("get", help="IDで取得")
def get_task(task_id: str) -> None:
    from logic.queries.task_queries import GetTaskByIdQuery

    tid = uuid.UUID(task_id)
    task = _get_task(GetTaskByIdQuery(task_id=tid))
    if task.result is None:
        console.print("[yellow]Not found[/yellow]")
        raise typer.Exit(code=1)
    table = Table(title="Task Detail", box=box.MINIMAL_DOUBLE_HEAD)
    table.add_column("Field")
    table.add_column("Value")
    detail = task.result
    table.add_row("ID", str(detail.id))
    table.add_row("Title", detail.title)
    table.add_row("Status", detail.status.value)
    table.add_row("Description", detail.description or "")
    table.add_row("Due", detail.due_date.isoformat() if detail.due_date else "")
    table.caption = f"Elapsed: {task.elapsed:.2f}s"
    console.print(table)


@app.command("update", help="タスク更新")
def update_task(
    task_id: str = typer.Argument(...),
    title: str | None = typer.Option(None, "--title", "-t"),
    description: str | None = typer.Option(None, "--desc", "-d"),
    status: TaskStatus | None = None,
    due: str | None = typer.Option(None, "--due"),
) -> None:
    from logic.commands.task_commands import UpdateTaskCommand
    from logic.queries.task_queries import GetTaskByIdQuery

    tid = uuid.UUID(task_id)

    def prompt_interactive() -> tuple[str | None, str | None, TaskStatus | None, str | None]:
        new_title = questionary.text("New Title(blank=skip)").ask() or None
        new_desc = questionary.text("New Description(blank=skip)").ask() or None
        new_status: TaskStatus | None = None
        if questionary.confirm("Change status?").ask():
            status_choice = questionary.select("Status", choices=[s.value for s in TaskStatus]).ask()
            if status_choice:
                new_status = TaskStatus(status_choice)
        new_due: str | None = None
        if questionary.confirm("Change due date?").ask():
            new_due = questionary.text("YYYY-MM-DD(blank=skip)").ask() or None
        return new_title, new_desc, new_status, new_due

    if title is None and description is None and status is None and due is None:
        title, description, status, due = prompt_interactive()

    # 期限変換
    due_date: date | None = None
    if due:
        try:
            due_date = date.fromisoformat(due)
        except ValueError:
            console.print("[yellow]Invalid date -> ignore[/yellow]")
    current = _get_task(GetTaskByIdQuery(task_id=tid))
    if current.result is None:
        console.print("[red]Task not found[/red]")
        raise typer.Exit(code=1)
    current_task = current.result
    title = title or current_task.title
    if description is None:
        description = current_task.description
    status = status or current_task.status

    cmd = UpdateTaskCommand(task_id=tid, title=title, description=description or "", status=status, due_date=due_date)
    updated = _update_task(cmd)
    console.print(
        f"[green]Updated:[/green] {updated.result.title} ({updated.result.id}) Elapsed: {updated.elapsed:.2f}s"
    )


@app.command("delete", help="タスク削除")
def delete_task(task_id: str, force: bool = typer.Option(default=False, help="確認なし")) -> None:  # noqa: FBT001
    from logic.commands.task_commands import DeleteTaskCommand

    tid = uuid.UUID(task_id)
    if (not force) and (not questionary.confirm("Delete this task?").ask()):
        console.print("[yellow]Cancelled[/yellow]")
        raise typer.Exit(code=1)
    deleted = _delete_task(DeleteTaskCommand(task_id=tid))
    console.print(f"[red]Deleted:[/red] {tid} Elapsed: {deleted.elapsed:.2f}s")


@app.command("status", help="ステータス変更")
def change_status(task_id: str, new_status: TaskStatus) -> None:
    from logic.commands.task_commands import UpdateTaskCommand
    from logic.queries.task_queries import GetTaskByIdQuery

    tid = uuid.UUID(task_id)
    current = _get_task(GetTaskByIdQuery(task_id=tid))
    if current.result is None:
        console.print("[red]Not found[/red]")
        raise typer.Exit(code=1)
    cmd = UpdateTaskCommand(
        task_id=tid,
        title=current.result.title,
        description=current.result.description or "",
        status=new_status,
        due_date=current.result.due_date,
    )
    updated = _change_status(cmd)
    console.print(f"[green]Status -> {updated.result.status.value}[/green] Elapsed: {updated.elapsed:.2f}s")
