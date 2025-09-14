"""Typer application instance.

The CLI is intentionally minimal for now. Additional command modules should
register themselves by importing and attaching to the `app` object here.
"""

from __future__ import annotations

import typer
from rich.console import Console
from rich.panel import Panel

from cli.commands import project, tag, task

app = typer.Typer(help="Kage project command line interface", invoke_without_command=True)
console = Console()


@app.callback()
def top_level_default(ctx: typer.Context) -> None:
    """kage-cli: A simple CLI tool.

    サブコマンドが指定されない場合は、デフォルトのトップアクセス（例：ヘルプ表示）を実行します。
    """
    if ctx.invoked_subcommand is None:
        console.print(
            Panel.fit(
                (
                    "\n\n[bold green]🚀 Welcome to kage-cli! 🚀[/bold green]\n"
                    "[dim]Welcome to the Kage CLI prototype.[/dim]\n\n\n"
                    "Try 'kage-cli --help' to see available commands."
                ),
                title="kage-cli",
                border_style="cyan",
            )
        )


# app.add_typer(hello.app, name="hello", help="Print a friendly greeting")
app.add_typer(project.app, name="project")
app.add_typer(task.app, name="task")
app.add_typer(tag.app, name="tag")

if __name__ == "__main__":
    app()
