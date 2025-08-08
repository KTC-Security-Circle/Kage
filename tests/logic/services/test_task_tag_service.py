"""TaskTagServiceのテストケース

このモジュールは、TaskTagServiceクラスのタスクタグ関連のビジネスロジックを
テストするためのテストケースを提供します。

テスト対象：
- create_task_tag: タスクタグ関連作成
- delete_task_tag: タスクタグ関連削除
- get_task_tags: タスクの関連タグ取得
- get_tag_tasks: タグの関連タスク取得
"""

import uuid
from unittest.mock import Mock

import pytest

from logic.repositories.task_tag import TaskTagRepository
from logic.services.task_tag_service import (
    TaskTagService,
    TaskTagServiceCheckError,
    TaskTagServiceCreateError,
)
from models import TaskTag, TaskTagCreate, TaskTagRead


class TestTaskTagServiceCreate:
    """create_task_tagメソッドのテストクラス"""

    def test_create_task_tag_success(self) -> None:
        """タスクタグ作成が成功することをテスト"""
        # [AI GENERATED] モックを作成
        task_tag_repo = Mock(spec=TaskTagRepository)
        service = TaskTagService(task_tag_repo)

        # [AI GENERATED] 作成するタスクタグデータ
        task_id = uuid.uuid4()
        tag_id = uuid.uuid4()
        task_tag_data = TaskTagCreate(task_id=task_id, tag_id=tag_id)

        # [AI GENERATED] モックの戻り値を設定
        task_tag_repo.get_by_task_and_tag.return_value = None  # 既存の関連なし
        created_task_tag = TaskTag(task_id=task_id, tag_id=tag_id)
        task_tag_repo.create.return_value = created_task_tag

        # [AI GENERATED] タスクタグを作成
        result = service.create_task_tag(task_tag_data)

        # [AI GENERATED] 結果の検証
        assert isinstance(result, TaskTagRead)
        assert result.task_id == task_id
        assert result.tag_id == tag_id

        # [AI GENERATED] モックの呼び出しを確認
        task_tag_repo.get_by_task_and_tag.assert_called_once_with(task_id, tag_id)
        task_tag_repo.create.assert_called_once_with(task_tag_data)

    def test_create_task_tag_already_exists(self) -> None:
        """既に存在するタスクタグの作成でエラーが発生することをテスト"""
        # [AI GENERATED] モックを作成
        task_tag_repo = Mock(spec=TaskTagRepository)
        service = TaskTagService(task_tag_repo)

        # [AI GENERATED] 作成するタスクタグデータ
        task_id = uuid.uuid4()
        tag_id = uuid.uuid4()
        task_tag_data = TaskTagCreate(task_id=task_id, tag_id=tag_id)

        # [AI GENERATED] 既存の関連が存在する設定
        existing_task_tag = TaskTag(task_id=task_id, tag_id=tag_id)
        task_tag_repo.get_by_task_and_tag.return_value = existing_task_tag

        # [AI GENERATED] 例外が発生することを確認
        with pytest.raises(TaskTagServiceCreateError):
            service.create_task_tag(task_tag_data)

        # [AI GENERATED] createが呼ばれていないことを確認
        task_tag_repo.create.assert_not_called()

    def test_create_task_tag_failure(self) -> None:
        """タスクタグ作成が失敗することをテスト"""
        # [AI GENERATED] モックを作成
        task_tag_repo = Mock(spec=TaskTagRepository)
        service = TaskTagService(task_tag_repo)

        # [AI GENERATED] 作成するタスクタグデータ
        task_id = uuid.uuid4()
        tag_id = uuid.uuid4()
        task_tag_data = TaskTagCreate(task_id=task_id, tag_id=tag_id)

        # [AI GENERATED] モックの戻り値を設定
        task_tag_repo.get_by_task_and_tag.return_value = None  # 既存の関連なし
        task_tag_repo.create.return_value = None  # 作成失敗

        # [AI GENERATED] 例外が発生することを確認
        with pytest.raises(TaskTagServiceCreateError):
            service.create_task_tag(task_tag_data)


class TestTaskTagServiceDelete:
    """delete_task_tagメソッドのテストクラス"""

    def test_delete_task_tag_success(self) -> None:
        """タスクタグ削除が成功することをテスト"""
        # [AI GENERATED] モックを作成
        task_tag_repo = Mock(spec=TaskTagRepository)
        service = TaskTagService(task_tag_repo)

        # [AI GENERATED] 削除対象のタスクタグ
        task_id = uuid.uuid4()
        tag_id = uuid.uuid4()

        # [AI GENERATED] モックの戻り値を設定
        existing_task_tag = TaskTag(task_id=task_id, tag_id=tag_id)
        task_tag_repo.get_by_task_and_tag.return_value = existing_task_tag
        task_tag_repo.delete_by_task_and_tag.return_value = True

        # [AI GENERATED] タスクタグを削除（例外が発生しないことを確認）
        service.delete_task_tag(task_id, tag_id)

        # [AI GENERATED] モックの呼び出しを確認
        task_tag_repo.get_by_task_and_tag.assert_called_once_with(task_id, tag_id)
        task_tag_repo.delete_by_task_and_tag.assert_called_once_with(task_id, tag_id)

    def test_delete_task_tag_not_found(self) -> None:
        """存在しないタスクタグの削除でエラーが発生することをテスト"""
        # [AI GENERATED] モックを作成
        task_tag_repo = Mock(spec=TaskTagRepository)
        service = TaskTagService(task_tag_repo)

        # [AI GENERATED] 存在しないタスクタグ
        task_id = uuid.uuid4()
        tag_id = uuid.uuid4()

        # [AI GENERATED] タスクタグが見つからない設定
        task_tag_repo.get_by_task_and_tag.return_value = None

        # [AI GENERATED] 例外が発生することを確認
        with pytest.raises(TaskTagServiceCheckError):
            service.delete_task_tag(task_id, tag_id)


class TestTaskTagServiceGetTaskTags:
    """get_task_tags_by_task_idメソッドのテストクラス"""

    def test_get_task_tags_by_task_id_success(self) -> None:
        """タスクの関連タグ取得が成功することをテスト"""
        # [AI GENERATED] モックを作成
        task_tag_repo = Mock(spec=TaskTagRepository)
        service = TaskTagService(task_tag_repo)

        # [AI GENERATED] タスクID
        task_id = uuid.uuid4()

        # [AI GENERATED] モックの戻り値を設定
        task_tags = [
            TaskTag(task_id=task_id, tag_id=uuid.uuid4()),
            TaskTag(task_id=task_id, tag_id=uuid.uuid4()),
        ]
        task_tag_repo.get_by_task_id.return_value = task_tags

        # [AI GENERATED] タスクの関連タグを取得
        result = service.get_task_tags_by_task_id(task_id)

        # [AI GENERATED] 結果の検証
        assert len(result) == len(task_tags)
        for i, task_tag_read in enumerate(result):
            assert isinstance(task_tag_read, TaskTagRead)
            assert task_tag_read.task_id == task_tags[i].task_id
            assert task_tag_read.tag_id == task_tags[i].tag_id

        # [AI GENERATED] モックの呼び出しを確認
        task_tag_repo.get_by_task_id.assert_called_once_with(task_id)

    def test_get_task_tags_by_task_id_empty_result(self) -> None:
        """関連タグがないタスクで空のリストを返すことをテスト"""
        # [AI GENERATED] モックを作成
        task_tag_repo = Mock(spec=TaskTagRepository)
        service = TaskTagService(task_tag_repo)

        # [AI GENERATED] タスクID
        task_id = uuid.uuid4()

        # [AI GENERATED] 関連タグがない設定
        task_tag_repo.get_by_task_id.return_value = []

        # [AI GENERATED] タスクの関連タグを取得
        result = service.get_task_tags_by_task_id(task_id)

        # [AI GENERATED] 空のリストが返されることを確認
        assert result == []


class TestTaskTagServiceGetTagTasks:
    """get_task_tags_by_tag_idメソッドのテストクラス"""

    def test_get_task_tags_by_tag_id_success(self) -> None:
        """タグの関連タスク取得が成功することをテスト"""
        # [AI GENERATED] モックを作成
        task_tag_repo = Mock(spec=TaskTagRepository)
        service = TaskTagService(task_tag_repo)

        # [AI GENERATED] タグID
        tag_id = uuid.uuid4()

        # [AI GENERATED] モックの戻り値を設定
        task_tags = [
            TaskTag(task_id=uuid.uuid4(), tag_id=tag_id),
            TaskTag(task_id=uuid.uuid4(), tag_id=tag_id),
        ]
        task_tag_repo.get_by_tag_id.return_value = task_tags

        # [AI GENERATED] タグの関連タスクを取得
        result = service.get_task_tags_by_tag_id(tag_id)

        # [AI GENERATED] 結果の検証
        assert len(result) == len(task_tags)
        for i, task_tag_read in enumerate(result):
            assert isinstance(task_tag_read, TaskTagRead)
            assert task_tag_read.task_id == task_tags[i].task_id
            assert task_tag_read.tag_id == task_tags[i].tag_id

        # [AI GENERATED] モックの呼び出しを確認
        task_tag_repo.get_by_tag_id.assert_called_once_with(tag_id)

    def test_get_task_tags_by_tag_id_empty_result(self) -> None:
        """関連タスクがないタグで空のリストを返すことをテスト"""
        # [AI GENERATED] モックを作成
        task_tag_repo = Mock(spec=TaskTagRepository)
        service = TaskTagService(task_tag_repo)

        # [AI GENERATED] タグID
        tag_id = uuid.uuid4()

        # [AI GENERATED] 関連タスクがない設定
        task_tag_repo.get_by_tag_id.return_value = []

        # [AI GENERATED] タグの関連タスクを取得
        result = service.get_task_tags_by_tag_id(tag_id)

        # [AI GENERATED] 空のリストが返されることを確認
        assert result == []


class TestTaskTagServiceBulkOperations:
    """一括操作のテストクラス"""

    def test_delete_task_tags_by_task_id_success(self) -> None:
        """タスクの全関連削除が成功することをテスト"""
        # [AI GENERATED] モックを作成
        task_tag_repo = Mock(spec=TaskTagRepository)
        service = TaskTagService(task_tag_repo)

        # [AI GENERATED] タスクID
        task_id = uuid.uuid4()

        # [AI GENERATED] モックの戻り値を設定
        task_tag_repo.delete_by_task_id.return_value = 3  # 3件削除

        # [AI GENERATED] タスクの全関連を削除
        service.delete_task_tags_by_task_id(task_id)

        # [AI GENERATED] モックの呼び出しを確認
        task_tag_repo.delete_by_task_id.assert_called_once_with(task_id)

    def test_delete_task_tags_by_tag_id_success(self) -> None:
        """タグの全関連削除が成功することをテスト"""
        # [AI GENERATED] モックを作成
        task_tag_repo = Mock(spec=TaskTagRepository)
        service = TaskTagService(task_tag_repo)

        # [AI GENERATED] タグID
        tag_id = uuid.uuid4()

        # [AI GENERATED] モックの戻り値を設定
        task_tag_repo.delete_by_tag_id.return_value = 2  # 2件削除

        # [AI GENERATED] タグの全関連を削除
        service.delete_task_tags_by_tag_id(tag_id)

        # [AI GENERATED] モックの呼び出しを確認
        task_tag_repo.delete_by_tag_id.assert_called_once_with(tag_id)
