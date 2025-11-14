"""Settings CLI commands.

設定の表示と更新用コマンド。
"""

from __future__ import annotations

import contextlib
from typing import TYPE_CHECKING

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.tree import Tree

from cli.utils import elapsed_time, handle_cli_errors, with_spinner

if TYPE_CHECKING:  # import grouping for type checking only
    from typing import Any

    from logic.application.settings_application_service import SettingsApplicationService
    from settings.models import (
        AgentsSettings,
        AppSettings,
        DatabaseSettings,
        UserSettings,
        WindowSettings,
    )

app = typer.Typer(help="設定の表示と更新")
console = Console()


def _get_service() -> SettingsApplicationService:
    from logic.application.apps import ApplicationServices

    # Use ApplicationServices container to obtain the shared SettingsApplicationService
    return ApplicationServices.create().settings


# ==== Helpers ====
@elapsed_time()
@with_spinner("Fetching all settings...")
def _get_all_settings() -> AppSettings:
    service = _get_service()
    return service.get_all_settings()


@elapsed_time()
@with_spinner("Fetching window settings...")
def _get_window_settings() -> WindowSettings:
    service = _get_service()
    return service.get_window_settings()


@elapsed_time()
@with_spinner("Fetching user settings...")
def _get_user_settings() -> UserSettings:
    service = _get_service()
    return service.get_user_settings()


@elapsed_time()
@with_spinner("Fetching database settings...")
def _get_database_settings() -> DatabaseSettings:
    service = _get_service()
    return service.get_database_settings()


@elapsed_time()
@with_spinner("Fetching agents settings...")
def _get_agents_settings() -> AgentsSettings:
    service = _get_service()
    return service.get_agents_settings()


@elapsed_time()
@with_spinner("Fetching setting...")
def _get_setting(query: str | Any) -> Any:  # noqa: ANN401
    service = _get_service()
    # Accept either a GetSettingQuery-like object or a raw path string
    path = getattr(query, "path", query)
    return service.get_setting(path)


@elapsed_time()
@with_spinner("Updating window settings...")
def _update_window_settings(size: list[int] | None, position: list[int] | None) -> WindowSettings:
    """Update window settings via service helper.

    Args:
        size: [width, height] list or None
        position: [x, y] list or None

    Returns:
        Updated WindowSettings
    """
    service = _get_service()
    return service.update_window_settings(size=size or [], position=position or [])


@elapsed_time()
@with_spinner("Updating user settings...")
def _update_user_settings(last_login_user: str | None, theme: str | None, user_name: str | None) -> UserSettings:
    service = _get_service()
    return service.update_user_settings(
        last_login_user=last_login_user or "",
        theme=theme or "",
        user_name=user_name or "",
    )


@elapsed_time()
@with_spinner("Updating database settings...")
def _update_database_settings(url: str) -> DatabaseSettings:
    service = _get_service()
    return service.update_database_settings(url=url)


@elapsed_time()
@with_spinner("Updating setting...")
def _update_setting(path: str, value: Any) -> Any:  # noqa: ANN401
    service = _get_service()
    return service.update_setting(path=path, value=value)


def _render_settings_tree(settings: AppSettings) -> Tree:
    """設定をツリー形式で表示

    Args:
        settings: アプリケーション設定

    Returns:
        Rich Treeオブジェクト
    """
    tree = Tree("[bold cyan]アプリケーション設定[/bold cyan]")

    # Window settings
    window_branch = tree.add("[bold yellow]Window[/bold yellow]")
    window_branch.add(f"size: {settings.window.size}")
    window_branch.add(f"position: {settings.window.position}")

    # User settings
    user_branch = tree.add("[bold yellow]User[/bold yellow]")
    user_branch.add(f"last_login_user: {settings.user.last_login_user}")
    user_branch.add(f"theme: {settings.user.theme}")
    user_branch.add(f"user_name: {settings.user.user_name}")

    # Database settings
    db_branch = tree.add("[bold yellow]Database[/bold yellow]")
    db_branch.add(f"url: {settings.database.url}")

    # Agents settings
    agents_branch = tree.add("[bold yellow]Agents[/bold yellow]")
    agents_branch.add(f"provider: {settings.agents.provider}")
    agents_branch.add(f"huggingface: {settings.agents.huggingface}")
    agents_branch.add(f"gemini: {settings.agents.gemini}")

    return tree


# ==== Commands ====
@app.command("show", help="全設定を表示")
@handle_cli_errors()
def show_all() -> None:
    """全設定をツリー形式で表示"""
    result = _get_all_settings()

    tree = _render_settings_tree(result.result)
    console.print(tree)
    console.print(f"\n[dim]Elapsed: {result.elapsed:.2f}s[/dim]")


@app.command("get", help="特定の設定値を取得")
@handle_cli_errors()
def get_setting(
    path: str = typer.Argument(..., help="設定パス (例: user.theme, window.size)"),
) -> None:
    """特定の設定値を取得して表示

    Args:
        path: ドット区切りの設定パス
    """
    result = _get_setting(path)

    console.print(
        Panel.fit(
            f"[bold]{path}[/bold]\n\n[green]{result.result}[/green]",
            title="Setting Value",
            border_style="cyan",
        )
    )
    console.print(f"\n[dim]Elapsed: {result.elapsed:.2f}s[/dim]")


@app.command("set", help="特定の設定値を更新")
@handle_cli_errors()
def set_setting(
    path: str = typer.Argument(..., help="設定パス (例: user.theme, window.size)"),
    value: str = typer.Argument(..., help="設定する値"),
) -> None:
    """特定の設定値を更新

    Args:
        path: ドット区切りの設定パス
        value: 設定する値（JSON形式も可）
    """
    from json import JSONDecodeError, loads

    # Try to parse value as JSON (for lists, dicts, etc.)
    parsed_value: Any = value
    with contextlib.suppress(JSONDecodeError):
        parsed_value = loads(value)

    # Call helper directly with raw args to avoid depending on missing command types
    result = _update_setting(path, parsed_value)

    console.print(f"[green]✓[/green] Updated [bold]{path}[/bold] = [cyan]{result.result}[/cyan]")
    console.print(f"[dim]Elapsed: {result.elapsed:.2f}s[/dim]")


@app.command("window", help="ウィンドウ設定を表示")
@handle_cli_errors()
def show_window() -> None:
    """ウィンドウ設定を表示"""
    result = _get_window_settings()

    table = Table(title="Window Settings", caption=f"Elapsed: {result.elapsed:.2f}s")
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("size", str(result.result.size))
    table.add_row("position", str(result.result.position))

    console.print(table)


@app.command("user", help="ユーザー設定を表示")
@handle_cli_errors()
def show_user() -> None:
    """ユーザー設定を表示"""
    result = _get_user_settings()

    table = Table(title="User Settings", caption=f"Elapsed: {result.elapsed:.2f}s")
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("last_login_user", str(result.result.last_login_user))
    table.add_row("theme", result.result.theme)
    table.add_row("user_name", result.result.user_name)

    console.print(table)


@app.command("database", help="データベース設定を表示")
@handle_cli_errors()
def show_database() -> None:
    """データベース設定を表示"""
    result = _get_database_settings()

    console.print(
        Panel.fit(
            f"[bold]Database URL[/bold]\n\n[green]{result.result.url}[/green]",
            title="Database Settings",
            border_style="cyan",
        )
    )
    console.print(f"\n[dim]Elapsed: {result.elapsed:.2f}s[/dim]")


@app.command("agents", help="エージェント設定を表示")
@handle_cli_errors()
def show_agents() -> None:
    """エージェント設定を表示"""
    result = _get_agents_settings()

    table = Table(title="Agents Settings", caption=f"Elapsed: {result.elapsed:.2f}s")
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("provider", str(result.result.provider))
    table.add_row("huggingface", str(result.result.huggingface))
    table.add_row("gemini", str(result.result.gemini))

    console.print(table)


@app.command("update-window", help="ウィンドウ設定を更新")
@handle_cli_errors()
def update_window(
    size: str | None = typer.Option(None, "--size", help="ウィンドウサイズ [幅,高さ] (例: 1920,1080)"),
    position: str | None = typer.Option(None, "--position", help="ウィンドウ位置 [X,Y] (例: 100,100)"),
) -> None:
    """ウィンドウ設定を更新

    Args:
        size: カンマ区切りのサイズ
        position: カンマ区切りの位置
    """
    size_list: list[int] | None = None
    position_list: list[int] | None = None

    if size:
        size_list = [int(x.strip()) for x in size.split(",")]
    if position:
        position_list = [int(x.strip()) for x in position.split(",")]

    if size_list is None and position_list is None:
        console.print("[yellow]No changes specified[/yellow]")
        return

    # Call helper directly with parsed lists
    result = _update_window_settings(size_list, position_list)

    console.print("[green]✓[/green] Window settings updated")
    console.print(f"  size: {result.result.size}")
    console.print(f"  position: {result.result.position}")
    console.print(f"[dim]Elapsed: {result.elapsed:.2f}s[/dim]")


@app.command("update-user", help="ユーザー設定を更新")
@handle_cli_errors()
def update_user(
    theme: str | None = typer.Option(None, "--theme", help="テーマ (light/dark)"),
    user_name: str | None = typer.Option(None, "--user-name", help="ユーザー名"),
    last_login: str | None = typer.Option(None, "--last-login", help="最終ログインユーザー"),
) -> None:
    """ユーザー設定を更新

    Args:
        theme: UIテーマ
        user_name: ユーザー表示名
        last_login: 最終ログインユーザー
    """
    if theme is None and user_name is None and last_login is None:
        console.print("[yellow]No changes specified[/yellow]")
        return

    # Call helper directly with raw values
    result = _update_user_settings(last_login, theme, user_name)

    console.print("[green]✓[/green] User settings updated")
    console.print(f"  theme: {result.result.theme}")
    console.print(f"  user_name: {result.result.user_name}")
    console.print(f"  last_login_user: {result.result.last_login_user}")
    console.print(f"[dim]Elapsed: {result.elapsed:.2f}s[/dim]")


@app.command("update-database", help="データベース設定を更新")
@handle_cli_errors()
def update_database(
    url: str = typer.Argument(..., help="データベース接続URL"),
) -> None:
    """データベース設定を更新

    Args:
        url: データベース接続URL
    """
    # Call helper directly with raw url
    result = _update_database_settings(url)

    console.print(f"[green]✓[/green] Database URL updated: {result.result.url}")
    console.print(f"[dim]Elapsed: {result.elapsed:.2f}s[/dim]")
