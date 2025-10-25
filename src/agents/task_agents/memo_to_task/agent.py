"""メモをタスク案へ変換するエージェント。"""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from itertools import chain
from typing import TYPE_CHECKING, cast

from langgraph.graph import END, START, StateGraph
from pydantic import ValidationError

from agents.base import BaseAgent, ErrorAgentOutput, KwargsAny
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
)
from agents.task_agents.memo_to_task.state import MemoToTaskState
from agents.utils import LLMProvider, agents_logger

if TYPE_CHECKING:
    from collections.abc import Callable

    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.runnables import RunnableSerializable
    from pydantic import BaseModel


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
    title = memo_text.splitlines()[0][:30] or "メモの整理"
    description = memo_text[:120] if memo_text else None
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


class MemoToTaskAgent(BaseAgent[MemoToTaskState, MemoToTaskAgentOutput]):
    """メモから TaskDraft を抽出するエージェント。"""

    _name = "MemoToTaskAgent"
    _description = "自由形式メモからタスク候補を抽出する"
    _state = MemoToTaskState

    _fake_responses = cast("list[BaseModel]", list(_DEFAULT_FAKE_RESPONSES))

    def __init__(self, provider: LLMProvider = LLMProvider.FAKE, **kwargs: KwargsAny) -> None:
        super().__init__(provider, **kwargs)

    def create_graph(self, graph_builder: StateGraph) -> StateGraph:
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

    def _get_structured_runner(
        self,
        attr_name: str,
        prompt: ChatPromptTemplate,
        schema: type[BaseModel],
    ) -> RunnableSerializable:
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

    def _invoke_schema_with_retry(
        self,
        runner_attr: str,
        prompt: ChatPromptTemplate,
        schema: type[BaseModel],
        base_params: dict[str, object],
        retry_hint: str,
    ) -> BaseModel | ErrorAgentOutput:
        """構造化出力に対して1回だけ再試行する薄いヘルパー。

        1回目: retry_hint="" で実行→検証
        失敗時: retry_hint に修正指示を渡して再実行→検証
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

    def _repair_classification_response(
        self,
        raw_response: object,
    ) -> MemoClassification | ErrorAgentOutput:
        """Attempt to coerce a non-conforming classification payload."""
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
        return self.validate_output(raw_response, MemoClassification)

    @staticmethod
    def _infer_decision_from_reason(reason: object) -> MemoProcessingDecision | None:
        """Infer memo classification decision from reasoning text."""
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
        runner = self._get_structured_runner("_classifier_runner", classification_prompt, MemoClassification)
        response = runner.invoke(
            {
                "memo_text": state["memo_text"],
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
        return {"error_output": classification}

    def _handle_idea(self, state: MemoToTaskState) -> dict[str, object]:
        classification = state.get("classification")
        if isinstance(classification, MemoClassification) and classification.reason:
            agents_logger.debug("IDEA判定理由: %s", classification.reason)
        return {"routed_tasks": [], "suggested_status": "idea"}

    def _plan_project(self, state: MemoToTaskState) -> dict[str, object]:
        classification = state.get("classification")
        if not isinstance(classification, MemoClassification):
            return {"routed_tasks": [], "suggested_status": "idea"}
        base_params = {
            "memo_text": state["memo_text"],
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
                        return {"error_output": suggestion3}
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
                    return {"error_output": suggestion2}
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
        try:
            datetime.fromisoformat(value)
        except ValueError:
            return False
        else:
            return True

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
        action = dict(item)
        due = action.get("due_date")
        if isinstance(due, str) and due and not self._is_valid_iso8601(due):
            action["due_date"] = None
        route = action.get("route")
        if isinstance(route, str) and route not in VALID_TASK_ROUTES:
            action.pop("route", None)
        return action

    def _sanitize_action_model(self, item: TaskDraft) -> TaskDraft:
        # Pydanticモデル(TaskDraft)が来る場合を想定
        new_item = item
        if isinstance(item.due_date, str) and item.due_date and not self._is_valid_iso8601(item.due_date):
            new_item = item.model_copy(update={"due_date": None})
        if isinstance(new_item.route, str) and new_item.route not in VALID_TASK_ROUTES:
            new_item = new_item.model_copy(update={"route": None})
        return new_item

    def _generate_task_seed(self, state: MemoToTaskState) -> dict[str, object]:
        params = {
            "memo_text": state["memo_text"],
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
        return {"error_output": seed}

    def _evaluate_quick_action(self, state: MemoToTaskState) -> dict[str, object]:
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
        return {"error_output": assessment}

    def _apply_quick_action(self, state: MemoToTaskState) -> dict[str, object]:
        task = self._build_task_from_seed(state, {"route": "progress"})
        if task.estimate_minutes is None:
            task = task.model_copy(update={"estimate_minutes": QUICK_ACTION_THRESHOLD_MINUTES})
        return {"routed_tasks": [task], "suggested_status": "active"}

    def _evaluate_responsibility(self, state: MemoToTaskState) -> dict[str, object]:
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
        return {"error_output": assessment}

    def _apply_delegate(self, state: MemoToTaskState) -> dict[str, object]:
        task = self._build_task_from_seed(state, {"route": "waiting"})
        return {"routed_tasks": [task], "suggested_status": "active"}

    def _evaluate_schedule(self, state: MemoToTaskState) -> dict[str, object]:
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
        return {"error_output": assessment}

    def _apply_schedule(self, state: MemoToTaskState) -> dict[str, object]:
        assessment = state.get("schedule_assessment")
        due_date = assessment.due_date if isinstance(assessment, ScheduleAssessment) else None
        overrides: dict[str, object] = {"route": "calendar"}
        if due_date:
            overrides["due_date"] = due_date
        task = self._build_task_from_seed(state, overrides)
        return {"routed_tasks": [task], "suggested_status": "active"}

    def _prepare_next_action(self, state: MemoToTaskState) -> dict[str, object]:
        task = self._build_task_from_seed(state, {"route": "next_action"})
        return {"routed_tasks": [task], "suggested_status": "active"}

    def _get_task_context(self, state: MemoToTaskState) -> dict[str, object]:
        task = self._build_task_from_seed(state)
        return {
            "task_title": task.title,
            "task_description": task.description or "",
            "memo_text": state["memo_text"],
        }

    def _build_task_from_seed(self, state: MemoToTaskState, overrides: dict[str, object] | None = None) -> TaskDraft:
        overrides = overrides or {}
        seed_obj = state.get("task_seed")
        seed = seed_obj if isinstance(seed_obj, TaskDraftSeed) else None

        classification_obj = state.get("classification")
        classification = classification_obj if isinstance(classification_obj, MemoClassification) else None
        project_title = classification.project_title if classification and classification.project_title else None

        if seed is not None:
            title = seed.title
            description = seed.description
            tags = list(seed.tags) if seed.tags else None
        else:
            memo_text = state["memo_text"]
            first_line = memo_text.splitlines()[0].strip() if memo_text else ""
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
        error_output = state.get("error_output")
        if isinstance(error_output, ErrorAgentOutput):
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
        return "apply_quick_action" if state.get("is_quick_action") else "evaluate_responsibility"

    def _route_after_responsibility(self, state: MemoToTaskState) -> str:
        return "apply_delegate" if state.get("should_delegate") else "evaluate_schedule"

    def _route_after_schedule(self, state: MemoToTaskState) -> str:
        return "apply_schedule" if state.get("requires_specific_date") else "prepare_next_action"

    def _finalize_response(self, state: MemoToTaskState) -> dict[str, MemoToTaskAgentOutput | ErrorAgentOutput]:
        error_output = state.get("error_output")
        if isinstance(error_output, ErrorAgentOutput):
            return {"final_response": error_output}

        tasks = state.get("routed_tasks") or []
        cleaned_tasks = [self._clean_task(task, state) for task in tasks]

        suggested_status = state.get("suggested_status")
        if not suggested_status:
            classification = state.get("classification")
            if isinstance(classification, MemoClassification) and classification.decision == "idea":
                suggested_status = "idea"
            else:
                suggested_status = "active" if cleaned_tasks else "clarify"

        final_output = MemoToTaskAgentOutput(
            tasks=cleaned_tasks,
            suggested_memo_status=suggested_status,
        )
        return {"final_response": final_output}

    def _post_process(self, output: MemoToTaskAgentOutput, state: MemoToTaskState) -> MemoToTaskAgentOutput:
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
        matched_tags = self._classify_tags(task, state)
        sanitized_tags = matched_tags if matched_tags else None
        due_date = task.due_date or None
        return task.model_copy(update={"tags": sanitized_tags, "due_date": due_date})

    def _classify_tags(self, task: TaskDraft, state: MemoToTaskState) -> list[str]:
        available = {tag.lower(): tag for tag in state["existing_tags"]}
        texts = [state["memo_text"], task.title, task.description or ""]
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

    from agents.agent_conf import HuggingFaceModel
    from logging_conf import setup_logger
    from settings.models import EnvSettings

    EnvSettings.init_environment()
    setup_logger()

    agent = MemoToTaskAgent(
        LLMProvider.OPENVINO, model_name=HuggingFaceModel.QWEN_3_8B_INT4, verbose=True, error_response=False
    )

    current_datetime = "2025-10-25T10:00:00+09:00"
    sample_inputs: list[tuple[str, MemoToTaskState]] = [
        (
            "delegate_waiting",
            {
                "memo_text": "来週のプロジェクト会議の準備をする。議題は予算案の確認と新規メンバーの紹介。",
                "existing_tags": ["仕事", "会議", "準備"],
                "current_datetime_iso": current_datetime,
                "final_response": "",
            },
        ),
        (
            "quick_action",
            {
                "memo_text": "Slackで田中さんに承認状況を確認するメッセージを送る。",
                "existing_tags": ["連絡", "フォロー"],
                "current_datetime_iso": current_datetime,
                "final_response": "",
            },
        ),
        (
            "idea_capture",
            {
                "memo_text": "将来的に試したい新サービスのアイデアを箇条書きで記録しておく。",
                "existing_tags": ["アイデア", "リサーチ"],
                "current_datetime_iso": current_datetime,
                "final_response": "",
            },
        ),
        (
            "schedule_needed",
            {
                "memo_text": "木曜日の15時に顧客とのデモ準備ミーティングを開催する。場所と資料を整える必要あり。",
                "existing_tags": ["会議", "顧客", "調整"],
                "current_datetime_iso": current_datetime,
                "final_response": "",
            },
        ),
        (
            "project_planning",
            {
                "memo_text": (
                    "新しいキャンペーンサイトを来月中に公開するためのプロジェクトを立ち上げる。必要なタスクを洗い出す。"
                ),
                "existing_tags": ["プロジェクト", "マーケティング"],
                "current_datetime_iso": current_datetime,
                "final_response": "",
            },
        ),
    ]

    for label, sample_state in sample_inputs:
        scenario_thread_id = str(uuid4())
        state_payload = deepcopy(sample_state)
        agents_logger.info("=== Scenario: {} ===", label)
        result = agent.invoke(state_payload, scenario_thread_id)
        if result:
            agents_logger.info(
                "Assistant({}): {}",
                label,
                json.dumps(result.model_dump(mode="json"), ensure_ascii=False, indent=2),
            )
        else:
            agents_logger.warning("Assistant({}): No response returned", label)
