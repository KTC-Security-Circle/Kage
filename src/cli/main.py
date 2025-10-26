"""Typer application instance.

The CLI is intentionally minimal for now. Additional command modules should
register themselves by importing and attaching to the `app` object here.
"""

from __future__ import annotations

import typer
from rich.console import Console
from rich.panel import Panel

from cli.commands import (
    # agent,  # 新規エージェントコマンド
    memo,
    # project,
    # settings,
    # tag,
    # task,
    # task_qa,  # 新規クイックアクションコマンド
    # task_status,  # 新規ステータス/ボード表示コマンド
    # task_tag,
)

app = typer.Typer(help="Kage project command line interface", invoke_without_command=True)
console = Console()

# app.add_typer(project.app, name="project")
# app.add_typer(task.app, name="task")
# app.add_typer(tag.app, name="tag")
# app.add_typer(task_tag.app, name="task-tag")
app.add_typer(memo.app, name="memo")
# app.add_typer(task_qa.app, name="task-qa")
# app.add_typer(task_status.app, name="task-status")
# app.add_typer(agent.app, name="agent")
# app.add_typer(settings.app, name="settings")


@app.callback()
def top_level_default(ctx: typer.Context) -> None:
    """kage-cli: A simple CLI tool.

    サブコマンドが指定されない場合は、デフォルトのトップアクセス（例：ヘルプ表示）を実行します。
    """
    if ctx.invoked_subcommand is None:
        # Display welcome message and basic help
        # 使用できるコマンドの一覧を表示する
        commands = [f"- {cmd.name}" for cmd in app.registered_groups]

        console.print(
            Panel.fit(
                (
                    "\n[bold green]🚀 Welcome to kage-cli! 🚀[/bold green]\n"
                    "[dim]Welcome to the Kage CLI prototype.[/dim]\n\n"
                    "Try 'kage-cli --help' to see available commands.\n\n\n"
                    "Available commands:\n" + "\n".join(commands) + "\n\n"
                    "[dim]Use 'kage-cli <command> --help' for more information on a command.[/dim]\n"
                ),
                title="kage-cli",
                border_style="cyan",
            )
        )


if __name__ == "__main__":
    app()
