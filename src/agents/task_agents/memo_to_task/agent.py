"""メモをタスク案へ変換するエージェント。"""

from __future__ import annotations

from collections.abc import Callable
from copy import deepcopy
from itertools import chain
from typing import TYPE_CHECKING, cast

from langgraph.graph import END, START, StateGraph
from pydantic import ValidationError

from agents.base import AgentError, BaseAgent, KwargsAny
from agents.task_agents.memo_to_task.prompt import (
    classification_prompt,
    project_plan_prompt,
    quick_action_prompt,
    responsibility_prompt,
    schedule_prompt,
    task_seed_prompt,
)
from agents.task_agents.memo_to_task.schema import (
    MemoClassification,
    MemoProcessingDecision,
    MemoToTaskAgentOutput,
    ProjectPlanSuggestion,
    QuickActionAssessment,
    ResponsibilityAssessment,
    ScheduleAssessment,
    TaskDraft,
    TaskDraftSeed,
    TaskPriority,
    TaskRoute,
    is_iso8601_string,
)
from agents.task_agents.memo_to_task.state import MemoToTaskResult, MemoToTaskState
from agents.utils import LLMProvider, agents_logger

if TYPE_CHECKING:
    from collections.abc import Callable

    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.runnables import RunnableSerializable
    from pydantic import BaseModel

    from models import MemoRead


QUICK_ACTION_THRESHOLD_MINUTES = 2

VALID_TASK_ROUTES: set[TaskRoute] = {"progress", "waiting", "calendar", "next_action"}
VALID_TASK_PRIORITIES: set[TaskPriority] = {"low", "normal", "high"}


_DEFAULT_FAKE_RESPONSES: list[MemoToTaskAgentOutput] = [
    MemoToTaskAgentOutput(
        tasks=[
            TaskDraft(
                title="牛乳を買う",
                description="近所のスーパーで本日購入",
                route="progress",
                tags=["買い物"],
                due_date="",
            ),
            TaskDraft(
                title="予算案を仕上げる",
                description="今週中にドラフトをまとめる",
                route="next_action",
                tags=["仕事"],
            ),
        ],
        suggested_memo_status="active",
    ),
    MemoToTaskAgentOutput(
        tasks=[
            TaskDraft(
                title="金曜までにレポートを提出",
                description="上長にメールで送付",
                due_date="2025-10-31",
                route="calendar",
                tags=["レポート"],
            )
        ],
        suggested_memo_status="active",
    ),
    MemoToTaskAgentOutput(tasks=[], suggested_memo_status="idea"),
]


def _fake_classification_factory(params: dict[str, object]) -> MemoClassification:
    memo_text = str(params.get("memo_text", ""))
    lowered = memo_text.lower()
    if "プロジェクト" in memo_text or "project" in lowered:
        return MemoClassification(
            decision="project",
            reason="キーワードからプロジェクトと判断",
            project_title="プロジェクト",
        )
    if "アイデア" in memo_text or "idea" in lowered:
        return MemoClassification(decision="idea", reason="アイデア的な記録", project_title=None)
    return MemoClassification(decision="task", reason="単一タスクとして処理可能", project_title=None)


def _fake_seed_factory(params: dict[str, object]) -> TaskDraftSeed:
    memo_text = str(params.get("memo_text", ""))
    stripped_text = memo_text.strip()
    lines = [line for line in memo_text.splitlines() if line.strip()]
    first_line = lines[0] if lines else stripped_text
    title = first_line[:30] if first_line else "メモの整理"
    description = memo_text[:120] if stripped_text else None
    return TaskDraftSeed(title=title, description=description, tags=None)


def _fake_quick_factory(params: dict[str, object]) -> QuickActionAssessment:
    title = str(params.get("task_title", ""))
    is_quick = "確認" in title or "call" in title.lower()
    reason = "短時間で完結すると推測" if is_quick else "所要時間が不明のため標準処理"
    return QuickActionAssessment(is_quick_action=is_quick, reason=reason)


def _fake_responsibility_factory(params: dict[str, object]) -> ResponsibilityAssessment:
    description = str(params.get("task_description", "")).lower()
    should_delegate = "依頼" in description or "approval" in description
    reason = "他者への依頼が含まれる" if should_delegate else "自分で対応するのが適切"
    return ResponsibilityAssessment(should_delegate=should_delegate, reason=reason)


def _fake_schedule_factory(params: dict[str, object]) -> ScheduleAssessment:
    description = str(params.get("task_description", ""))
    requires_date = "会議" in description or "meeting" in description.lower()
    iso_value = params.get("current_datetime_iso") if requires_date else None
    due_date = iso_value if isinstance(iso_value, str) else None
    reason = "時間が指定されたイベント" if requires_date else "特定の締切は不要"
    return ScheduleAssessment(requires_specific_date=requires_date, due_date=due_date, reason=reason)


def _fake_project_factory(params: dict[str, object]) -> ProjectPlanSuggestion:
    title_hint = params.get("project_title_hint", "メモプロジェクト")
    title = str(title_hint) if isinstance(title_hint, str) else "メモプロジェクト"
    task = TaskDraft(
        title=f"{title}の次のアクション",
        description="プロジェクトを前進させる最初のステップ",
        route="next_action",
        project_title=title,
    )
    return ProjectPlanSuggestion(project_title=title, next_actions=[task])


_FAKE_SCHEMA_FACTORIES: dict[type[BaseModel], Callable[[dict[str, object]], BaseModel]] = {
    MemoClassification: _fake_classification_factory,
    TaskDraftSeed: _fake_seed_factory,
    QuickActionAssessment: _fake_quick_factory,
    ResponsibilityAssessment: _fake_responsibility_factory,
    ScheduleAssessment: _fake_schedule_factory,
    ProjectPlanSuggestion: _fake_project_factory,
}


class MemoToTaskAgent(BaseAgent[MemoToTaskState, MemoToTaskResult]):
    """メモから TaskDraft を抽出するエージェント。"""

    _name = "MemoToTaskAgent"
    _description = "自由形式メモからタスク候補を抽出する"
    _state = MemoToTaskState

    def __init__(
        self,
        provider: LLMProvider = LLMProvider.FAKE,
        *,
        persist_on_finalize: bool = False,
        **kwargs: KwargsAny,
    ) -> None:
        """エージェント初期化。

        Args:
            provider: 利用するLLMプロバイダ
            persist_on_finalize: finalize時にApplication Service経由で永続化を行うか（テスト用）
            **kwargs: 親クラス引数（model_name等）
        """
        self._persist_on_finalize = persist_on_finalize
        self._fake_response_index: int = 0
        super().__init__(provider, **kwargs)
        if provider == LLMProvider.FAKE:
            self._fake_responses = cast("list[BaseModel]", list(_DEFAULT_FAKE_RESPONSES))

    def create_graph(self, graph_builder: StateGraph) -> StateGraph:
        """エージェントの状態遷移グラフを構築する。

        このエージェントは、自由形式のメモからタスク案を導出するために
        複数の評価・生成ステップを順に実行する。ここでは各ステップをノード
        として登録し、条件分岐（エッジ）を設定している。

        成功/失敗やLLM出力の妥当性に応じて、次に進むノードが切り替わる。
        最終的には `finalize_response` で `MemoToTaskAgentOutput` を構築して終了する。

        Args:
            graph_builder: langgraph の `StateGraph` ビルダー

        Returns:
            遷移ノードとエッジを組み上げた `StateGraph` インスタンス
        """
        graph_builder.add_node("classify_memo", self._classify_memo)
        graph_builder.add_node("handle_idea", self._handle_idea)
        graph_builder.add_node("plan_project", self._plan_project)
        graph_builder.add_node("generate_task_seed", self._generate_task_seed)
        graph_builder.add_node("evaluate_quick_action", self._evaluate_quick_action)
        graph_builder.add_node("apply_quick_action", self._apply_quick_action)
        graph_builder.add_node("evaluate_responsibility", self._evaluate_responsibility)
        graph_builder.add_node("apply_delegate", self._apply_delegate)
        graph_builder.add_node("evaluate_schedule", self._evaluate_schedule)
        graph_builder.add_node("apply_schedule", self._apply_schedule)
        graph_builder.add_node("prepare_next_action", self._prepare_next_action)
        graph_builder.add_node("finalize_response", self._finalize_response)

        graph_builder.add_edge(START, "classify_memo")
        graph_builder.add_conditional_edges(
            "classify_memo",
            self._route_after_classification,
            [
                "handle_idea",
                "plan_project",
                "generate_task_seed",
                "finalize_response",
            ],
        )
        graph_builder.add_edge("handle_idea", "finalize_response")
        graph_builder.add_edge("plan_project", "finalize_response")
        graph_builder.add_edge("generate_task_seed", "evaluate_quick_action")
        graph_builder.add_conditional_edges(
            "evaluate_quick_action",
            self._route_after_quick_action,
            ["apply_quick_action", "evaluate_responsibility"],
        )
        graph_builder.add_edge("apply_quick_action", "finalize_response")
        graph_builder.add_conditional_edges(
            "evaluate_responsibility",
            self._route_after_responsibility,
            ["apply_delegate", "evaluate_schedule"],
        )
        graph_builder.add_edge("apply_delegate", "finalize_response")
        graph_builder.add_conditional_edges(
            "evaluate_schedule",
            self._route_after_schedule,
            ["apply_schedule", "prepare_next_action"],
        )
        graph_builder.add_edge("apply_schedule", "finalize_response")
        graph_builder.add_edge("prepare_next_action", "finalize_response")
        graph_builder.add_edge("finalize_response", END)

        return graph_builder

    def invoke(self, state: MemoToTaskState, thread_id: str) -> MemoToTaskResult | AgentError:
        if self.provider == LLMProvider.FAKE:
            fake_output = self.next_fake_response()
            if fake_output is not None:
                return MemoToTaskResult(
                    tasks=list(fake_output.tasks),
                    suggested_memo_status=fake_output.suggested_memo_status,
                    processed_data=self._state,
                )
        return super().invoke(state, thread_id)

    def next_fake_response(self) -> MemoToTaskAgentOutput | None:
        """FAKEプロバイダ用のプリセット応答を返す。"""
        if self.provider != LLMProvider.FAKE or not self._fake_responses:
            return None
        responses = self._fake_responses
        index = self._fake_response_index % len(responses)
        raw = deepcopy(responses[index])
        self._fake_response_index = (self._fake_response_index + 1) % len(responses)
        if not isinstance(raw, MemoToTaskAgentOutput):
            return None
        return MemoToTaskAgentOutput(
            tasks=list(raw.tasks),
            suggested_memo_status=raw.suggested_memo_status,
        )

    def _create_return_response(
        self, final_response: dict[str, KwargsAny] | KwargsAny
    ) -> MemoToTaskResult | AgentError:
        """レスポンスをReturnTypeに変換するメソッド.

        Args:
            final_response (dict[str, Any] | Any): グラフからの生のレスポンス

        Returns:
            ReturnType: 変換されたレスポンス
        """
        # BaseAgent は互換抽出を行わないため、ここで辞書から取り出す
        if isinstance(final_response, dict):
            # エラーが state に格納されていれば優先的に返す
            err = final_response.get("error")
            if isinstance(err, AgentError):
                return err
            # フォールバック: 状態辞書から最終出力を再構築する
            tasks = final_response.get("routed_tasks") or []
            suggested = final_response.get("suggested_status") or ("idea" if not tasks else "active")
            try:
                rebuilt = MemoToTaskAgentOutput(tasks=tasks, suggested_memo_status=suggested)
            except Exception:
                rebuilt = None
            if rebuilt is not None:
                final_response = rebuilt
        if isinstance(final_response, MemoToTaskAgentOutput):
            return MemoToTaskResult(
                tasks=final_response.tasks,
                suggested_memo_status=final_response.suggested_memo_status,
                processed_data=self._state,
            )
        if isinstance(final_response, AgentError):
            return final_response
        return AgentError("Invalid final response format")

    # 互換: 旧テストが monkeypatch するフック。デフォルトは None を返す。
    def _create_agent(self) -> RunnableSerializable | None:  # pragma: no cover - 互換用
        return None

    # 旧互換エントリは撤去済み

    def _get_structured_runner(
        self,
        attr_name: str,
        prompt: ChatPromptTemplate,
        schema: type[BaseModel],
    ) -> RunnableSerializable:
        """構造化出力用の実行ランナーを取得/生成する。

        指定された `attr_name` に対応するランナーが既に存在すれば再利用し、
        なければプロバイダ種別に応じて新規に構築してキャッシュする。

        - FAKE プロバイダ: 事前定義の疑似ファクトリを使うダミーRunner
        - それ以外: LLMに Pydantic スキーマの構造化出力を要求するRunner

        Args:
            attr_name: インスタンス属性名（キャッシュキー）
            prompt: 実行に用いるチャットプロンプト
            schema: 期待する構造化出力の Pydantic モデル型

        Returns:
            構造化出力を返す `RunnableSerializable` 実装
        """
        runner = getattr(self, attr_name, None)
        if runner is not None:
            return runner
        if self.provider == LLMProvider.FAKE:
            runner = self._build_fake_runner(schema)
            setattr(self, attr_name, runner)
            return runner
        structured_llm = self.get_model().with_structured_output(schema)
        runner = prompt | structured_llm
        setattr(self, attr_name, runner)
        return runner

    def _build_fake_runner(self, schema: type[BaseModel]) -> RunnableSerializable:
        """FAKEプロバイダ向けの簡易Runnerを構築する。

        スキーマに対応する疑似出力ファクトリを見つけ、`invoke(params)` で
        直接Pydanticモデルを返すシンプルなRunnerを返す。

        Args:
            schema: 期待する構造化出力の Pydantic モデル型

        Returns:
            疑似出力を返す `RunnableSerializable` 実装

        Raises:
            ValueError: 指定スキーマに対応する疑似ファクトリが未定義の場合
        """

        class _FakeRunner:
            def __init__(self, factory: Callable[[dict[str, object]], BaseModel]) -> None:
                self._factory = factory

            def invoke(self, params: dict[str, object]) -> BaseModel:
                return self._factory(params)

        factory = _FAKE_SCHEMA_FACTORIES.get(schema)
        if factory is None:
            msg = "Unsupported schema for fake runner"
            raise ValueError(msg)

        return cast("RunnableSerializable", _FakeRunner(factory))

    def _get_memo_context(self, state: MemoToTaskState) -> tuple[MemoRead | object, str, dict[str, str]]:
        """状態からメモ本文とメタデータを抽出する。"""
        memo = state.get("memo")
        memo_text = ""
        meta = {
            "memo_id": "",
            "memo_title": "",
            "memo_status": "",
        }

        if memo is None:
            return memo, memo_text, meta

        content = getattr(memo, "content", "")
        memo_text = str(content or "")

        memo_id = getattr(memo, "id", None)
        if memo_id:
            meta["memo_id"] = str(memo_id)

        title = getattr(memo, "title", "")
        meta["memo_title"] = str(title or "")

        status = getattr(memo, "status", "")
        status_value = getattr(status, "value", status)
        meta["memo_status"] = str(status_value or "")

        return memo, memo_text, meta

    def _invoke_schema_with_retry(
        self,
        runner_attr: str,
        prompt: ChatPromptTemplate,
        schema: type[BaseModel],
        base_params: dict[str, object],
        retry_hint: str,
    ) -> BaseModel | AgentError:
        """構造化出力の検証に失敗した場合に限り、1回だけ再試行する。

        1回目は `retry_hint` を空にして実行し、スキーマ検証に通れば返す。
        失敗した場合のみ、与えられた `retry_hint` を追加して2回目を実行し、
        その結果を検証して返却する。

        Args:
            runner_attr: キャッシュに用いるランナー属性名
            prompt: 実行に用いるチャットプロンプト
            schema: 期待する構造化出力の Pydantic モデル型
            base_params: プロンプトへ渡す共通パラメータ
            retry_hint: 2回目の実行時にLLMへ与える修正指示

        Returns:
            検証済みの Pydantic モデル、またはエラー出力
        """
        runner = self._get_structured_runner(runner_attr, prompt, schema)
        first_params = {**base_params, "retry_hint": ""}
        first = runner.invoke(first_params)
        validated = self.validate_output(first, schema)
        if isinstance(validated, schema):  # type: ignore[arg-type]
            return validated
        # 2回目
        second_params = {**base_params, "retry_hint": retry_hint}
        second = runner.invoke(second_params)
        return self.validate_output(second, schema)

    def _repair_classification_response(  # noqa: C901
        self,
        raw_response: object,
    ) -> MemoClassification | AgentError:
        """メモ分類の非整合な出力を可能な範囲で補正して復元する。

        LLMの出力が `MemoClassification` に合致しない場合でも、辞書形状から
        意図を推定し、`decision` や `project_title` を補うなどのヒューリスティクスで
        復旧を試みる。最終的にスキーマ検証が通らなければ `AgentError` を返す。

        Args:
            raw_response: LLM等から受け取った生の分類出力

        Returns:
            復旧済みの `MemoClassification` もしくは `AgentError`
        """
        if isinstance(raw_response, MemoClassification):
            return raw_response
        if isinstance(raw_response, dict):
            candidate: dict[str, object] = dict(raw_response)
            # Heuristic 1: project-plan shaped payload → decision 'project'
            project_shaped = "project_title" in candidate or "next_actions" in candidate
            if project_shaped and not candidate.get("decision"):
                candidate["decision"] = "project"
                if candidate.get("project_title") is None:
                    reason_text = str(candidate.get("reason", ""))
                    candidate["project_title"] = reason_text or "プロジェクト"
                candidate.setdefault("reason", "プロジェクト構造の出力から推定")
            # Heuristic 2: task-related keys imply decision 'task'
            task_hint_keys = {
                "is_quick_action",
                "should_delegate",
                "requires_specific_date",
                "title",
                "description",
                "tags",
            }
            if not candidate.get("decision") and any(k in candidate for k in task_hint_keys):
                candidate["decision"] = "task"
            if not candidate.get("decision"):
                inferred = self._infer_decision_from_reason(candidate.get("reason"))
                if inferred is not None:
                    candidate["decision"] = inferred
            candidate.setdefault("project_title", None)
            try:
                classification = MemoClassification.model_validate(candidate)
            except ValidationError as exc:
                agents_logger.warning(
                    "Failed to repair classification response. error={} raw={}",
                    str(exc),
                    candidate,
                )
            else:
                agents_logger.warning(
                    "Repaired classification output using inferred decision {}.",
                    classification.decision,
                )
                return classification
        validated = self.validate_output(raw_response, MemoClassification)
        if isinstance(validated, (MemoClassification, AgentError)):
            return validated
        # ErrorAgentOutput の場合はメッセージを AgentError に変換
        return AgentError(getattr(validated, "message", "classification validation failed"))

    @staticmethod
    def _infer_decision_from_reason(reason: object) -> MemoProcessingDecision | None:
        """理由テキストから分類方針を推定する単純なヒューリスティクス。"""
        if not isinstance(reason, str):
            return None
        normalized = reason.lower()
        if "project" in normalized or "プロジェクト" in reason:
            return "project"
        if "idea" in normalized or "アイデア" in reason or "メモ" in reason:
            return "idea"
        if "task" in normalized or "タスク" in reason or "行動" in reason:
            return "task"
        return None

    def _classify_memo(self, state: MemoToTaskState) -> dict[str, object]:
        """メモ本文の性質を分類し、後続の分岐条件を決める。

        LLMに対し `MemoClassification` の構造化出力を要求し、
        - task: 単発タスクとして処理
        - project: プロジェクト計画へ
        - idea: アイデア（保留）
        のいずれかを判断する。必要に応じて補正関数で復旧を試みる。

        Args:
            state: 現在のメモ処理状態

        Returns:
            次ノードに必要なフラグと `classification` を含む辞書。
            検証失敗時は `error` を含む。
        """
        _, memo_text, memo_meta = self._get_memo_context(state)
        runner = self._get_structured_runner("_classifier_runner", classification_prompt, MemoClassification)
        response = runner.invoke(
            {
                "memo_text": memo_text,
                **memo_meta,
                "existing_tags": state["existing_tags"],
                "current_datetime_iso": state["current_datetime_iso"],
                "retry_hint": "",
            }
        )
        classification = self._repair_classification_response(response)
        if isinstance(classification, MemoClassification):
            update: dict[str, object] = {"classification": classification}
            if classification.decision == "task":
                update["requires_action"] = True
                update["suggested_status"] = "active"
            elif classification.decision == "project":
                update["requires_project"] = True
                update["suggested_status"] = "active"
            else:
                update["requires_action"] = False
                update["suggested_status"] = "idea"
            return update
        return {"error": classification}

    def _handle_idea(self, state: MemoToTaskState) -> dict[str, object]:
        """アイデア扱いのメモをそのまま保持する。

        Args:
            state: 現在のメモ処理状態

        Returns:
            空の `routed_tasks` と `suggested_status="idea"` を含む辞書
        """
        classification = state.get("classification")
        if isinstance(classification, MemoClassification) and classification.reason:
            agents_logger.debug("IDEA判定理由: %s", classification.reason)
        return {"routed_tasks": [], "suggested_status": "idea"}

    def _plan_project(self, state: MemoToTaskState) -> dict[str, object]:
        """プロジェクト前提のメモに対し、最初のアクション群を提案する。

        LLMから `ProjectPlanSuggestion` を取得・検証し、必要に応じて
        - 出力のサニタイズ
        - リトライ（`retry_hint`付き）
        を行った上で、`next_actions` をタスク案にマッピングする。

        Args:
            state: 現在のメモ処理状態

        Returns:
            `project_plan` と `routed_tasks`、`suggested_status` を含む辞書。
            検証失敗時は `error` を含む。
        """
        classification = state.get("classification")
        if not isinstance(classification, MemoClassification):
            return {"routed_tasks": [], "suggested_status": "idea"}
        _, memo_text, memo_meta = self._get_memo_context(state)
        base_params = {
            "memo_text": memo_text,
            **memo_meta,
            "existing_tags": state["existing_tags"],
            "current_datetime_iso": state["current_datetime_iso"],
            "project_title_hint": classification.project_title or classification.reason,
        }
        runner = self._get_structured_runner("_project_plan_runner", project_plan_prompt, ProjectPlanSuggestion)
        first = runner.invoke({**base_params, "retry_hint": ""})
        suggestion = self.validate_output(first, ProjectPlanSuggestion)
        if not isinstance(suggestion, ProjectPlanSuggestion):
            # 1. サニタイズで救済
            if isinstance(first, dict):
                cleaned = self._sanitize_project_plan_payload(first)
                suggestion2 = self.validate_output(cleaned, ProjectPlanSuggestion)
                if isinstance(suggestion2, ProjectPlanSuggestion):
                    suggestion = suggestion2
                else:
                    # 2. LLM に修正指示を与えて1回だけ再試行
                    retry_hint = (
                        "出力は project_title と next_actions のみ。各 next_actions[i] の due_date は ISO8601 例: "
                        '"2025-10-25T10:00:00+09:00" または "2025-10-25"。不要なら null。route は '
                        '"next_action"|"progress"|"waiting"|"calendar" のいずれかのみ。JSON のみを出力。'
                    )
                    second = runner.invoke({**base_params, "retry_hint": retry_hint})
                    suggestion3 = self.validate_output(second, ProjectPlanSuggestion)
                    if not isinstance(suggestion3, ProjectPlanSuggestion):
                        return {"error": suggestion3}
                    suggestion = suggestion3
            else:
                # 直接リトライ
                retry_hint = (
                    "出力は project_title と next_actions のみ。各 next_actions[i] の due_date は ISO8601 例: "
                    '"2025-10-25T10:00:00+09:00" または "2025-10-25"。不要なら null。route は '
                    '"next_action"|"progress"|"waiting"|"calendar" のいずれかのみ。JSON のみを出力。'
                )
                second = runner.invoke({**base_params, "retry_hint": retry_hint})
                suggestion2 = self.validate_output(second, ProjectPlanSuggestion)
                if not isinstance(suggestion2, ProjectPlanSuggestion):
                    return {"error": suggestion2}
                suggestion = suggestion2

        tasks: list[TaskDraft] = []
        for index, task in enumerate(suggestion.next_actions or []):
            updates: dict[str, object] = {"project_title": suggestion.project_title}
            if not task.route:
                updates["route"] = "next_action" if index == 0 else "progress"
            tasks.append(task.model_copy(update=updates) if updates else task)
        if not tasks:
            tasks.append(
                TaskDraft(
                    title=f"{suggestion.project_title}の開始準備",
                    description="プロジェクトの開始に必要な最初のステップを決める",
                    route="next_action",
                    project_title=suggestion.project_title,
                )
            )

        return {
            "project_plan": suggestion,
            "routed_tasks": tasks,
            "suggested_status": "active",
            "requires_project": True,
        }

    @staticmethod
    def _is_valid_iso8601(value: str) -> bool:
        """与えられた文字列が `datetime.fromisoformat` で解釈可能か判定する。"""
        return is_iso8601_string(value)

    def _sanitize_project_plan_payload(self, raw: object) -> object:
        """LLMの出力（辞書想定）から、検証で弾かれる可能性の高い箇所をサニタイズする。

        現状の主目的は next_actions[].due_date のISO8601不備を None に落とすこと。
        あわせて無効な route は削除して Pydantic 側でデフォルトに任せる。
        """
        if not isinstance(raw, dict):
            return raw
        payload: dict[str, object] = dict(raw)
        actions = payload.get("next_actions")
        if not isinstance(actions, list):
            return payload

        cleaned_actions: list[object] = []
        for item in actions:
            if isinstance(item, dict):
                cleaned_actions.append(self._sanitize_action_dict(item))
            elif isinstance(item, TaskDraft):
                try:
                    cleaned_actions.append(self._sanitize_action_model(item))
                except Exception as exc:
                    agents_logger.warning("Sanitize action model failed: {}", str(exc))
            # サポート外の型はスキップ
        payload["next_actions"] = cleaned_actions
        return payload

    def _sanitize_action_dict(self, item: dict[str, object]) -> dict[str, object]:
        """辞書形のタスク案から、不正な期日とルート値を除去/修正する。"""
        action = dict(item)
        due = action.get("due_date")
        if isinstance(due, str) and due and not self._is_valid_iso8601(due):
            action["due_date"] = None
        route = action.get("route")
        if isinstance(route, str) and route not in VALID_TASK_ROUTES:
            action.pop("route", None)
        return action

    def _sanitize_action_model(self, item: TaskDraft) -> TaskDraft:
        """`TaskDraft` モデルのフィールドを検証し、不正値を無害化する。"""
        # Pydanticモデル(TaskDraft)が来る場合を想定
        new_item = item
        if isinstance(item.due_date, str) and item.due_date and not self._is_valid_iso8601(item.due_date):
            new_item = item.model_copy(update={"due_date": None})
        if isinstance(new_item.route, str) and new_item.route not in VALID_TASK_ROUTES:
            new_item = new_item.model_copy(update={"route": None})
        return new_item

    def _generate_task_seed(self, state: MemoToTaskState) -> dict[str, object]:
        """メモからタスク素案 `TaskDraftSeed` を生成する。

        LLMに title/description/tags の最小セットをJSONで生成させ、
        1回の再試行ロジック付きで検証を行う。

        Args:
            state: 現在のメモ処理状態

        Returns:
            `task_seed` を含む辞書。検証失敗時は `error` を返す。
        """
        _, memo_text, memo_meta = self._get_memo_context(state)
        params = {
            "memo_text": memo_text,
            **memo_meta,
            "existing_tags": state["existing_tags"],
            "current_datetime_iso": state["current_datetime_iso"],
        }
        hint = (
            "JSON 出力は title(string), description(string|null), "
            "tags(array<string>|null) のみ。余計なキーは含めないでください。"
        )
        seed = self._invoke_schema_with_retry("_task_seed_runner", task_seed_prompt, TaskDraftSeed, params, hint)
        if isinstance(seed, TaskDraftSeed):
            return {"task_seed": seed, "requires_action": True, "suggested_status": "active"}
        return {"error": seed}

    def _evaluate_quick_action(self, state: MemoToTaskState) -> dict[str, object]:
        """タスクが数分で終わる「クイックアクション」かを判定する。

        `QuickActionAssessment` の構造化出力を用い、真であれば
        以降の分岐で即時実行（`apply_quick_action`）へ誘導する。

        Args:
            state: 現在のメモ処理状態

        Returns:
            `quick_assessment` と `is_quick_action` を含む辞書。
            検証失敗時は `error` を返す。
        """
        task_context = self._get_task_context(state)
        hint = (
            "JSON 出力は is_quick_action(boolean), reason(string) のみ。"
            "project_title や next_actions などのキーは出力しないでください。"
        )
        assessment = self._invoke_schema_with_retry(
            "_quick_runner",
            quick_action_prompt,
            QuickActionAssessment,
            {**task_context},
            hint,
        )
        if isinstance(assessment, QuickActionAssessment):
            return {
                "quick_assessment": assessment,
                "is_quick_action": assessment.is_quick_action,
            }
        return {"error": assessment}

    def _apply_quick_action(self, state: MemoToTaskState) -> dict[str, object]:
        """クイックアクションとして実行可能なタスクの案を確定する。"""
        task = self._build_task_from_seed(state, {"route": "progress"})
        if task.estimate_minutes is None:
            task = task.model_copy(update={"estimate_minutes": QUICK_ACTION_THRESHOLD_MINUTES})
        return {"routed_tasks": [task], "suggested_status": "active"}

    def _evaluate_responsibility(self, state: MemoToTaskState) -> dict[str, object]:
        """委譲すべきか（自分以外に任せるべきか）を評価する。"""
        task_context = self._get_task_context(state)
        hint = "JSON 出力は should_delegate(boolean), reason(string) のみ。余計なキーは含めないでください。"
        assessment = self._invoke_schema_with_retry(
            "_responsibility_runner",
            responsibility_prompt,
            ResponsibilityAssessment,
            {**task_context},
            hint,
        )
        if isinstance(assessment, ResponsibilityAssessment):
            return {
                "responsibility_assessment": assessment,
                "should_delegate": assessment.should_delegate,
            }
        return {"error": assessment}

    def _apply_delegate(self, state: MemoToTaskState) -> dict[str, object]:
        """委譲が適切なタスクとして、`waiting` ルートに割り当てる。"""
        task = self._build_task_from_seed(state, {"route": "waiting"})
        return {"routed_tasks": [task], "suggested_status": "active"}

    def _evaluate_schedule(self, state: MemoToTaskState) -> dict[str, object]:
        """特定日時（期日）が必要かを評価し、必要なら値も提案させる。"""
        task_context = self._get_task_context(state)
        task_context["current_datetime_iso"] = state["current_datetime_iso"]
        hint = (
            "JSON 出力は requires_specific_date(boolean), due_date(string|null), reason(string)。"
            "due_date は ISO8601 形式（例: '2025-10-25T10:00:00+09:00' または '2025-10-25'）、不要なら null。"
        )
        assessment = self._invoke_schema_with_retry(
            "_schedule_runner",
            schedule_prompt,
            ScheduleAssessment,
            {**task_context},
            hint,
        )
        if isinstance(assessment, ScheduleAssessment):
            return {
                "schedule_assessment": assessment,
                "requires_specific_date": assessment.requires_specific_date,
            }
        return {"error": assessment}

    def _apply_schedule(self, state: MemoToTaskState) -> dict[str, object]:
        """期日ベースのタスクとして `calendar` ルートに割り当てる。"""
        assessment = state.get("schedule_assessment")
        due_date = assessment.due_date if isinstance(assessment, ScheduleAssessment) else None
        overrides: dict[str, object] = {"route": "calendar"}
        if due_date:
            overrides["due_date"] = due_date
        task = self._build_task_from_seed(state, overrides)
        return {"routed_tasks": [task], "suggested_status": "active"}

    def _prepare_next_action(self, state: MemoToTaskState) -> dict[str, object]:
        """次に取るべきアクションとして `next_action` ルートを付与する。"""
        task = self._build_task_from_seed(state, {"route": "next_action"})
        return {"routed_tasks": [task], "suggested_status": "active"}

    def _get_task_context(self, state: MemoToTaskState) -> dict[str, object]:
        """下流の判定で必要となるタスク文脈（タイトル・説明等）を生成する。"""
        task = self._build_task_from_seed(state)
        _, memo_text, memo_meta = self._get_memo_context(state)
        return {
            "task_title": task.title,
            "task_description": task.description or "",
            "memo_text": memo_text,
            **memo_meta,
        }

    def _build_task_from_seed(self, state: MemoToTaskState, overrides: dict[str, object] | None = None) -> TaskDraft:
        """`TaskDraftSeed` や分類情報を用い、完成形 `TaskDraft` を構築する。

        `overrides` で route/priority/due_date 等を上書きできる。不正な値は
        サニタイズされる（未定義扱いに落とす）。

        Args:
            state: 現在のメモ処理状態
            overrides: 生成物に対する上書き指定

        Returns:
            完成した `TaskDraft`
        """
        overrides = overrides or {}
        seed_obj = state.get("task_seed")
        seed = seed_obj if isinstance(seed_obj, TaskDraftSeed) else None

        classification_obj = state.get("classification")
        classification = classification_obj if isinstance(classification_obj, MemoClassification) else None
        project_title = classification.project_title if classification and classification.project_title else None

        _, memo_text, memo_meta = self._get_memo_context(state)

        if seed is not None:
            title = seed.title
            description = seed.description
            tags = list(seed.tags) if seed.tags else None
        else:
            first_line = memo_text.splitlines()[0].strip() if memo_text else ""
            if not first_line:
                memo_title = memo_meta.get("memo_title", "")
                first_line = str(memo_title).strip()
            fallback_title = first_line[:60] or "未定義タスク"
            title = classification.project_title if classification and classification.project_title else fallback_title
            description = None
            tags = None

        route_value = overrides.get("route")
        route: TaskRoute | None = (
            route_value if isinstance(route_value, str) and route_value in VALID_TASK_ROUTES else None
        )

        due_date_value = overrides.get("due_date")
        due_date = due_date_value if isinstance(due_date_value, str) else None

        priority_value = overrides.get("priority")
        priority: TaskPriority | None = (
            priority_value if isinstance(priority_value, str) and priority_value in VALID_TASK_PRIORITIES else None
        )

        estimate_value = overrides.get("estimate_minutes")
        estimate_minutes = estimate_value if isinstance(estimate_value, int) else None

        project_title_value = overrides.get("project_title")
        if isinstance(project_title_value, str) and project_title_value:
            project_title = project_title_value

        return TaskDraft(
            title=title,
            description=description,
            tags=tags,
            route=route,
            due_date=due_date,
            priority=priority,
            estimate_minutes=estimate_minutes,
            project_title=project_title,
        )

    def _route_after_classification(self, state: MemoToTaskState) -> str:
        """分類結果とエラー有無に基づき、次のノード名を返す。"""
        error_output = state.get("error")
        if isinstance(error_output, AgentError):
            return "finalize_response"
        classification = state.get("classification")
        if not isinstance(classification, MemoClassification):
            return "finalize_response"
        if classification.decision == "idea":
            return "handle_idea"
        if classification.decision == "project":
            return "plan_project"
        return "generate_task_seed"

    def _route_after_quick_action(self, state: MemoToTaskState) -> str:
        """クイックアクション判定の真偽で分岐を返す。"""
        return "apply_quick_action" if state.get("is_quick_action") else "evaluate_responsibility"

    def _route_after_responsibility(self, state: MemoToTaskState) -> str:
        """委譲判定の真偽で分岐を返す。"""
        return "apply_delegate" if state.get("should_delegate") else "evaluate_schedule"

    def _route_after_schedule(self, state: MemoToTaskState) -> str:
        """期日必要性の真偽で分岐を返す。"""
        return "apply_schedule" if state.get("requires_specific_date") else "prepare_next_action"

    def _finalize_response(self, state: MemoToTaskState) -> dict[str, object]:
        """最終出力 `MemoToTaskAgentOutput` を組み立てて返す。

        - 途中で `error_output` が設定されていればそれを返す
        - タスク案をクリーンアップし、`suggested_memo_status` を補完
        - テスト用途フラグが有効なら Application Service 経由で永続化（ベストエフォート）

        Args:
            state: 現在のメモ処理状態

        Returns:
            エラー時は {"error": AgentError}、正常時は {"routed_tasks": [...], "suggested_status": str}
        """
        error_output = state.get("error")
        if isinstance(error_output, AgentError):
            return {"error": error_output}

        tasks = state.get("routed_tasks") or []
        cleaned_tasks = [self._clean_task(task, state) for task in tasks]

        suggested_status = state.get("suggested_status")
        if not suggested_status:
            classification = state.get("classification")
            if isinstance(classification, MemoClassification) and classification.decision == "idea":
                suggested_status = "idea"
            else:
                suggested_status = "active" if cleaned_tasks else "clarify"

        # ここで最終出力モデルは生成可能だが、stateに戻すのは最低限の情報に留める
        # （上位の _create_return_response で型付き出力へ変換する）

        # [AI GENERATED] テスト用途: フラグが有効なら永続化を実行
        try:
            if self._persist_on_finalize and cleaned_tasks:
                created_ids = self._persist_tasks_via_app(cleaned_tasks)
                agents_logger.info("Persisted tasks via Tool: {}", created_ids)
        except Exception as _exc:  # pragma: no cover - safety guard for local runs
            agents_logger.exception("Persisting tasks failed: {}", str(_exc))
        # final_response を廃止し、最終的に必要なキーだけ返す
        return {"routed_tasks": cleaned_tasks, "suggested_status": suggested_status}

    def _persist_tasks_via_app(self, tasks: list[TaskDraft]) -> list[str]:
        """Application Service 経由でタスクを永続化する（簡易版）。

        Args:
            tasks: 永続化対象のタスク候補

        Returns:
            作成されたタスクID（文字列）のリスト
        """
        from datetime import date

        from logic.application.apps import ApplicationServices
        from logic.application.task_application_service import TaskApplicationService
        from models import TaskStatus, TaskUpdate

        # 最小実装: 生成タスクはまず DRAFT として保存（レビュー前提）。
        # 必要なら後段で route→運用ステータスに更新する設計に拡張可能。
        status_map = {
            "next_action": TaskStatus.DRAFT,
            "progress": TaskStatus.DRAFT,
            "waiting": TaskStatus.DRAFT,
            "calendar": TaskStatus.DRAFT,
        }

        created_ids: list[str] = []
        # DIコンテナから TaskApplicationService を取得
        apps = ApplicationServices.create()
        app = apps.get_service(TaskApplicationService)
        for t in tasks:
            status = status_map.get(t.route or "", TaskStatus.DRAFT)
            created = app.create(title=t.title, description=t.description or None, status=status)
            created_ids.append(str(created.id))

            # TaskCreate では due_date を直接指定できないため、必要に応じて更新で反映する
            if t.due_date:
                try:
                    due = date.fromisoformat((t.due_date.split("T", 1)[0]).strip())
                    app.update(created.id, TaskUpdate(due_date=due))
                except Exception as exc:
                    # 期日の変換や更新に失敗してもエラーにはしない（ログのみ）
                    agents_logger.warning("Failed to set due_date for '{}': {}", t.title, str(exc))

        return created_ids

    def _post_process(self, output: MemoToTaskAgentOutput, state: MemoToTaskState) -> MemoToTaskAgentOutput:
        """出力後処理。

        タスクが空であれば `clarify` を提案し、存在する場合はタグや期日を
        クリーンアップして `active` を提案する。

        Args:
            output: 一旦生成した出力
            state: 現在のメモ処理状態

        Returns:
            後処理を施した `MemoToTaskAgentOutput`
        """
        if not output.tasks:
            return output.model_copy(update={"suggested_memo_status": "clarify"})

        cleaned_tasks = [self._clean_task(task, state) for task in output.tasks]
        return output.model_copy(
            update={
                "tasks": cleaned_tasks,
                "suggested_memo_status": "active",
            }
        )

    def _clean_task(self, task: TaskDraft, state: MemoToTaskState) -> TaskDraft:
        """タグ・期日などの冗長/不正値を整形してから返す。"""
        matched_tags = self._classify_tags(task, state)
        sanitized_tags = matched_tags if matched_tags else None
        due_date = task.due_date or None
        return task.model_copy(update={"tags": sanitized_tags, "due_date": due_date})

    def _classify_tags(self, task: TaskDraft, state: MemoToTaskState) -> list[str]:
        """メモ本文/タイトル/説明に基づき、利用可能な既存タグをマッチングする。"""
        available = {tag.lower(): tag for tag in state["existing_tags"]}
        _, memo_text, memo_meta = self._get_memo_context(state)
        texts = [memo_text, memo_meta.get("memo_title", ""), task.title, task.description or ""]
        from_llm = task.tags or []
        candidates = list(chain(from_llm, available.values()))

        matched: list[str] = []
        combined = "\n".join(texts).lower()
        for candidate in candidates:
            key = candidate.lower()
            if key not in available:
                continue
            if key in combined and available[key] not in matched:
                matched.append(available[key])
        for tag in from_llm:
            lower = tag.lower()
            if lower in available and available[lower] not in matched:
                matched.append(available[lower])
        return matched


if __name__ == "__main__":  # 単体テスト用簡易実行 # pragma: no cover
    import json
    from copy import deepcopy
    from uuid import uuid4

    from logging_conf import setup_logger
    from models import MemoRead, MemoStatus
    from settings.models import EnvSettings

    EnvSettings.init_environment()
    setup_logger()

    # [AI GENERATED] 最終的な確認は HuggingFaceModel(OpenVINO) で実施。
    # 実行環境に依存するため、失敗時は FAKE へフォールバックします。
    try:
        agent = MemoToTaskAgent(
            LLMProvider.FAKE,
            verbose=True,
            error_response=False,
            persist_on_finalize=True,
        )
    except Exception as exc:
        agents_logger.warning("Falling back to FAKE provider due to init error: {}", str(exc))
        agent = MemoToTaskAgent(
            LLMProvider.FAKE, verbose=True, error_response=False, persist_on_finalize=True, device="AUTO"
        )

    current_datetime = "2025-10-25T10:00:00+09:00"

    def _build_sample_state(content: str, tags: list[str], *, title: str | None = None) -> MemoToTaskState:
        memo_title = title if title is not None else (content.splitlines()[0].strip() or "サンプルメモ")
        return {
            "memo": MemoRead(id=uuid4(), title=memo_title, content=content, status=MemoStatus.INBOX),
            "existing_tags": tags,
            "current_datetime_iso": current_datetime,
        }

    # [AI GENERATED] 少数シナリオで手動確認。
    all_samples: list[tuple[str, MemoToTaskState]] = [
        (
            "quick_action",
            _build_sample_state(
                "Slackで田中さんに承認状況を確認するメッセージを送る。",
                ["連絡", "フォロー"],
                title="承認状況の確認",
            ),
        ),
        (
            "project_planning",
            _build_sample_state(
                "新しいキャンペーンサイトを来月中に公開するためのプロジェクトを立ち上げる。必要なタスクを洗い出す。",
                ["プロジェクト", "マーケティング"],
                title="キャンペーンサイト構築",
            ),
        ),
        (
            "idea_handling",
            _build_sample_state(
                "次の週末に家族とピクニックに行くアイデアを考える。",
                ["プライベート", "アイデア"],
                title="週末ピクニック案",
            ),
        ),
        (
            "task_with_schedule",
            _build_sample_state(
                "来週の月曜日までにクライアントへの提案書を作成する。",
                ["仕事", "提案書"],
                title="提案書作成",
            ),
        ),
    ]
    # [AI GENERATED] ここで実行対象シナリオを直接選択（環境変数は使用しない）
    # 必要に応じて下記のラベル配列を書き換えて、1件ずつ確認してください。
    selected_labels = ["task_with_schedule", "project_planning", "idea_handling"]
    sample_inputs = [item for item in all_samples if item[0] in selected_labels]

    for label, sample_state in sample_inputs:
        scenario_thread_id = str(uuid4())
        state_payload = deepcopy(sample_state)
        agents_logger.info("=== Scenario: {} ===", label)
        result = agent.invoke(state_payload, scenario_thread_id)
        if isinstance(result, AgentError):
            agents_logger.error("Assistant({}) Error: {}", label, str(result))
        else:
            payload = {
                "tasks": [t.model_dump(mode="json") for t in result.tasks],
                "suggested_memo_status": result.suggested_memo_status,
            }
            agents_logger.info(
                "Assistant({}): {}",
                label,
                json.dumps(payload, ensure_ascii=False, indent=2),
            )
