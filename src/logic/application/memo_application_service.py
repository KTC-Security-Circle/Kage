"""メモ管理のApplication Service

View層からSession管理を分離し、ビジネスロジックを調整する層
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any, override
from uuid import uuid4

from loguru import logger

from agents.base import ErrorAgentOutput
from errors import ApplicationError, ValidationError
from logic.application.base import BaseApplicationService
from logic.services.memo_service import MemoService
from logic.services.tag_service import TagService
from logic.unit_of_work import SqlModelUnitOfWork
from models import MemoCreate, MemoRead, MemoUpdate
from settings.manager import get_config_manager

if TYPE_CHECKING:
    import uuid

    from agents.agent_conf import LLMProvider
    from agents.task_agents.memo_to_task.agent import MemoToTaskAgent
    from agents.task_agents.memo_to_task.schema import MemoToTaskAgentOutput, TaskDraft
    from agents.task_agents.memo_to_task.state import MemoToTaskState

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
        provider: LLMProvider | None = None,
        memo_to_task_agent: MemoToTaskAgent | None = None,
    ) -> None:
        """MemoApplicationServiceの初期化

        Args:
            unit_of_work_factory: Unit of Workファクトリー
            provider: LLMプロバイダー。未指定の場合は設定値を利用する。
            memo_to_task_agent: 既存のMemoToTaskエージェントを注入する場合に指定。
        """
        super().__init__(unit_of_work_factory)

        settings = get_config_manager().settings
        self._provider: LLMProvider = provider if provider is not None else settings.agents.provider
        self._memo_to_task_agent: MemoToTaskAgent | None = memo_to_task_agent

    @classmethod
    @override
    def get_instance(cls, *args: Any, **kwargs: Any) -> MemoApplicationService: ...

    def create(self, title: str, content: str) -> MemoRead:
        """メモを作成する

        Args:
            title: メモタイトル
            content: メモ内容

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

        memo = MemoCreate(title=title, content=content)

        with self._unit_of_work_factory() as uow:
            memo_service = uow.get_service(MemoService)
            created_memo = memo_service.create(memo)

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

    def clarify_memo(self, memo_text: str) -> MemoToTaskAgentOutput:
        """自由記述メモを解析し、タスク候補とメモ状態の提案を返す。

        Args:
            memo_text: ユーザーが入力したメモ本文

        Returns:
            MemoToTaskAgentOutput: 推定タスクとメモ状態の提案

        Raises:
            MemoApplicationError: エージェントの応答がエラーまたは不正な場合
        """
        from agents.task_agents.memo_to_task.schema import MemoToTaskAgentOutput as OutputModel

        if not memo_text.strip():
            return OutputModel(tasks=[], suggested_memo_status="clarify")

        existing_tags = self._collect_existing_tag_names()
        state: MemoToTaskState = {
            "memo_text": memo_text,
            "existing_tags": existing_tags,
            "current_datetime_iso": self._current_datetime_iso(),
            "final_response": "",
        }

        response = self._invoke_memo_to_task_agent(state)
        if response is None:
            msg = "memo_to_taskエージェントから応答を取得できませんでした"
            raise MemoApplicationError(msg)
        if isinstance(response, ErrorAgentOutput):
            msg = f"memo_to_taskエージェントがエラーを返しました: {response.message}"
            raise MemoApplicationError(msg)
        if not isinstance(response, OutputModel):
            msg = "memo_to_taskエージェントの応答形式が不正です"
            raise MemoApplicationError(msg)
        return response

    def generate_tasks_from_memo(self, memo_text: str) -> list[TaskDraft]:
        """メモ本文からタスク案だけを抽出する。

        Args:
            memo_text: ユーザーが入力したメモ本文

        Returns:
            list[TaskDraft]: 抽出されたタスク案のリスト
        """
        result = self.clarify_memo(memo_text)
        return list(result.tasks)

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

            self._memo_to_task_agent = MemoToTaskAgent(provider=self._provider)
        return self._memo_to_task_agent

    def _invoke_memo_to_task_agent(
        self,
        state: MemoToTaskState,
    ) -> MemoToTaskAgentOutput | ErrorAgentOutput | None:
        """エージェントを実行し応答を取得する。"""
        agent = self._get_memo_to_task_agent()
        thread_id = str(uuid4())
        return agent.invoke(state, thread_id)

    def _current_datetime_iso(self) -> str:
        """現在日時のISO8601文字列を返す。"""
        return datetime.now(UTC).isoformat()
