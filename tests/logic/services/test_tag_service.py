"""TagServiceのテストケース

このモジュールは、TagServiceクラスのタグ関連のビジネスロジックを
テストするためのテストケースを提供します。

テスト対象：
- create_tag: タグ作成
- update_tag: タグ更新
- delete_tag: タグ削除（関連タスクタグチェック含む）
- get_all_tags: 全タグ取得
- search_tags: タグ検索
"""

import uuid
from unittest.mock import Mock, call

import pytest

from logic.repositories.tag import TagRepository
from logic.repositories.task_tag import TaskTagRepository
from logic.services.tag_service import (
    TagService,
    TagServiceCheckError,
    TagServiceCreateError,
    TagServiceDeleteError,
    TagServiceUpdateError,
)
from models import Tag, TagCreate, TagRead, TagUpdate, TaskTag


class TestTagServiceCreate:
    """create_tagメソッドのテストクラス"""

    def test_create_tag_success(self) -> None:
        """タグ作成が成功することをテスト"""
        # [AI GENERATED] モックを作成
        tag_repo = Mock(spec=TagRepository)
        task_tag_repo = Mock(spec=TaskTagRepository)
        service = TagService(tag_repo, task_tag_repo)

        # [AI GENERATED] 作成するタグデータ
        tag_data = TagCreate(name="新しいタグ")

        # [AI GENERATED] モックの戻り値を設定
        created_tag = Tag(
            id=uuid.uuid4(),
            name=tag_data.name,
        )
        tag_repo.get_by_name.return_value = None  # 重複なし
        tag_repo.create.return_value = created_tag

        # [AI GENERATED] タグを作成
        result = service.create_tag(tag_data)

        # [AI GENERATED] 結果の検証
        assert isinstance(result, TagRead)
        assert result.name == tag_data.name
        assert result.id == created_tag.id

        # [AI GENERATED] モックの呼び出しを確認
        tag_repo.create.assert_called_once_with(tag_data)

    def test_create_tag_failure(self) -> None:
        """タグ作成が失敗することをテスト"""
        # [AI GENERATED] モックを作成
        tag_repo = Mock(spec=TagRepository)
        task_tag_repo = Mock(spec=TaskTagRepository)
        service = TagService(tag_repo, task_tag_repo)

        # [AI GENERATED] 作成するタグデータ
        tag_data = TagCreate(name="失敗タグ")

        # [AI GENERATED] リポジトリの作成が失敗する設定
        tag_repo.create.return_value = None

        # [AI GENERATED] 例外が発生することを確認
        with pytest.raises(TagServiceCreateError):
            service.create_tag(tag_data)


class TestTagServiceUpdate:
    """update_tagメソッドのテストクラス"""

    def test_update_tag_success(self) -> None:
        """タグ更新が成功することをテスト"""
        # [AI GENERATED] モックを作成
        tag_repo = Mock(spec=TagRepository)
        task_tag_repo = Mock(spec=TaskTagRepository)
        service = TagService(tag_repo, task_tag_repo)

        # [AI GENERATED] 更新対象のタグ
        tag_id = uuid.uuid4()
        existing_tag = Tag(
            id=tag_id,
            name="更新前タグ",
        )

        # [AI GENERATED] 更新データ
        update_data = TagUpdate(name="更新後タグ")

        # [AI GENERATED] 更新後のタグ
        updated_tag = Tag(
            id=tag_id,
            name=update_data.name or "デフォルト名",
        )

        # [AI GENERATED] モックの戻り値を設定
        tag_repo.get_by_id.return_value = existing_tag
        tag_repo.get_by_name.return_value = None  # 重複なし
        tag_repo.update.return_value = updated_tag

        # [AI GENERATED] タグを更新
        result = service.update_tag(tag_id, update_data)

        # [AI GENERATED] 結果の検証
        assert isinstance(result, TagRead)
        assert result.id == tag_id
        assert result.name == (update_data.name or "デフォルト名")

        # [AI GENERATED] モックの呼び出しを確認
        tag_repo.get_by_id.assert_called_once_with(tag_id)
        tag_repo.update.assert_called_once_with(tag_id, update_data)

    def test_update_tag_not_found(self) -> None:
        """存在しないタグの更新でエラーが発生することをテスト"""
        # [AI GENERATED] モックを作成
        tag_repo = Mock(spec=TagRepository)
        task_tag_repo = Mock(spec=TaskTagRepository)
        service = TagService(tag_repo, task_tag_repo)

        # [AI GENERATED] 存在しないタグID
        tag_id = uuid.uuid4()
        update_data = TagUpdate(name="更新データ")

        # [AI GENERATED] タグが見つからない設定
        tag_repo.get_by_id.return_value = None

        # [AI GENERATED] 例外が発生することを確認
        with pytest.raises(TagServiceCheckError):
            service.update_tag(tag_id, update_data)

    def test_update_tag_failure(self) -> None:
        """タグ更新が失敗することをテスト"""
        # [AI GENERATED] モックを作成
        tag_repo = Mock(spec=TagRepository)
        task_tag_repo = Mock(spec=TaskTagRepository)
        service = TagService(tag_repo, task_tag_repo)

        # [AI GENERATED] 更新対象のタグ
        tag_id = uuid.uuid4()
        existing_tag = Tag(
            id=tag_id,
            name="更新前タグ",
        )

        update_data = TagUpdate(name="更新データ")

        # [AI GENERATED] モックの戻り値を設定
        tag_repo.get_by_id.return_value = existing_tag
        tag_repo.update.return_value = None  # 更新失敗

        # [AI GENERATED] 例外が発生することを確認
        with pytest.raises(TagServiceUpdateError):
            service.update_tag(tag_id, update_data)


class TestTagServiceDelete:
    """delete_tagメソッドのテストクラス"""

    def test_delete_tag_success_no_related_task_tags(self) -> None:
        """関連タスクタグがないタグの削除が成功することをテスト"""
        # [AI GENERATED] モックを作成
        tag_repo = Mock(spec=TagRepository)
        task_tag_repo = Mock(spec=TaskTagRepository)
        service = TagService(tag_repo, task_tag_repo)

        # [AI GENERATED] 削除対象のタグ
        tag_id = uuid.uuid4()
        existing_tag = Tag(
            id=tag_id,
            name="削除対象タグ",
        )

        # [AI GENERATED] モックの戻り値を設定
        tag_repo.get_by_id.return_value = existing_tag
        task_tag_repo.get_by_tag_id.return_value = []  # 関連タスクタグなし
        tag_repo.delete.return_value = True

        # [AI GENERATED] タグを削除
        result = service.delete_tag(tag_id)

        # [AI GENERATED] 削除が成功したことを確認
        assert result is True

        # [AI GENERATED] モックの呼び出しを確認
        tag_repo.get_by_id.assert_called_once_with(tag_id)
        task_tag_repo.get_by_tag_id.assert_called_once_with(tag_id)
        tag_repo.delete.assert_called_once_with(tag_id)

    def test_delete_tag_with_related_task_tags_without_force(self) -> None:
        """関連タスクタグがあるタグの削除でエラーが発生することをテスト"""
        # [AI GENERATED] モックを作成
        tag_repo = Mock(spec=TagRepository)
        task_tag_repo = Mock(spec=TaskTagRepository)
        service = TagService(tag_repo, task_tag_repo)

        # [AI GENERATED] 削除対象のタグ
        tag_id = uuid.uuid4()
        existing_tag = Tag(
            id=tag_id,
            name="関連タスクタグありタグ",
        )

        # [AI GENERATED] 関連タスクタグを作成
        related_task_tags = [
            TaskTag(
                task_id=uuid.uuid4(),
                tag_id=tag_id,
            )
        ]

        # [AI GENERATED] モックの戻り値を設定
        tag_repo.get_by_id.return_value = existing_tag
        task_tag_repo.get_by_tag_id.return_value = related_task_tags

        # [AI GENERATED] 例外が発生することを確認
        with pytest.raises(TagServiceDeleteError):
            service.delete_tag(tag_id, force=False)

        # [AI GENERATED] 削除が呼ばれていないことを確認
        tag_repo.delete.assert_not_called()

    def test_delete_tag_with_related_task_tags_with_force(self) -> None:
        """関連タスクタグがあるタグの強制削除が成功することをテスト"""
        # [AI GENERATED] モックを作成
        tag_repo = Mock(spec=TagRepository)
        task_tag_repo = Mock(spec=TaskTagRepository)
        service = TagService(tag_repo, task_tag_repo)

        # [AI GENERATED] 削除対象のタグ
        tag_id = uuid.uuid4()
        existing_tag = Tag(
            id=tag_id,
            name="強制削除タグ",
        )

        # [AI GENERATED] 関連タスクタグを作成
        task1_id = uuid.uuid4()
        task2_id = uuid.uuid4()
        related_task_tags = [
            TaskTag(
                task_id=task1_id,
                tag_id=tag_id,
            ),
            TaskTag(
                task_id=task2_id,
                tag_id=tag_id,
            ),
        ]

        # [AI GENERATED] モックの戻り値を設定
        tag_repo.get_by_id.return_value = existing_tag
        task_tag_repo.get_by_tag_id.return_value = related_task_tags
        task_tag_repo.delete_by_task_and_tag.return_value = True  # 各削除が成功
        tag_repo.delete.return_value = True

        # [AI GENERATED] タグを強制削除
        result = service.delete_tag(tag_id, force=True)

        # [AI GENERATED] 削除が成功したことを確認
        assert result is True

        # [AI GENERATED] 関連タスクタグの削除が呼ばれたことを確認
        expected_calls = [call(task1_id, tag_id), call(task2_id, tag_id)]
        task_tag_repo.delete_by_task_and_tag.assert_has_calls(expected_calls)
        tag_repo.delete.assert_called_once_with(tag_id)

    def test_delete_tag_not_found(self) -> None:
        """存在しないタグの削除でエラーが発生することをテスト"""
        # [AI GENERATED] モックを作成
        tag_repo = Mock(spec=TagRepository)
        task_tag_repo = Mock(spec=TaskTagRepository)
        service = TagService(tag_repo, task_tag_repo)

        # [AI GENERATED] 存在しないタグID
        tag_id = uuid.uuid4()

        # [AI GENERATED] タグが見つからない設定
        tag_repo.get_by_id.return_value = None

        # [AI GENERATED] 例外が発生することを確認
        with pytest.raises(TagServiceCheckError):
            service.delete_tag(tag_id)

    def test_delete_tag_failure(self) -> None:
        """タグ削除が失敗することをテスト"""
        # [AI GENERATED] モックを作成
        tag_repo = Mock(spec=TagRepository)
        task_tag_repo = Mock(spec=TaskTagRepository)
        service = TagService(tag_repo, task_tag_repo)

        # [AI GENERATED] 削除対象のタグ
        tag_id = uuid.uuid4()
        existing_tag = Tag(
            id=tag_id,
            name="削除失敗タグ",
        )

        # [AI GENERATED] モックの戻り値を設定
        tag_repo.get_by_id.return_value = existing_tag
        task_tag_repo.get_by_tag_id.return_value = []
        tag_repo.delete.return_value = False  # 削除失敗

        # [AI GENERATED] 例外が発生することを確認
        with pytest.raises(TagServiceDeleteError):
            service.delete_tag(tag_id)
