from __future__ import annotations

from types import SimpleNamespace
from uuid import UUID, uuid4

from agents.task_agents.memo_to_task.schema import MemoToTaskAgentOutput, ProjectPlanSuggestion, TaskDraft
from logic.application.memo_ai_job_queue import MemoAiJobQueue
from logic.application.project_application_service import ProjectApplicationService
from logic.application.task_application_service import TaskApplicationService
from models import ProjectStatus, TaskStatus


class FakeApps:
    def __init__(self, services: dict[type[object], object]) -> None:
        self._services = services

    def get_service(self, service_cls: type[object]) -> object:
        return self._services[service_cls]


class FakeProjectService:
    def __init__(self) -> None:
        self.created: list[dict[str, object]] = []

    def create(self, *, title: str, description: str, status: object) -> SimpleNamespace:
        project_id = uuid4()
        self.created.append({"title": title, "description": description, "status": status, "id": project_id})
        return SimpleNamespace(id=project_id, status=status, title=title, description=description)


class FakeTaskService:
    def __init__(self) -> None:
        self.created_payloads: list[dict[str, object]] = []

    def create(self, **kwargs: object) -> SimpleNamespace:
        self.created_payloads.append(kwargs)
        task_id = uuid4()
        return SimpleNamespace(
            id=task_id,
            title=kwargs.get("title"),
            description=kwargs.get("description"),
            status=kwargs.get("status", TaskStatus.DRAFT),
            tags=[],
            project_id=kwargs.get("project_id"),
        )


def _build_stub_memo(*, memo_id: UUID | None = None, title: str = "memo", content: str = "summary") -> SimpleNamespace:
    return SimpleNamespace(id=memo_id or uuid4(), title=title, content=content)


def _build_queue(fake_apps: FakeApps) -> MemoAiJobQueue:
    queue = object.__new__(MemoAiJobQueue)
    queue._apps = fake_apps  # type: ignore[attr-defined]
    return queue


def test_project_creation_and_task_linking() -> None:
    """requires_project=True の場合にプロジェクト作成とタスク紐付けが行われる。"""
    project_service = FakeProjectService()
    task_service = FakeTaskService()
    apps = FakeApps(
        {
            ProjectApplicationService: project_service,
            TaskApplicationService: task_service,
        }
    )
    queue = _build_queue(apps)
    memo = _build_stub_memo()
    output = MemoToTaskAgentOutput(
        tasks=[TaskDraft(title="最初のアクション", project_title="LLM PoC")],
        suggested_memo_status="active",
        requires_project=True,
        project_plan=ProjectPlanSuggestion(project_title="LLM PoC", next_actions=[]),
    )

    project_payload = queue._create_project_if_required(memo, output)  # type: ignore[attr-defined]
    assert project_payload is not None
    assert project_service.created
    created_project_id = project_payload.project_id
    assert created_project_id is not None

    payloads = queue._create_draft_tasks(memo, output.tasks, created_project_id)  # type: ignore[attr-defined]
    assert task_service.created_payloads[0]["project_id"] == created_project_id
    assert payloads[0].project_id == created_project_id
    assert project_payload.status == ProjectStatus.DRAFT.value


def test_project_description_uses_memo_content() -> None:
    """メモ本文からプロジェクト説明が生成される。"""
    project_service = FakeProjectService()
    task_service = FakeTaskService()
    apps = FakeApps(
        {
            ProjectApplicationService: project_service,
            TaskApplicationService: task_service,
        }
    )
    queue = _build_queue(apps)
    memo = _build_stub_memo(content="第一行\n第二行\n\n詳細メモ")
    output = MemoToTaskAgentOutput(
        tasks=[TaskDraft(title="kickoff", project_title="新製品企画")],
        suggested_memo_status="active",
        requires_project=True,
        project_plan=ProjectPlanSuggestion(project_title="新製品企画", next_actions=[]),
    )

    payload = queue._create_project_if_required(memo, output)  # type: ignore[attr-defined]
    assert payload is not None
    description = str(project_service.created[0]["description"])
    assert "第一行 第二行 詳細メモ" in description
    assert project_service.created[0]["status"] == ProjectStatus.DRAFT
