"""TaskTagApplicationServiceのテストケース

このモジュールは、TaskTagApplicationServiceクラスの
Application Service層の機能をテストするためのテストケースを提供します。

テスト対象：
- create_task_tag: タスクタグ作成のApplication Service層ロジック
- delete_task_tag: タスクタグ削除のApplication Service層ロジック
- get_task_tags_by_task_id: タスクID指定のタスクタグ取得
- get_task_tags_by_tag_id: タグID指定のタスクタグ取得
- check_task_tag_exists: タスクタグ存在確認
- get_all_task_tags: 全タスクタグ取得
"""

import uuid
from unittest.mock import Mock

import pytest

from logic.application.task_tag_application_service import TaskTagApplicationService
from logic.commands.task_tag_commands import (
    CreateTaskTagCommand,
    DeleteTaskTagCommand,
    DeleteTaskTagsByTagCommand,
    DeleteTaskTagsByTaskCommand,
)
from logic.queries.task_tag_queries import (
    CheckTaskTagExistsQuery,
    GetAllTaskTagsQuery,
    GetTaskTagByTaskAndTagQuery,
    GetTaskTagsByTagIdQuery,
    GetTaskTagsByTaskIdQuery,
)
from models import TaskTagRead


class TestTaskTagApplicationService:
    """TaskTagApplicationServiceのApplication Service層機能をテストするクラス"""

    @pytest.fixture
    def mock_unit_of_work(self) -> Mock:
        """モックのUnit of Workを作成"""
        mock_uow = Mock()
        mock_service_factory = Mock()
        mock_task_tag_service = Mock()

        # [AI GENERATED] モックの階層構造を設定
        mock_uow.service_factory = mock_service_factory
        mock_service_factory.create_task_tag_service.return_value = mock_task_tag_service

        # [AI GENERATED] コンテキストマネージャとして機能させる
        mock_uow.__enter__ = Mock(return_value=mock_uow)
        mock_uow.__exit__ = Mock(return_value=None)

        return mock_uow

    @pytest.fixture
    def mock_unit_of_work_factory(self, mock_unit_of_work: Mock) -> Mock:
        """モックのUnit of Work Factoryを作成"""
        return Mock(return_value=mock_unit_of_work)

    @pytest.fixture
    def task_tag_application_service(self, mock_unit_of_work_factory: Mock) -> TaskTagApplicationService:
        """TaskTagApplicationServiceのインスタンスを作成"""
        return TaskTagApplicationService(mock_unit_of_work_factory)  # type: ignore[arg-type]

    @pytest.fixture
    def sample_task_tag_read(self) -> TaskTagRead:
        """テスト用のTaskTagReadデータを作成"""
        return TaskTagRead(
            task_id=uuid.uuid4(),
            tag_id=uuid.uuid4(),
        )

    def test_create_task_tag_success(
        self,
        task_tag_application_service: TaskTagApplicationService,
        mock_unit_of_work: Mock,
        sample_task_tag_read: TaskTagRead,
    ) -> None:
        """正常系: タスクタグ作成成功"""
        # モックの設定
        mock_task_tag_service = mock_unit_of_work.service_factory.create_task_tag_service.return_value
        mock_task_tag_service.create_task_tag.return_value = sample_task_tag_read

        # コマンド作成
        command = CreateTaskTagCommand(
            task_id=sample_task_tag_read.task_id,
            tag_id=sample_task_tag_read.tag_id,
        )

        # 実行
        result = task_tag_application_service.create_task_tag(command)

        # 検証
        assert isinstance(result, TaskTagRead)
        assert result.task_id == sample_task_tag_read.task_id
        assert result.tag_id == sample_task_tag_read.tag_id
        mock_task_tag_service.create_task_tag.assert_called_once()
        mock_unit_of_work.commit.assert_called_once()

    def test_create_task_tag_validation_error_no_task_id(
        self, task_tag_application_service: TaskTagApplicationService
    ) -> None:
        """異常系: タスクタグ作成時のタスクIDなしバリデーションエラー"""
        # タスクIDなしでコマンド作成
        command = CreateTaskTagCommand(
            task_id=None,  # type: ignore[arg-type]
            tag_id=uuid.uuid4(),
        )

        # 実行と検証
        with pytest.raises(ValueError, match="タスクIDが指定されていません"):
            task_tag_application_service.create_task_tag(command)

    def test_create_task_tag_validation_error_no_tag_id(
        self, task_tag_application_service: TaskTagApplicationService
    ) -> None:
        """異常系: タスクタグ作成時のタグIDなしバリデーションエラー"""
        # タグIDなしでコマンド作成
        command = CreateTaskTagCommand(
            task_id=uuid.uuid4(),
            tag_id=None,  # type: ignore[arg-type]
        )

        # 実行と検証
        with pytest.raises(ValueError, match="タグIDが指定されていません"):
            task_tag_application_service.create_task_tag(command)

    def test_get_all_task_tags(
        self,
        task_tag_application_service: TaskTagApplicationService,
        mock_unit_of_work: Mock,
        sample_task_tag_read: TaskTagRead,
    ) -> None:
        """正常系: 全タスクタグ取得"""
        # モックの設定
        mock_task_tag_service = mock_unit_of_work.service_factory.create_task_tag_service.return_value
        mock_task_tag_service.get_all_task_tags.return_value = [sample_task_tag_read]

        # クエリ作成
        query = GetAllTaskTagsQuery()

        # 実行
        result = task_tag_application_service.get_all_task_tags(query)

        # 検証
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0] == sample_task_tag_read
        mock_task_tag_service.get_all_task_tags.assert_called_once()

    def test_get_task_tags_by_task_id(
        self,
        task_tag_application_service: TaskTagApplicationService,
        mock_unit_of_work: Mock,
        sample_task_tag_read: TaskTagRead,
    ) -> None:
        """正常系: タスクID指定タスクタグ取得"""
        # モックの設定
        mock_task_tag_service = mock_unit_of_work.service_factory.create_task_tag_service.return_value
        mock_task_tag_service.get_task_tags_by_task_id.return_value = [sample_task_tag_read]

        # クエリ作成
        query = GetTaskTagsByTaskIdQuery(task_id=sample_task_tag_read.task_id)

        # 実行
        result = task_tag_application_service.get_task_tags_by_task_id(query)

        # 検証
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0] == sample_task_tag_read
        mock_task_tag_service.get_task_tags_by_task_id.assert_called_once_with(sample_task_tag_read.task_id)

    def test_get_task_tags_by_tag_id(
        self,
        task_tag_application_service: TaskTagApplicationService,
        mock_unit_of_work: Mock,
        sample_task_tag_read: TaskTagRead,
    ) -> None:
        """正常系: タグID指定タスクタグ取得"""
        # モックの設定
        mock_task_tag_service = mock_unit_of_work.service_factory.create_task_tag_service.return_value
        mock_task_tag_service.get_task_tags_by_tag_id.return_value = [sample_task_tag_read]

        # クエリ作成
        query = GetTaskTagsByTagIdQuery(tag_id=sample_task_tag_read.tag_id)

        # 実行
        result = task_tag_application_service.get_task_tags_by_tag_id(query)

        # 検証
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0] == sample_task_tag_read
        mock_task_tag_service.get_task_tags_by_tag_id.assert_called_once_with(sample_task_tag_read.tag_id)

    def test_check_task_tag_exists_true(
        self,
        task_tag_application_service: TaskTagApplicationService,
        mock_unit_of_work: Mock,
        sample_task_tag_read: TaskTagRead,
    ) -> None:
        """正常系: タスクタグ存在確認（存在する場合）"""
        # モックの設定
        mock_task_tag_service = mock_unit_of_work.service_factory.create_task_tag_service.return_value
        mock_task_tag_service.check_task_tag_exists.return_value = True

        # クエリ作成
        query = CheckTaskTagExistsQuery(
            task_id=sample_task_tag_read.task_id,
            tag_id=sample_task_tag_read.tag_id,
        )

        # 実行
        result = task_tag_application_service.check_task_tag_exists(query)

        # 検証
        assert result is True
        mock_task_tag_service.check_task_tag_exists.assert_called_once_with(
            sample_task_tag_read.task_id, sample_task_tag_read.tag_id
        )

    def test_check_task_tag_exists_false(
        self,
        task_tag_application_service: TaskTagApplicationService,
        mock_unit_of_work: Mock,
        sample_task_tag_read: TaskTagRead,
    ) -> None:
        """正常系: タスクタグ存在確認（存在しない場合）"""
        # モックの設定
        mock_task_tag_service = mock_unit_of_work.service_factory.create_task_tag_service.return_value
        mock_task_tag_service.check_task_tag_exists.return_value = False

        # クエリ作成
        query = CheckTaskTagExistsQuery(
            task_id=sample_task_tag_read.task_id,
            tag_id=sample_task_tag_read.tag_id,
        )

        # 実行
        result = task_tag_application_service.check_task_tag_exists(query)

        # 検証
        assert result is False
        mock_task_tag_service.check_task_tag_exists.assert_called_once_with(
            sample_task_tag_read.task_id, sample_task_tag_read.tag_id
        )

    def test_get_task_tag_by_task_and_tag(
        self,
        task_tag_application_service: TaskTagApplicationService,
        mock_unit_of_work: Mock,
        sample_task_tag_read: TaskTagRead,
    ) -> None:
        """正常系: タスクとタグ指定でタスクタグ取得"""
        # モックの設定
        mock_task_tag_service = mock_unit_of_work.service_factory.create_task_tag_service.return_value
        mock_task_tag_service.get_task_tag_by_task_and_tag.return_value = sample_task_tag_read

        # クエリ作成
        query = GetTaskTagByTaskAndTagQuery(
            task_id=sample_task_tag_read.task_id,
            tag_id=sample_task_tag_read.tag_id,
        )

        # 実行
        result = task_tag_application_service.get_task_tag_by_task_and_tag(query)

        # 検証
        assert result == sample_task_tag_read
        mock_task_tag_service.get_task_tag_by_task_and_tag.assert_called_once_with(
            sample_task_tag_read.task_id, sample_task_tag_read.tag_id
        )

    def test_delete_task_tag_success(
        self,
        task_tag_application_service: TaskTagApplicationService,
        mock_unit_of_work: Mock,
        sample_task_tag_read: TaskTagRead,
    ) -> None:
        """正常系: タスクタグ削除成功"""
        # モックの設定
        mock_task_tag_service = mock_unit_of_work.service_factory.create_task_tag_service.return_value

        # コマンド作成
        command = DeleteTaskTagCommand(
            task_id=sample_task_tag_read.task_id,
            tag_id=sample_task_tag_read.tag_id,
        )

        # 実行
        task_tag_application_service.delete_task_tag(command)

        # 検証
        mock_task_tag_service.delete_task_tag.assert_called_once_with(
            sample_task_tag_read.task_id, sample_task_tag_read.tag_id
        )
        mock_unit_of_work.commit.assert_called_once()

    def test_delete_task_tags_by_task_id(
        self,
        task_tag_application_service: TaskTagApplicationService,
        mock_unit_of_work: Mock,
        sample_task_tag_read: TaskTagRead,
    ) -> None:
        """正常系: タスクID指定のタスクタグ削除"""
        # モックの設定
        mock_task_tag_service = mock_unit_of_work.service_factory.create_task_tag_service.return_value

        # コマンド作成
        command = DeleteTaskTagsByTaskCommand(task_id=sample_task_tag_read.task_id)

        # 実行
        task_tag_application_service.delete_task_tags_by_task_id(command)

        # 検証
        mock_task_tag_service.delete_task_tags_by_task_id.assert_called_once_with(sample_task_tag_read.task_id)
        mock_unit_of_work.commit.assert_called_once()

    def test_delete_task_tags_by_tag_id(
        self,
        task_tag_application_service: TaskTagApplicationService,
        mock_unit_of_work: Mock,
        sample_task_tag_read: TaskTagRead,
    ) -> None:
        """正常系: タグID指定のタスクタグ削除"""
        # モックの設定
        mock_task_tag_service = mock_unit_of_work.service_factory.create_task_tag_service.return_value

        # コマンド作成
        command = DeleteTaskTagsByTagCommand(tag_id=sample_task_tag_read.tag_id)

        # 実行
        task_tag_application_service.delete_task_tags_by_tag_id(command)

        # 検証
        mock_task_tag_service.delete_task_tags_by_tag_id.assert_called_once_with(sample_task_tag_read.tag_id)
        mock_unit_of_work.commit.assert_called_once()
