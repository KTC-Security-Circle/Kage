"""Project related CLI commands.

GUI層の代替として Application Service を呼び出す Typer サブコマンド群。
"""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

import questionary
import typer
from rich import box
from rich.console import Console
from rich.table import Table

from cli.utils import elapsed_time, handle_cli_errors, with_spinner
from models import ProjectStatus

if TYPE_CHECKING:
    from logic.application.project_application_service import ProjectApplicationService
    from logic.commands.project_commands import CreateProjectCommand, DeleteProjectCommand, UpdateProjectCommand
    from logic.queries.project_queries import GetAllProjectsQuery, GetProjectByIdQuery, SearchProjectsByTitleQuery
    from models import ProjectRead

app = typer.Typer(help="プロジェクト CRUD / 検索 コマンド")
console = Console()


def _get_service() -> ProjectApplicationService:
    from logic.application.project_application_service import ProjectApplicationService
    from logic.container import service_container

    return service_container.get_service(ProjectApplicationService)


@elapsed_time()
@with_spinner("Loading projects...")
def _get_all_projects(query: GetAllProjectsQuery) -> list[ProjectRead]:  # [AI GENERATED]
    service = _get_service()
    return service.get_all_projects(query)


@elapsed_time()
@with_spinner("Creating project...")
def _create_project(cmd: CreateProjectCommand) -> ProjectRead:  # [AI GENERATED]
    service = _get_service()
    return service.create_project(cmd)


@elapsed_time()
@with_spinner("Fetching project...")
def _get_project(query: GetProjectByIdQuery) -> ProjectRead:  # [AI GENERATED]
    service = _get_service()
    return service.get_project_by_id(query)


@elapsed_time()
@with_spinner("Searching projects...")
def _search_projects(query: SearchProjectsByTitleQuery) -> list[ProjectRead]:  # [AI GENERATED]
    service = _get_service()
    return service.search_projects_by_title(query)


@elapsed_time()
@with_spinner("Updating project...")
def _update_project(cmd: UpdateProjectCommand) -> ProjectRead:  # [AI GENERATED]
    service = _get_service()
    return service.update_project(cmd)


@elapsed_time()
@with_spinner("Deleting project...")
def _delete_project(cmd: DeleteProjectCommand) -> None:  # [AI GENERATED]
    service = _get_service()
    service.delete_project(cmd)


@app.command("list", help="全プロジェクト一覧を表示")
@handle_cli_errors()
def list_projects() -> None:
    """全プロジェクトを一覧表示するコマンド [AI GENERATED]

    ApplicationService から全件取得し Rich Table で出力します。
    """
    from logic.queries.project_queries import GetAllProjectsQuery

    projects = _get_all_projects(GetAllProjectsQuery())
    table = Table(
        title="Projects",
        box=box.SIMPLE_HEAVY,
        caption=f"Total: {len(projects.result)} Elapsed: {projects.elapsed:.2f}s",
    )
    table.add_column("ID")
    table.add_column("Title")
    table.add_column("Status")
    for p in projects.result:
        table.add_row(str(p.id), p.title, p.status.value if hasattr(p.status, "value") else str(p.status))
    console.print(table)


@app.command("create", help="新しいプロジェクトを作成")
@handle_cli_errors()
def create_project(
    title: str | None = typer.Option(None, "--title", "-t", help="プロジェクトタイトル"),
    description: str | None = typer.Option(None, "--desc", "-d", help="説明"),
    status: ProjectStatus = ProjectStatus.ACTIVE,
) -> None:  # [AI GENERATED] CLI create project
    """新しいプロジェクトを作成するコマンド [AI GENERATED]

    Args:
        title: プロジェクトタイトル (未指定なら対話入力)
        description: 説明 (未指定なら対話入力可)
        status: 初期ステータス
    """
    from logic.commands.project_commands import CreateProjectCommand

    if title is None:
        title = questionary.text("Title?").ask()
    if description is None:
        description = questionary.text("Description? (optional)").ask()

    if title is None:
        msg = "title が必要です"  # [AI GENERATED] validation message
        raise typer.BadParameter(msg)
    cmd = CreateProjectCommand(title=title, description=description or "", status=status)
    project = _create_project(cmd)
    console.print(
        f"[green]Created:[/green] {project.result.title} ({project.result.id}) Elapsed: {project.elapsed:.2f}s"
    )


@app.command("get", help="ID指定で取得")
@handle_cli_errors()
def get_project(project_id: str) -> None:
    """ID を指定してプロジェクトの詳細を取得するコマンド [AI GENERATED]

    Args:
        project_id: 取得対象プロジェクト UUID 文字列
    """
    from logic.queries.project_queries import GetProjectByIdQuery

    pid = uuid.UUID(project_id)
    project = _get_project(GetProjectByIdQuery(project_id=pid))
    table = Table(title="Project Detail", box=box.MINIMAL_DOUBLE_HEAD, caption=f"Elapsed: {project.elapsed:.2f}s")
    table.add_column("Field")
    table.add_column("Value")
    table.add_row("ID", str(project.result.id))
    table.add_row("Title", project.result.title)
    table.add_row(
        "Status",
        project.result.status.value if hasattr(project.result.status, "value") else str(project.result.status),
    )
    table.add_row("Description", project.result.description or "")
    console.print(table)


@app.command("search", help="タイトル部分一致検索")
@handle_cli_errors()
def search_projects(query: str) -> None:
    """タイトルの部分一致でプロジェクトを検索するコマンド [AI GENERATED]

    Args:
        query: 検索語 (部分一致)
    """
    from logic.queries.project_queries import SearchProjectsByTitleQuery

    results = _search_projects(SearchProjectsByTitleQuery(title_query=query))
    if not results.result:
        console.print("[yellow]No results[/yellow]")
        raise typer.Exit(code=0)
    table = Table(
        title=f"Search: {query}",
        box=box.SIMPLE,
        caption=f"Hits: {len(results.result)} Elapsed: {results.elapsed:.2f}s",
    )
    table.add_column("ID")
    table.add_column("Title")
    table.add_column("Status")
    for p in results.result:
        table.add_row(str(p.id), p.title, p.status.value if hasattr(p.status, "value") else str(p.status))
    console.print(table)


@app.command("update", help="既存プロジェクトを更新")
@handle_cli_errors()
def update_project(
    project_id: str = typer.Argument(..., help="対象プロジェクトID"),
    title: str | None = typer.Option(None, "--title", "-t", help="新しいタイトル"),
    description: str | None = typer.Option(None, "--desc", "-d", help="説明"),
    status: ProjectStatus | None = None,
) -> None:  # [AI GENERATED] CLI update project
    """既存プロジェクトのタイトル/説明/ステータスを更新するコマンド [AI GENERATED]

    未指定の場合は対話入力モードに入ります。

    Args:
        project_id: 対象プロジェクト UUID
        title: 新タイトル
        description: 新説明
        status: 新ステータス
    """
    from logic.commands.project_commands import UpdateProjectCommand

    pid = uuid.UUID(project_id)
    if title is None and description is None and status is None:
        # interactive prompt if nothing provided
        title = questionary.text("New Title (blank=skip)").ask() or None
        description = questionary.text("New Description (blank=skip)").ask() or None
        if questionary.confirm("Change status?").ask():
            status_choice = questionary.select("Status", choices=[s.value for s in ProjectStatus]).ask()
            if status_choice:
                status = ProjectStatus(status_choice)

    cmd = UpdateProjectCommand(project_id=pid, title=title, description=description, status=status)
    updated = _update_project(cmd)
    console.print(
        f"[green]Updated:[/green] {updated.result.title} ({updated.result.id}) Elapsed: {updated.elapsed:.2f}s"
    )


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
    """プロジェクトを削除するコマンド [AI GENERATED]

    force 指定が無い場合は確認プロンプトを表示します。

    Args:
        project_id: 削除対象 UUID
        force: 確認無しで削除するか
    """
    from logic.commands.project_commands import DeleteProjectCommand

    pid = uuid.UUID(project_id)
    if (not force) and (not questionary.confirm("Delete this project?").ask()):
        console.print("[yellow]Cancelled[/yellow]")
        raise typer.Exit(code=1)
    deleted = _delete_project(DeleteProjectCommand(project_id=pid))
    console.print(f"[red]Deleted:[/red] {pid} Elapsed: {deleted.elapsed:.2f}s")
