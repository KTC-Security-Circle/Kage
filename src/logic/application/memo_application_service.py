"""メモ管理のApplication Service

View層からSession管理を分離し、ビジネスロジックを調整する層
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any, override
from uuid import UUID, uuid4

from loguru import logger

from agents.agent_conf import LLMProvider, OpenVINODevice
from errors import ApplicationError, ValidationError
from logic.application.base import BaseApplicationService
from logic.application.memo_ai_job_queue import MemoAiJobSnapshot, MemoAiJobStatus, get_memo_ai_job_queue
from logic.application.settings_application_service import SettingsApplicationService
from logic.services.memo_service import MemoService
from logic.services.tag_service import TagService
from logic.unit_of_work import SqlModelUnitOfWork
from models import (
    AiSuggestionStatus,
    MemoCreate,
    MemoRead,
    MemoStatus,
    MemoUpdate,
    ProjectStatus,
    ProjectUpdate,
    TaskRead,
    TaskStatus,
    TaskUpdate,
)

if TYPE_CHECKING:
    import uuid
    from collections.abc import Callable, Sequence

    from agents.base import AgentError
    from agents.task_agents.memo_to_task.agent import MemoToTaskAgent
    from agents.task_agents.memo_to_task.schema import MemoToTaskAgentOutput, TaskDraft
    from agents.task_agents.memo_to_task.state import MemoToTaskResult, MemoToTaskState
    from logic.application.apps import ApplicationServices
    from logic.application.task_application_service import TaskApplicationService

logger_msg = "{msg} - (ID={memo_id})"


class MemoApplicationError(ApplicationError):
    """メモ管理のApplication Serviceで発生するエラー"""


class ContentValidationError(ValidationError, MemoApplicationError):
    """メモ内容のバリデーションエラー"""


class MemoApplicationService(BaseApplicationService[type[SqlModelUnitOfWork]]):
    """メモ管理のApplication Service

    View層からSession管理を分離し、ビジネスロジックを調整する層
    """

    def __init__(
        self,
        unit_of_work_factory: type[SqlModelUnitOfWork] = SqlModelUnitOfWork,
        *,
        memo_to_task_agent: MemoToTaskAgent | None = None,
    ) -> None:
        """MemoApplicationServiceの初期化

        Args:
            unit_of_work_factory: Unit of Workファクトリー
            memo_to_task_agent: 既存のMemoToTaskエージェントを注入する場合に指定。
        """
        super().__init__(unit_of_work_factory)

        # 設定値は SettingsApplicationService 経由で初期化時に読み取りキャッシュ。
        # invalidate_all() によりサービス再構築時に最新値へ更新される。
        from typing import cast

        settings_app = cast("SettingsApplicationService", SettingsApplicationService.get_instance())
        settings = settings_app.get_agents_settings()
        self._provider: LLMProvider = settings.provider
        runtime_cfg = getattr(settings, "runtime", None)
        raw_device = getattr(runtime_cfg, "device", None)
        if isinstance(raw_device, OpenVINODevice):
            self._device = raw_device.value
        else:
            self._device = str(raw_device or OpenVINODevice.CPU.value).upper()
        self._memo_to_task_agent: MemoToTaskAgent | None = memo_to_task_agent
        from logic.application.apps import ApplicationServices

        self._apps: ApplicationServices = ApplicationServices.create()

    @classmethod
    @override
    def get_instance(cls, *args: Any, **kwargs: Any) -> MemoApplicationService:
        from typing import cast

        instance = super().get_instance(*args, **kwargs)
        return cast("MemoApplicationService", instance)

    def create(
        self,
        title: str,
        content: str,
        *,
        status: MemoStatus = MemoStatus.INBOX,
        tag_ids: Sequence[uuid.UUID] | None = None,
    ) -> MemoRead:
        """メモを作成する

        Args:
            title: メモタイトル
            content: メモ内容
            status: 初期ステータス（省略時は INBOX）
            tag_ids: 付与するタグIDの一覧

        Returns:
            MemoRead: 作成されたメモ

        Raises:
            ContentValidationError: タイトルまたは内容が空の場合
        """
        if not title.strip():
            msg = "メモタイトルを入力してください"
            raise ContentValidationError(msg)

        if not content.strip():
            msg = "メモ内容を入力してください"
            raise ContentValidationError(msg)

        memo = MemoCreate(title=title, content=content, status=status)

        with self._unit_of_work_factory() as uow:
            memo_service = uow.get_service(MemoService)
            created_memo = memo_service.create(memo)
            if tag_ids:
                # dict.fromkeys で順序を維持したまま重複排除
                unique_tag_ids = dict.fromkeys(tag_ids)
                for tag_id in unique_tag_ids:
                    created_memo = memo_service.add_tag(created_memo.id, tag_id)

        logger.info(logger_msg.format(msg="メモ作成完了", memo_id=created_memo.id))
        return created_memo

    def update(self, memo_id: uuid.UUID, update_data: MemoUpdate) -> MemoRead:
        """メモを更新する

        Args:
            memo_id: 更新するメモのID
            update_data: メモ更新データ

        Returns:
            MemoRead: 更新されたメモ
        """
        with self._unit_of_work_factory() as uow:
            memo_service = uow.get_service(MemoService)
            updated_memo = memo_service.update(memo_id, update_data)

        logger.info(logger_msg.format(msg="メモ更新完了", memo_id=updated_memo.id))
        return updated_memo

    def delete(self, memo_id: uuid.UUID) -> bool:
        """メモ削除

        Args:
            memo_id: 削除するメモのID

        Returns:
            bool: 削除成功フラグ

        Raises:
            RuntimeError: 削除エラー
        """
        with self._unit_of_work_factory() as uow:
            memo_service = uow.get_service(MemoService)
            success = memo_service.delete(memo_id)

            logger.info(f"メモ削除完了: ID {memo_id}, 結果: {success}")
            return success

    def get_by_id(self, memo_id: uuid.UUID, *, with_details: bool = False) -> MemoRead:
        """IDでメモ取得

        Args:
            memo_id: メモのID
            with_details: 関連エンティティも取得するかどうか

        Returns:
            MemoRead: 指定されたIDのメモ
        """
        with self._unit_of_work_factory() as uow:
            memo_service = uow.get_service(MemoService)
            return memo_service.get_by_id(memo_id, with_details=with_details)

    def get_all_memos(self, *, with_details: bool = False) -> list[MemoRead]:
        """全メモ取得

        Args:
            with_details: 関連エンティティも取得するかどうか

        Returns:
            list[MemoRead]: 全メモのリスト
        """
        with self._unit_of_work_factory() as uow:
            memo_service = uow.service_factory.get_service(MemoService)
            return memo_service.get_all(with_details=with_details)

    def list_by_tag(self, tag_id: uuid.UUID, *, with_details: bool = False) -> list[MemoRead]:
        """タグIDでメモ一覧を取得する。

        Args:
            tag_id: タグID
            with_details: 関連エンティティを含めるかどうか

        Returns:
            list[MemoRead]: タグに紐づくメモ一覧
        """
        with self._unit_of_work_factory() as uow:
            memo_service = uow.get_service(MemoService)
            return memo_service.list_by_tag(tag_id, with_details=with_details)

    def clarify_memo(self, memo: MemoRead) -> MemoToTaskAgentOutput:
        """自由記述メモを解析し、タスク候補とメモ状態の提案を返す。

        Args:
            memo: 解析対象のメモ情報

        Returns:
            MemoToTaskAgentOutput: 推定タスクとメモ状態の提案

        Raises:
            MemoApplicationError: エージェントの応答がエラーまたは不正な場合
        """
        from agents.task_agents.memo_to_task.schema import MemoToTaskAgentOutput as OutputModel

        memo_content = getattr(memo, "content", "")
        if not str(memo_content).strip():
            return OutputModel(tasks=[], suggested_memo_status="clarify")

        if self._provider == LLMProvider.FAKE:
            agent = self._get_memo_to_task_agent()
            logger.debug(f"MemoToTask: using FAKE provider, memo_id={memo.id}")
            fake_output = agent.next_fake_response()
            if fake_output is not None:
                logger.debug(f"MemoToTask: returning fake output with {len(fake_output.tasks)} tasks")
                return fake_output

        existing_tags = self._collect_existing_tag_names()
        state: MemoToTaskState = {
            "memo": memo,
            "existing_tags": existing_tags,
            "current_datetime_iso": self._current_datetime_iso(),
        }

        response = self._invoke_memo_to_task_agent(state)
        if response is None:
            msg = "memo_to_taskエージェントから応答を取得できませんでした"
            raise MemoApplicationError(msg)
        # 新契約: dataclass 結果 or AgentError
        from agents.base import AgentError
        from agents.task_agents.memo_to_task.state import MemoToTaskResult

        if isinstance(response, AgentError):
            msg = f"memo_to_taskエージェントがエラーを返しました: {response}"
            raise MemoApplicationError(msg)
        if isinstance(response, MemoToTaskResult):
            return OutputModel(
                tasks=response.tasks,
                suggested_memo_status=response.suggested_memo_status,
                requires_project=response.requires_project,
                project_plan=response.project_plan,
            )
        # 互換: テストが直接 OutputModel を返すようにモンキーパッチする場合を許容
        if isinstance(response, OutputModel):
            return response
        msg = "memo_to_taskエージェントの応答形式が不正です"
        raise MemoApplicationError(msg)

    def generate_tasks_from_memo(self, memo: MemoRead) -> list[TaskDraft]:
        """メモ本文からタスク案だけを抽出する。

        Args:
            memo: 解析対象のメモ情報

        Returns:
            list[TaskDraft]: 抽出されたタスク案のリスト
        """
        result = self.clarify_memo(memo)
        return list(result.tasks)

    # --- AIタスク生成 -------------------------------------------------

    def enqueue_ai_generation(self, memo_id: uuid.UUID) -> MemoAiJobSnapshot:
        """メモをAIタスク生成キューに登録する。"""
        memo = self.get_by_id(memo_id, with_details=True)
        updated = self._mark_ai_status(
            memo_id,
            ai_status=AiSuggestionStatus.PENDING,
            memo_status=MemoStatus.ACTIVE if memo.status == MemoStatus.INBOX else None,
            clear_analysis_log=True,
        )
        queue = get_memo_ai_job_queue()
        return queue.enqueue(updated, callback=self._handle_ai_job_callback)

    def get_ai_job_snapshot(self, job_id: uuid.UUID) -> MemoAiJobSnapshot:
        """ジョブ状態を取得する。"""
        queue = get_memo_ai_job_queue()
        snapshot = queue.get_snapshot(job_id)
        if snapshot is None:
            msg = f"AIジョブが見つかりません: job_id={job_id}"
            raise MemoApplicationError(msg)
        return snapshot

    def _handle_ai_job_callback(self, snapshot: MemoAiJobSnapshot) -> None:
        if snapshot.status == MemoAiJobStatus.SUCCEEDED:
            self._persist_ai_snapshot(snapshot)
            self._mark_ai_status(snapshot.memo_id, ai_status=AiSuggestionStatus.AVAILABLE)
        elif snapshot.status == MemoAiJobStatus.FAILED:
            self._mark_ai_status(snapshot.memo_id, ai_status=AiSuggestionStatus.FAILED)

    def _collect_existing_tag_names(self) -> list[str]:
        """既存タグの名称一覧を取得する。"""
        names: list[str] = []
        with self._unit_of_work_factory() as uow:
            tag_service = uow.get_service(TagService)
            tags = tag_service.get_all()

        for tag in tags:
            name = getattr(tag, "name", "").strip()
            if not name or name in names:
                continue
            names.append(name)
        return names

    def _get_memo_to_task_agent(self) -> MemoToTaskAgent:
        """MemoToTaskエージェントを遅延初期化して取得する。"""
        if self._memo_to_task_agent is None:
            from agents.task_agents.memo_to_task.agent import MemoToTaskAgent

            self._memo_to_task_agent = MemoToTaskAgent(provider=self._provider, device=self._device)
        return self._memo_to_task_agent

    def _invoke_memo_to_task_agent(
        self,
        state: MemoToTaskState,
    ) -> MemoToTaskResult | AgentError | None:
        """エージェントを実行し応答を取得する。"""
        agent = self._get_memo_to_task_agent()
        thread_id = str(uuid4())
        return agent.invoke(state, thread_id)

    def _current_datetime_iso(self) -> str:
        """現在日時のISO8601文字列を返す。"""
        return datetime.now(UTC).isoformat()

    def _mark_ai_status(
        self,
        memo_id: uuid.UUID,
        *,
        ai_status: AiSuggestionStatus,
        memo_status: MemoStatus | None = None,
        clear_analysis_log: bool = False,
    ) -> MemoRead:
        """メモのAIステータスを更新する。"""
        payload_kwargs: dict[str, Any] = {"ai_suggestion_status": ai_status}
        if memo_status is not None:
            payload_kwargs["status"] = memo_status
        if clear_analysis_log:
            payload_kwargs["ai_analysis_log"] = None
        payload = MemoUpdate(**payload_kwargs)
        return self.update(memo_id, payload)

    def _persist_ai_snapshot(self, snapshot: MemoAiJobSnapshot) -> None:
        tasks_payload = [
            {
                "task_id": str(task.task_id),
                "title": task.title,
                "description": task.description,
                "tags": list(task.tags),
                "route": task.route,
                "due_date": task.due_date,
                "project_title": task.project_title,
                "project_id": str(task.project_id) if task.project_id else None,
                "status": task.status.value,
            }
            for task in snapshot.tasks
        ]
        draft_refs = [
            {
                "task_id": str(task.task_id),
                "route": task.route,
                "project_title": task.project_title,
                "project_id": str(task.project_id) if task.project_id else None,
                "status": task.status.value,
            }
            for task in snapshot.tasks
        ]
        project_info = None
        if snapshot.project is not None:
            project_info = {
                "project_id": str(snapshot.project.project_id) if snapshot.project.project_id else None,
                "title": snapshot.project.title,
                "description": snapshot.project.description,
                "status": snapshot.project.status,
                "error": snapshot.project.error,
            }
        log_payload = {
            "version": 3,
            "job_id": str(snapshot.job_id),
            "generated_at": datetime.now(UTC).isoformat(),
            "suggested_memo_status": snapshot.suggested_memo_status,
            "tasks": tasks_payload,
            "draft_task_refs": draft_refs,
            "project_info": project_info,
        }
        serialized = json.dumps(log_payload, ensure_ascii=False)
        self.update(snapshot.memo_id, MemoUpdate(ai_analysis_log=serialized))

    def approve_ai_tasks(self, memo_id: uuid.UUID, task_ids: list[uuid.UUID]) -> list[TaskRead]:
        """Draft タスクを承認し、TaskStatus を route に応じて更新する。"""
        if not task_ids:
            return []

        route_map = self._load_route_map(memo_id)
        task_service = self._get_task_service()
        approved: list[TaskRead] = []
        for task_id in task_ids:
            status = self._route_to_status(route_map.get(str(task_id)))
            updated = task_service.update(task_id, TaskUpdate(status=status))
            approved.append(updated)

        self._activate_project_from_ai_log(memo_id)
        self._remove_tasks_from_ai_log(memo_id, task_ids)
        return approved

    def delete_ai_task(self, memo_id: uuid.UUID, task_id: uuid.UUID) -> None:
        """Draft タスクを削除する。"""
        task_service = self._get_task_service()
        task_service.delete(task_id)
        self._remove_tasks_from_ai_log(memo_id, [task_id])

    def create_ai_task(
        self,
        memo_id: uuid.UUID,
        *,
        title: str,
        description: str | None = None,
        route: str | None = None,
        project_title: str | None = None,
    ) -> TaskRead:
        """ユーザー起点の Draft タスクを作成する。"""
        task_service = self._get_task_service()
        created = task_service.create(
            title=title,
            description=description or "",
            status=TaskStatus.DRAFT,
            memo_id=memo_id,
        )
        self._append_draft_task_ref(
            memo_id,
            task_id=created.id,
            route=route or "next_action",
            project_title=project_title,
            status=created.status,
            project_id=created.project_id,
        )
        return created

    def update_ai_task(
        self,
        task_id: uuid.UUID,
        *,
        title: str | None = None,
        description: str | None = None,
    ) -> TaskRead:
        """Draft タスクの内容を更新する。"""
        task_service = self._get_task_service()
        update_payload = TaskUpdate(title=title, description=description)
        return task_service.update(task_id, update_payload)

    def _get_task_service(self) -> TaskApplicationService:
        from logic.application.task_application_service import TaskApplicationService

        return self._apps.get_service(TaskApplicationService)

    def _load_route_map(self, memo_id: uuid.UUID) -> dict[str, str | None]:
        memo = self.get_by_id(memo_id, with_details=True)
        data = self._ensure_ai_log_dict(memo.ai_analysis_log)
        route_map: dict[str, str | None] = {}
        refs = data.get("draft_task_refs")
        if not isinstance(refs, list):
            return route_map
        for entry in refs:
            if not isinstance(entry, dict):
                continue
            key = str(entry.get("task_id"))
            route_map[key] = entry.get("route")
        return route_map

    def _route_to_status(self, route: str | None) -> TaskStatus:
        if route == "progress":
            return TaskStatus.PROGRESS
        if route == "waiting":
            return TaskStatus.WAITING
        if route == "calendar":
            return TaskStatus.TODAYS
        return TaskStatus.TODO

    def _activate_project_from_ai_log(self, memo_id: uuid.UUID) -> None:
        """AIログに紐づくプロジェクトをACTIVEへ更新する。"""
        memo = self.get_by_id(memo_id, with_details=True)
        data = self._ensure_ai_log_dict(memo.ai_analysis_log)
        info = data.get("project_info")
        if not isinstance(info, dict):
            return
        project_id_str = info.get("project_id")
        if not project_id_str or info.get("status") == ProjectStatus.ACTIVE.value:
            return
        try:
            project_uuid = UUID(str(project_id_str))
        except ValueError:
            return
        from logic.application.project_application_service import ProjectApplicationService

        project_service = self._apps.get_service(ProjectApplicationService)
        project_service.update(project_uuid, ProjectUpdate(status=ProjectStatus.ACTIVE))

        def _mutator(payload: dict[str, object]) -> None:
            project_info = payload.get("project_info")
            if isinstance(project_info, dict):
                project_info["status"] = ProjectStatus.ACTIVE.value

        self._mutate_ai_log(memo_id, _mutator)

    def _remove_tasks_from_ai_log(self, memo_id: uuid.UUID, task_ids: list[uuid.UUID]) -> None:
        targets = {str(task_id) for task_id in task_ids}

        def _mutator(payload: dict[str, object]) -> None:
            tasks = payload.get("tasks")
            if isinstance(tasks, list):
                filtered: list[object] = []
                for task in tasks:
                    if isinstance(task, dict) and str(task.get("task_id")) in targets:
                        continue
                    filtered.append(task)
                payload["tasks"] = filtered
            refs = payload.get("draft_task_refs")
            if isinstance(refs, list):
                payload["draft_task_refs"] = [
                    ref for ref in refs if not (isinstance(ref, dict) and str(ref.get("task_id")) in targets)
                ]

        self._mutate_ai_log(memo_id, _mutator)

    def _append_draft_task_ref(
        self,
        memo_id: uuid.UUID,
        *,
        task_id: UUID,
        route: str | None,
        project_title: str | None,
        status: TaskStatus,
        project_id: UUID | None = None,
    ) -> None:
        def _mutator(payload: dict[str, object]) -> None:
            refs = payload.setdefault("draft_task_refs", [])
            if isinstance(refs, list):
                refs.append(
                    {
                        "task_id": str(task_id),
                        "route": route,
                        "project_title": project_title,
                        "project_id": str(project_id) if project_id else None,
                        "status": status.value,
                    }
                )

        self._mutate_ai_log(memo_id, _mutator)

    def _mutate_ai_log(self, memo_id: uuid.UUID, mutator: Callable[[dict[str, object]], None]) -> None:
        memo = self.get_by_id(memo_id, with_details=True)
        payload = self._ensure_ai_log_dict(memo.ai_analysis_log)
        mutator(payload)
        serialized = json.dumps(payload, ensure_ascii=False)
        self.update(memo_id, MemoUpdate(ai_analysis_log=serialized))

    def _ensure_ai_log_dict(self, raw: str | None) -> dict[str, object]:
        if raw:
            try:
                payload = json.loads(raw)
            except json.JSONDecodeError:
                payload = {}
        else:
            payload = {}
        payload.setdefault("version", 3)
        payload.setdefault("tasks", [])
        payload.setdefault("draft_task_refs", [])
        payload.setdefault("project_info", None)
        return payload

    def search(
        self,
        query: str,
        *,
        with_details: bool = False,
        status: MemoStatus | None = None,
        tags: list[uuid.UUID] | None = None,
    ) -> list[MemoRead]:
        """メモ検索

        タイトル・本文を横断検索し、必要に応じてステータスやタグで絞り込む。

        Args:
            query: 検索クエリ（空文字・空白のみなら空配列）
            with_details: 関連情報を含めるかどうか
            status: ステータスでの追加フィルタ
            tags: タグIDのリスト（OR条件）

        Returns:
            list[MemoRead]: 検索結果
        """
        if not query or not query.strip():
            return []

        with self._unit_of_work_factory() as uow:
            memo_service = uow.get_service(MemoService)
            results = memo_service.search_memos(query, with_details=with_details)

            # ステータスフィルタ
            if status is not None:
                status_items = memo_service.list_by_status(status, with_details=with_details)
                status_ids = {m.id for m in status_items}
                results = [m for m in results if m.id in status_ids]

            # タグフィルタ（リポジトリのJOIN利用、OR条件）
            if tags:
                from logic.repositories import MemoRepository as _MemoRepo

                memo_repo = uow.repository_factory.create(_MemoRepo)
                matched_ids: set[uuid.UUID] = set()
                for tag_id in tags:
                    try:
                        for m in memo_repo.list_by_tag(tag_id, with_details=with_details):
                            if m.id is not None:
                                matched_ids.add(m.id)
                    except Exception as exc:
                        logger.debug(f"メモのタグフィルタ処理中に例外: {exc}")
                        continue
                results = [m for m in results if m.id in matched_ids]

            return results
