"""Tag related CLI commands.

タグ CRUD 操作用のサブコマンド。
"""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

import questionary
import typer
from rich import box
from rich.console import Console
from rich.table import Table

if TYPE_CHECKING:
    from logic.application.tag_application_service import TagApplicationService
    from models import TagRead, TagUpdate

from cli.utils import elapsed_time, handle_cli_errors, with_spinner
from logic.application.apps import ApplicationServices

app = typer.Typer(help="タグ CRUD / 検索")
console = Console()


def _get_service() -> TagApplicationService:
    apps = ApplicationServices.create()
    return apps.tag


@elapsed_time()
@with_spinner("Loading tags...")
def _get_all_tags() -> list[TagRead]:  # [AI GENERATED] helper for list
    """全タグ取得サービス呼び出し [AI GENERATED]

    Args:
        query (GetAllTagsQuery): 全件取得クエリ

    Returns:
        list: TagRead のリスト
    """
    service = _get_service()
    return service.get_all_tags()


@elapsed_time()
@with_spinner("Creating tag...")
def _create_tag(name: str) -> TagRead:  # [AI GENERATED] return TagRead
    service = _get_service()
    return service.create(name)


@elapsed_time()
@with_spinner("Searching tags...")
def _search_tags(query: str) -> TagRead:  # [AI GENERATED] list[TagRead]
    service = _get_service()
    return service.get_by_name(query)


@elapsed_time()
@with_spinner("Fetching tag...")
def _get_tag(tag_id: str) -> TagRead | None:  # [AI GENERATED] TagRead | None
    utag_id = uuid.UUID(tag_id)
    service = _get_service()
    return service.get_by_id(utag_id)


@elapsed_time()
@with_spinner("Updating tag...")
def _update_tag(tag_id: str, update_data: TagUpdate) -> TagRead:  # [AI GENERATED] TagRead
    utag_id = uuid.UUID(tag_id)
    service = _get_service()
    return service.update(utag_id, update_data)


@elapsed_time()
@with_spinner("Deleting tag...")
def _delete_tag(tag_id: str) -> bool:  # [AI GENERATED]
    utag_id = uuid.UUID(tag_id)
    service = _get_service()
    return service.delete(utag_id)


@app.command("list", help="全タグ一覧")
@handle_cli_errors()
def list_tags() -> None:
    """全タグを一覧表示するコマンド [AI GENERATED]"""
    tags = _get_all_tags()
    table = Table(title="Tags", box=box.SIMPLE, caption=f"Total: {len(tags.result)} Elapsed: {tags.elapsed:.2f}s")
    table.add_column("ID")
    table.add_column("Name")
    for t in tags.result:
        table.add_row(str(t.id), t.name)
    console.print(table)


@app.command("create", help="タグ作成")
@handle_cli_errors()
def create_tag(name: str | None = typer.Option(None, "--name", "-n")) -> None:
    """新しいタグを作成するコマンド [AI GENERATED]

    Args:
        name: タグ名 (未指定なら対話入力)
    """
    if name is None:
        name = questionary.text("Tag name?").ask()
    if name is None:
        msg = "name 必須"
        raise typer.BadParameter(msg)
    created = _create_tag(name=name)
    console.print(
        f"[green]Created:[/green] {created.result.name} ({created.result.id}) Elapsed: {created.elapsed:.2f}s"
    )


@app.command("search", help="名前部分一致")
@handle_cli_errors()
def search_tags(query: str) -> None:
    """タグ名の部分一致検索を行うコマンド [AI GENERATED]

    Args:
        query: 検索語
    """
    results = _search_tags(query=query)
    if not results.result:
        console.print("[yellow]No results[/yellow]")
        raise typer.Exit(code=0)
    table = Table(
        title=f"Search: {query}",
        box=box.SIMPLE,
        # caption=f"Hits: {len(results.result)} Elapsed: {results.elapsed:.2f}s",
    )
    table.add_column("ID")
    table.add_column("Name")
    # for t in results.result:
    #    table.add_row(str(t.id), t.name)
    console.print(table)


@app.command("get", help="ID取得")
@handle_cli_errors()
def get_tag(tag_id: str) -> None:
    """ID 指定でタグ詳細を取得するコマンド [AI GENERATED]

    Args:
        tag_id: タグ UUID 文字列
    """
    tag = _get_tag(tag_id)
    if tag.result is None:
        console.print("[yellow]Not found[/yellow]")
        raise typer.Exit(code=1)
    table = Table(title="Tag Detail", box=box.MINIMAL_DOUBLE_HEAD, caption=f"Elapsed: {tag.elapsed:.2f}s")
    table.add_column("Field")
    table.add_column("Value")
    table.add_row("ID", str(tag.result.id))
    table.add_row("Name", tag.result.name)
    console.print(table)


@app.command("update", help="タグ名変更")
@handle_cli_errors()
def update_tag(tag_id: str, name: str | None = typer.Option(None, "--name", "-n")) -> None:
    """タグ名を変更するコマンド [AI GENERATED]

    Args:
        tag_id: タグ UUID
        name: 新しいタグ名
    """
    if name is None:
        name = questionary.text("New name?").ask()
    if name is None:
        console.print("[yellow]Cancelled[/yellow]")
        raise typer.Exit(code=1)
    updated = _update_tag(tag_id, update_data=TagUpdate(name=name))
    console.print(f"[green]Updated:[/green] {updated.result.name} Elapsed: {updated.elapsed:.2f}s")


@app.command("delete", help="タグ削除")
@handle_cli_errors()
def delete_tag(tag_id: str, force: bool = typer.Option(default=False, help="関連があっても削除")) -> None:
    """タグを削除するコマンド [AI GENERATED]

    Args:
        tag_id: 削除対象 UUID
        force: 確認を省略するか
    """
    if (not force) and (not questionary.confirm("Delete this tag?").ask()):
        console.print("[yellow]Cancelled[/yellow]")
        raise typer.Exit(code=1)
    deleted = _delete_tag(tag_id)
    console.print(f"[red]Deleted:[/red] {tag_id} Elapsed: {deleted.elapsed:.2f}s")
