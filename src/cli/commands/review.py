"""Weekly review insights CLI commands."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from cli.utils import handle_cli_errors
from logic.application.review_application_service import WeeklyReviewApplicationService

if TYPE_CHECKING:  # pragma: no cover
    from models import WeeklyReviewInsights
else:  # pragma: no cover
    WeeklyReviewInsights = object

app = typer.Typer(help="週次レビューのインサイト取得コマンド")
_console = Console()

PROJECT_ID_OPTION = typer.Option(
    [],
    "--project-id",
    help="対象プロジェクトID (複数指定可)",
)


def _parse_datetime(value: str | None, param_name: str) -> datetime | None:
    if value is None:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError as exc:  # pragma: no cover - typer handles in CLI context
        message = f"{param_name} は ISO8601 形式で指定してください"
        raise typer.BadParameter(message) from exc


def _parse_uuid_list(values: list[str]) -> list[UUID]:
    parsed: list[UUID] = []
    for raw in values:
        try:
            parsed.append(UUID(raw))
        except ValueError as exc:  # pragma: no cover
            message = f"project-id の値 {raw} は UUID 形式ではありません"
            raise typer.BadParameter(message) from exc
    return parsed


@app.command("insights")
@handle_cli_errors()
def generate_insights(
    start: str | None = typer.Option(None, help="集計期間の開始 (ISO8601)"),
    end: str | None = typer.Option(None, help="集計期間の終了 (ISO8601)"),
    zombie_threshold: int | None = typer.Option(None, help="ゾンビ判定日数を上書き"),
    project_id: list[str] = PROJECT_ID_OPTION,
    user_id: str | None = typer.Option(None, help="レビュー実行ユーザーID (UUID)"),
) -> None:
    """週次レビューのAIインサイトを生成し、コンソールに表示する。"""
    start_dt = _parse_datetime(start, "start")
    end_dt = _parse_datetime(end, "end")
    project_ids = _parse_uuid_list(project_id)
    user_uuid = UUID(user_id) if user_id else None

    service = WeeklyReviewApplicationService()
    insights = service.fetch_insights(
        start=start_dt,
        end=end_dt,
        zombie_threshold_days=zombie_threshold,
        project_ids=project_ids or None,
        user_id=user_uuid,
    )
    _render_insights(insights)


def _render_insights(insights: WeeklyReviewInsights) -> None:
    meta = insights.metadata
    _console.print(
        Panel.fit(
            f"期間: {meta.period.start:%Y-%m-%d} ~ {meta.period.end:%Y-%m-%d}\n"
            f"ゾンビ閾値: {meta.zombie_threshold_days}日\n"
            f"対象プロジェクト: {len(meta.project_filters) or '全件'}",
            title="Weekly Review",
            border_style="cyan",
        )
    )
    _render_highlights(insights)
    _render_zombies(insights)
    _render_memo_audits(insights)


def _render_highlights(insights: WeeklyReviewInsights) -> None:
    payload = insights.highlights
    title = "成果サマリー"
    if payload.status == "fallback" and payload.fallback_message:
        _console.print(Panel(payload.fallback_message, title=title, border_style="yellow"))
        return
    table = Table(title=title, border_style="green")
    table.add_column("タイトル", style="bold")
    table.add_column("説明")
    for item in payload.items:
        table.add_row(item.title, item.description)
    _console.print(Panel.fit(payload.intro or "", border_style="green"))
    _console.print(table)


def _render_zombies(insights: WeeklyReviewInsights) -> None:
    payload = insights.zombie_tasks
    title = "ゾンビタスク提案"
    if payload.status == "fallback" and payload.fallback_message:
        _console.print(Panel(payload.fallback_message, title=title, border_style="yellow"))
        return
    table = Table(title=title, border_style="magenta")
    table.add_column("タスク")
    table.add_column("停滞日数", justify="right")
    table.add_column("提案")
    for task in payload.tasks:
        suggestions = "\n".join(f"- {s.action}: {s.rationale}" for s in task.suggestions)
        table.add_row(task.title, str(task.stale_days), suggestions or "提案なし")
    _console.print(table)


def _render_memo_audits(insights: WeeklyReviewInsights) -> None:
    payload = insights.memo_audits
    title = "未処理メモ棚卸し"
    if payload.status == "fallback" and payload.fallback_message:
        _console.print(Panel(payload.fallback_message, title=title, border_style="yellow"))
        return
    table = Table(title=title, border_style="blue")
    table.add_column("要約")
    table.add_column("提案")
    table.add_column("メッセージ")
    for audit in payload.audits:
        table.add_row(audit.summary, audit.recommended_route, audit.guidance)
    _console.print(table)
