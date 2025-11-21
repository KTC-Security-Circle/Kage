"""Project related CLI commands.

GUI層の代替として Application Service を呼び出す Typer サブコマンド群。
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import questionary
import typer
from rich import box
from rich.console import Console
from rich.table import Table

from cli.utils import elapsed_time, handle_cli_errors, with_spinner
from logic.application.apps import ApplicationServices
from models import ProjectStatus

if TYPE_CHECKING:
    import uuid

    from logic.application.project_application_service import ProjectApplicationService
    from models import ProjectRead, ProjectUpdate

app = typer.Typer(help="プロジェクト CRUD / 検索 コマンド")
console = Console()


def _get_service() -> ProjectApplicationService:
    apps = ApplicationServices.create()
    return apps.project


@elapsed_time()
@with_spinner("Loading projects...")
def _get_all_projects() -> list[ProjectRead]:
    service = _get_service()
    return service.get_all_projects()


@elapsed_time()
@with_spinner("Creating project...")
def _create_project(title: str, description: str | None) -> ProjectRead:
    service = _get_service()
    return service.create(title, description)


@elapsed_time()
@with_spinner("Fetching project...")
def _get_project(project_id: uuid.UUID) -> ProjectRead:
    service = _get_service()
    return service.get_by_id(project_id)


@elapsed_time()
@with_spinner("Searching projects...")
def _search_projects(query: str, status: ProjectStatus | None = None) -> list[ProjectRead]:
    service = _get_service()
    return service.search(query, status=status)


@elapsed_time()
@with_spinner("Updating project...")
def _update_project(project_id: uuid.UUID, update_data: ProjectUpdate) -> ProjectRead:
    service = _get_service()
    return service.update(project_id, update_data)


@elapsed_time()
@with_spinner("Deleting project...")
def _delete_project(project_id: uuid.UUID) -> None:
    service = _get_service()
    service.delete(project_id)


@app.command("list", help="全プロジェクト一覧を表示")
@handle_cli_errors()
def list_projects() -> None:
    """全プロジェクトを一覧表示するコマンド

    ApplicationService から全件取得し Rich Table で出力します。
    """
    result = _get_all_projects()
    projects = result.result
    table = Table(
        title="Projects",
        box=box.SIMPLE_HEAVY,
        caption=f"Total: {len(projects)} Elapsed: {result.elapsed:.2f}s",
    )
    table.add_column("ID")
    table.add_column("Title")
    table.add_column("Status")
    for p in projects:
        table.add_row(str(p.id), p.title, p.status.value if hasattr(p.status, "value") else str(p.status))
    console.print(table)


@app.command("create", help="新しいプロジェクトを作成")
@handle_cli_errors()
def create_project(
    title: str | None = typer.Option(None, "--title", "-t", help="プロジェクトタイトル"),
    description: str | None = typer.Option(None, "--desc", "-d", help="説明"),
) -> None:
    """新しいプロジェクトを作成するコマンド

    Args:
        title: プロジェクトタイトル (未指定なら対話入力)
        description: 説明 (未指定なら対話入力可)
        status: 初期ステータス
    """
    if title is None:
        title = questionary.text("Title?").ask()
    if description is None:
        description = questionary.text("Description? (optional)").ask()

    if title is None:
        msg = "title が必要です"
        raise typer.BadParameter(msg)
    result = _create_project(title, description)
    project = result.result
    console.print(f"[green]Created:[/green] {project.title} ({project.id}) Elapsed: {result.elapsed:.2f}s")


@app.command("get", help="ID指定で取得")
@handle_cli_errors()
def get_project(project_id: str) -> None:
    """ID を指定してプロジェクトの詳細を取得するコマンド

    Args:
        project_id: 取得対象プロジェクト UUID 文字列
    """
    import uuid as _uuid

    pid = _uuid.UUID(project_id)
    result = _get_project(pid)
    project = result.result
    table = Table(title="Project Detail", box=box.MINIMAL_DOUBLE_HEAD, caption=f"Elapsed: {result.elapsed:.2f}s")
    table.add_column("Field")
    table.add_column("Value")
    table.add_row("ID", str(project.id))
    table.add_row("Title", project.title)
    table.add_row(
        "Status",
        project.status.value if hasattr(project.status, "value") else str(project.status),
    )
    table.add_row("Description", project.description or "")
    console.print(table)


@app.command("search", help="タイトル部分一致検索")
@handle_cli_errors()
def search_projects(query: str) -> None:
    """タイトルの部分一致でプロジェクトを検索するコマンド

    Args:
        query: 検索語 (部分一致)
    """
    result = _search_projects(query)
    results = result.result
    if not results:
        console.print("[yellow]No results[/yellow]")
        raise typer.Exit(code=0)
    table = Table(
        title=f"Search: {query}",
        box=box.SIMPLE,
        caption=f"Hits: {len(results)} Elapsed: {result.elapsed:.2f}s",
    )
    table.add_column("ID")
    table.add_column("Title")
    table.add_column("Status")
    for p in results:
        table.add_row(str(p.id), p.title, p.status.value if hasattr(p.status, "value") else str(p.status))
    console.print(table)


@app.command("update", help="既存プロジェクトを更新")
@handle_cli_errors()
def update_project(
    project_id: str = typer.Argument(..., help="対象プロジェクトID"),
    title: str | None = typer.Option(None, "--title", "-t", help="新しいタイトル"),
    description: str | None = typer.Option(None, "--desc", "-d", help="説明"),
    status: ProjectStatus | None = None,
) -> None:
    """既存プロジェクトのタイトル/説明/ステータスを更新するコマンド

    未指定の場合は対話入力モードに入ります。

    Args:
        project_id: 対象プロジェクト UUID
        title: 新タイトル
        description: 新説明
        status: 新ステータス
    """
    import uuid as _uuid

    from models import ProjectUpdate

    pid = _uuid.UUID(project_id)
    if title is None and description is None and status is None:
        # interactive prompt if nothing provided
        title = questionary.text("New Title (blank=skip)").ask() or None
        description = questionary.text("New Description (blank=skip)").ask() or None
        if questionary.confirm("Change status?").ask():
            status_choice = questionary.select("Status", choices=[s.value for s in ProjectStatus]).ask()
            if status_choice:
                status = ProjectStatus(status_choice)

    update_data = ProjectUpdate(title=title, description=description, status=status)
    result = _update_project(pid, update_data)
    updated = result.result
    console.print(f"[green]Updated:[/green] {updated.title} ({updated.id}) Elapsed: {result.elapsed:.2f}s")


@app.command("delete", help="プロジェクト削除")
@handle_cli_errors()
def delete_project(
    project_id: str,
    force: bool = typer.Option(
        default=False,
        help="確認なしで削除",
        rich_help_panel="Danger",
    ),
) -> None:
    """プロジェクトを削除するコマンド

    force 指定が無い場合は確認プロンプトを表示します。

    Args:
        project_id: 削除対象 UUID
        force: 確認無しで削除するか
    """
    import uuid as _uuid

    pid = _uuid.UUID(project_id)
    if (not force) and (not questionary.confirm("Delete this project?").ask()):
        console.print("[yellow]Cancelled[/yellow]")
        raise typer.Exit(code=1)
    _delete_project(pid)
    console.print(f"[red]Deleted:[/red] {pid}")
