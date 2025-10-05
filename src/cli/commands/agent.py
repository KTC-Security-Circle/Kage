"""Agent related CLI commands.

OneLinerService を用いた一言コメント生成と結果タスク保存。
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import questionary
import typer
from rich.console import Console
from rich.panel import Panel

from agents.agent_conf import HuggingFaceModel, LLMProvider
from cli.utils import elapsed_time, handle_cli_errors, with_spinner

if TYPE_CHECKING:  # pragma: no cover
    from logic.application.one_liner_application_service import OneLinerApplicationService
    from logic.queries.one_liner_queries import OneLinerContext

app = typer.Typer(help="エージェント (one-liner) コマンド")


def _unsupported_openvino_model(model: str) -> None:  # [AI GENERATED]
    """OpenVINO モデル未対応例外を発生させるヘルパー [AI GENERATED]"""
    msg = f"Unsupported OpenVINO model: {model}"  # [AI GENERATED]
    raise typer.BadParameter(msg)  # [AI GENERATED]


# Typer Option definitions (lint 対応: デフォルト評価を関数外で実行)
PROVIDER_OPT = typer.Option(None, help="LLM プロバイダー上書き (fake/google/openvino)")
MODEL_OPT = typer.Option(None, help="モデル名上書き。OPENVINO: Enum 名/値, GOOGLE: 文字列")
STATUS_OPT = typer.Option("inbox", help="タスクステータス (inbox/todo/doing/done 等)")
INTERACTIVE_OPT = typer.Option(
    None,
    "--interactive",
    "-i",
    help="手動入力 (questionary) でコンテキストを指定",
)
console = Console()


def _resolve_provider_model(
    provider: LLMProvider | None, model: str | None
) -> tuple[LLMProvider | None, HuggingFaceModel | str | None]:  # [AI GENERATED]
    """プロバイダ/モデル文字列を解決し型を揃えるヘルパー [AI GENERATED]"""
    resolved_provider: LLMProvider | None = provider
    resolved_model: HuggingFaceModel | str | None = None

    if resolved_provider is None and model:
        if model in HuggingFaceModel.__members__:
            resolved_provider = LLMProvider.OPENVINO
            resolved_model = HuggingFaceModel[model]
        else:
            enum_match = next((m for m in HuggingFaceModel if m.value == model), None)
            if enum_match:
                resolved_provider = LLMProvider.OPENVINO
                resolved_model = enum_match
            else:
                resolved_provider = LLMProvider.GOOGLE
                resolved_model = model
    elif resolved_provider == LLMProvider.OPENVINO and model:
        if model in HuggingFaceModel.__members__:
            resolved_model = HuggingFaceModel[model]
        else:
            enum_match = next((m for m in HuggingFaceModel if m.value == model), None)
            if enum_match is None:
                _unsupported_openvino_model(model)
            resolved_model = enum_match
    elif resolved_provider == LLMProvider.GOOGLE:
        resolved_model = model
    # FAKE / 未指定は resolved_model None のまま

    return resolved_provider, resolved_model


def _get_one_liner_service(
    provider: LLMProvider | None = None, model: str | None = None
) -> OneLinerApplicationService:  # [AI GENERATED]
    """OneLinerApplicationService インスタンスを取得 (設定を書き換えない) [AI GENERATED]"""
    from logic.application.one_liner_application_service import OneLinerApplicationService

    if provider is None and model is None:
        return OneLinerApplicationService()
    try:
        resolved_provider, resolved_model = _resolve_provider_model(provider, model)
    except typer.BadParameter:
        raise
    except Exception as e:  # pragma: no cover
        raise typer.BadParameter(str(e)) from e
    return OneLinerApplicationService(provider=resolved_provider, model_name=resolved_model)


@with_spinner("Building context...")
def _build_context_auto() -> OneLinerContext:  # [AI GENERATED]
    from logic.queries.one_liner_queries import build_one_liner_context_auto

    return build_one_liner_context_auto()


def _build_context_interactive() -> OneLinerContext:  # [AI GENERATED]
    """Questionary を用いて手動でカウント値を入力しコンテキスト構築 [AI GENERATED]"""
    today = int(questionary.text("today_task_count?", default="0").ask() or 0)
    completed = int(questionary.text("completed_task_count?", default="0").ask() or 0)
    overdue = int(questionary.text("overdue_task_count?", default="0").ask() or 0)
    from logic.queries.one_liner_queries import build_one_liner_context

    return build_one_liner_context(
        today_task_count=today,
        completed_task_count=completed,
        overdue_task_count=overdue,
    )


def _interactive_select_provider_model() -> tuple[LLMProvider | None, str | None]:  # [AI GENERATED]
    """対話的に provider / model を選択し適用有無を確認する [AI GENERATED]

    Returns:
        tuple[LLMProvider|None, str|None]: 適用が確認された場合は provider / model。適用しない場合は (None, None)
    """
    # Provider 選択
    provider_value = questionary.select("Provider?", choices=[p.value for p in LLMProvider]).ask()
    if provider_value is None:  # ユーザーキャンセル
        return None, None
    provider: LLMProvider = LLMProvider(provider_value)

    model: str | None = None
    if provider == LLMProvider.OPENVINO:
        # OpenVINO 用 HuggingFaceModel 選択 (Enum 名を渡す)
        model_choice = questionary.select("OpenVINO model?", choices=[m.name for m in HuggingFaceModel]).ask()
        if model_choice is None:
            return None, None
        model = model_choice
    elif provider == LLMProvider.GOOGLE:
        # 既定値を設定から取り出し editable で入力
        try:
            from settings.manager import get_config_manager  # 遅延 import

            default_google = get_config_manager().settings.agents.gemini.one_liner
        except Exception:  # pragma: no cover - 設定読み込み失敗時は空
            default_google = "gemini-2.0-flash"
        model_input = questionary.text("Google model?", default=str(default_google or "")).ask()
        if model_input:
            model = model_input.strip() or None
    else:
        # FAKE は model 不要
        model = None

    apply_override = questionary.confirm(
        f"この provider/model [{provider}, {model}] を適用しますか? (No: 既定設定を使用)", default=True
    ).ask()
    if not apply_override:
        return None, None
    return provider, model


@elapsed_time()
@with_spinner("Generating one-liner...")
def _generate_one_liner(
    ctx: OneLinerContext,
    provider: LLMProvider | None = None,
    model: str | None = None,
) -> str:  # [AI GENERATED] TimingResult[str]
    """One-liner 生成 (TimingResult[str] 相当オブジェクトを返却) [AI GENERATED]"""
    service = _get_one_liner_service(provider=provider, model=model)
    from logic.application.one_liner_application_service import OneLinerContext

    if isinstance(ctx, OneLinerContext):
        return service.generate_one_liner(ctx)
    return service.generate_one_liner()


def _print_one_liner(
    text: str,
    elapsed: float,
    *,
    provider: LLMProvider | None = None,
    model: str | HuggingFaceModel | None = None,
    ctx: OneLinerContext | None = None,
) -> None:  # [AI GENERATED]
    """結果表示用ヘルパー (Provider/Model/Context 情報付き) [AI GENERATED]

    Args:
        text: 生成テキスト
        elapsed: 経過秒数
        provider: 実際に使用した Provider
        model: 使用モデル (文字列または Enum)
        ctx: コンテキスト (件数表示用)
    """
    meta_parts: list[str] = []
    if provider:
        meta_parts.append(f"provider={provider.value}")
    if model:
        # Enum の場合は name を優先表示
        if isinstance(model, HuggingFaceModel):
            meta_parts.append(f"model={model.name}")
        else:
            meta_parts.append(f"model={model}")
    if ctx is not None:
        meta_parts.append(f"counts(t={ctx.today_task_count},c={ctx.completed_task_count},o={ctx.overdue_task_count})")
    caption = f"[dim]elapsed={elapsed:.2f}s | "
    caption += " | ".join(meta_parts) if meta_parts else ""
    caption += "[/dim]"
    console.print(
        Panel.fit(
            f"[bold cyan]{text}[/bold cyan]\n\n{caption}",
            title="One-Liner",
            border_style="cyan",
        )
    )


@app.command("run", help="一言コメント生成 (自動コンテキスト専用)")
@handle_cli_errors()
def run_one_liner(
    *,
    provider: LLMProvider | None = PROVIDER_OPT,
    model: str | None = MODEL_OPT,
    interactive: bool = INTERACTIVE_OPT,
) -> None:  # [AI GENERATED]
    """OneLiner を生成して表示するコマンド [AI GENERATED]"""
    if interactive:
        sel_provider, sel_model = _interactive_select_provider_model()
        if sel_provider is not None:
            provider = sel_provider
            model = sel_model
        skip_counts = questionary.confirm("タスク件数入力をスキップして自動集計しますか?", default=True).ask()
        ctx = _build_context_auto() if skip_counts else _build_context_interactive()
    else:
        ctx = _build_context_auto()
    gen_res = _generate_one_liner(ctx, provider=provider, model=model)
    _print_one_liner(
        gen_res.result,
        gen_res.elapsed,
        provider=provider,
        model=model,
        ctx=ctx,
    )


@app.command("save-task", help="生成した一言をタスクとして保存")
@handle_cli_errors()
def save_one_liner_as_task(
    *,
    status: str = STATUS_OPT,
    provider: LLMProvider | None = PROVIDER_OPT,
    model: str | None = MODEL_OPT,
    interactive: bool = INTERACTIVE_OPT,
) -> None:  # [AI GENERATED]
    if interactive:
        sel_provider, sel_model = _interactive_select_provider_model()
        if sel_provider is not None:
            provider = sel_provider
            model = sel_model
        skip_counts = questionary.confirm("タスク件数入力をスキップして自動集計しますか?", default=True).ask()
        ctx = _build_context_auto() if skip_counts else _build_context_interactive()
    else:
        ctx = _build_context_auto()
    gen_res = _generate_one_liner(ctx, provider=provider, model=model)
    text = gen_res.result
    from logic.application.task_application_service import TaskApplicationService
    from logic.commands.task_commands import CreateTaskCommand
    from logic.container import service_container
    from models import TaskStatus

    try:
        task_status = TaskStatus(status)
    except ValueError:  # [AI GENERATED]
        task_status = TaskStatus.INBOX  # [AI GENERATED]
    service = service_container.get_service(TaskApplicationService)
    truncated = text[:60]
    cmd = CreateTaskCommand(title=truncated, description=text, status=task_status)
    created = service.create_task(cmd)
    _print_one_liner(
        text,
        gen_res.elapsed,
        provider=provider,
        model=model,
        ctx=ctx,
    )
    console.print(f"[green]Saved task:[/green] {created.title}")


__all__ = ["app"]
