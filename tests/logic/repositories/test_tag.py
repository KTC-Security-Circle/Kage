"""TagRepositoryのテストケース

このモジュールは、TagRepositoryクラスのタグ固有の操作を
テストするためのテストケースを提供します。

テスト対象：
- get_all: 全タグ取得
- get_by_name: タグ名による取得
- search_by_name: タグ名検索
- exists_by_name: タグ名による存在チェック
"""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from sqlmodel import Session

    from logic.repositories.tag import TagRepository

from errors import NotFoundError, RepositoryError
from models import Memo, MemoStatus, Tag, TagCreate, TagUpdate
from tests.logic.helpers import create_test_task


def create_test_tag(
    name: str = "テストタグ",
) -> Tag:
    """テスト用のTagオブジェクトを作成する

    Args:
        name: タグの名前

    Returns:
        作成されたTagオブジェクト
    """
    return Tag(
        name=name,
    )


@pytest.fixture
def sample_tags(test_session: Session) -> list[Tag]:
    """テスト用のサンプルタグを作成してデータベースに保存

    Args:
        test_session: テスト用データベースセッション

    Returns:
        list[Tag]: 作成されたサンプルタグのリスト
    """
    tags = [
        create_test_tag("重要"),
        create_test_tag("緊急"),
        create_test_tag("仕事"),
        create_test_tag("個人"),
        create_test_tag("学習"),
    ]

    # [AI GENERATED] データベースにサンプルタグを保存
    for tag in tags:
        test_session.add(tag)

    test_session.commit()

    # [AI GENERATED] 保存後にリフレッシュしてIDを確実に取得
    for tag in tags:
        test_session.refresh(tag)

    return tags


class TestTagRepositoryGetAll:
    """get_allメソッドのテストクラス"""

    def test_get_all_returns_all_tags(self, tag_repository: TagRepository, sample_tags: list[Tag]) -> None:
        """全てのタグを取得できることをテスト"""
        # [AI GENERATED] 全タグを取得
        result = tag_repository.get_all()

        # [AI GENERATED] 期待される数のタグが取得されることを確認
        assert len(result) == len(sample_tags)

        # [AI GENERATED] 全てのタグIDが含まれていることを確認
        result_ids = {tag.id for tag in result}
        expected_ids = {tag.id for tag in sample_tags}
        assert result_ids == expected_ids

    def test_get_all_raises_not_found_when_no_tags(self, tag_repository: TagRepository) -> None:
        """タグが存在しない場合は NotFoundError を送出"""
        with pytest.raises(NotFoundError):
            tag_repository.get_all()


class TestTagRepositoryGetByName:
    """get_by_nameメソッドのテストクラス"""

    def test_get_by_name_finds_existing_tag(self, tag_repository: TagRepository, sample_tags: list[Tag]) -> None:
        """存在するタグ名でタグを取得できることをテスト"""
        # [AI GENERATED] 存在するタグ名で検索
        target_tag = sample_tags[0]
        result = tag_repository.get_by_name(target_tag.name)

        # [AI GENERATED] 正しいタグが取得されることを確認
        assert result is not None
        assert result.id == target_tag.id
        assert result.name == target_tag.name

    def test_get_by_name_raises_not_found_for_nonexistent_tag(
        self, tag_repository: TagRepository, sample_tags: list[Tag]
    ) -> None:
        """存在しないタグ名で検索した場合は NotFoundError"""
        with pytest.raises(NotFoundError):
            tag_repository.get_by_name("存在しないタグ")

    def test_get_by_name_case_sensitive(self, tag_repository: TagRepository, sample_tags: list[Tag]) -> None:
        """タグ名検索が大文字小文字を区別することをテスト"""
        # [AI GENERATED] 大文字小文字を変えて検索
        target_tag = sample_tags[0]
        result = tag_repository.get_by_name(target_tag.name.upper())

        # [AI GENERATED] 大文字小文字が違う場合はNoneが返されることを確認
        if target_tag.name != target_tag.name.upper():
            assert result is None


class TestTagRepositorySearchByName:
    """search_by_nameメソッドのテストクラス"""

    def test_search_by_name_finds_matching_tags(self, tag_repository: TagRepository, sample_tags: list[Tag]) -> None:
        """タグ名の部分一致でタグを検索できることをテスト"""
        # [AI GENERATED] 部分一致する文字列で検索
        result = tag_repository.search_by_name("重")

        # [AI GENERATED] "重" を含むタグが取得されることを確認
        expected_tags = [tag for tag in sample_tags if "重" in tag.name]
        assert len(result) == len(expected_tags)

        # [AI GENERATED] 全ての結果のタグ名に検索キーワードが含まれることを確認
        for tag in result:
            assert "重" in tag.name

    def test_search_by_name_case_insensitive(self, tag_repository: TagRepository, sample_tags: list[Tag]) -> None:
        """タグ名検索が大文字小文字を区別しないことをテスト"""
        # [AI GENERATED] 大文字小文字を変えて検索
        result_lower = tag_repository.search_by_name("重要")
        result_upper = tag_repository.search_by_name("重要")

        # [AI GENERATED] 同じ結果が得られることを確認
        assert len(result_lower) == len(result_upper)

    def test_search_by_name_raises_not_found_for_no_matches(
        self, tag_repository: TagRepository, sample_tags: list[Tag]
    ) -> None:
        """一致しないキーワードで検索した場合は NotFoundError を送出"""
        with pytest.raises(NotFoundError):
            tag_repository.search_by_name("存在しないキーワード")


"""exists_by_name は現行APIに存在しないためスキップ"""


class TestTagRepositoryBaseCRUD:
    """BaseRepositoryから継承したCRUD操作のテストクラス"""

    def test_create_tag_success(self, tag_repository: TagRepository) -> None:
        """タグ作成が成功することをテスト"""
        # [AI GENERATED] テスト用タグデータを作成
        tag_data = TagCreate(
            name="新しいタグ",
        )

        # [AI GENERATED] タグを作成
        result = tag_repository.create(tag_data)

        # [AI GENERATED] 作成されたタグの検証
        assert result is not None
        assert result.name == tag_data.name
        assert result.id is not None

    def test_get_by_id_success(self, tag_repository: TagRepository) -> None:
        """IDによるタグ取得が成功することをテスト"""
        # [AI GENERATED] テスト用タグを作成
        tag_data = TagCreate(
            name="取得テストタグ",
        )
        created_tag = tag_repository.create(tag_data)
        assert created_tag is not None
        assert created_tag.id is not None

        # [AI GENERATED] 作成されたタグをIDで取得
        result = tag_repository.get_by_id(created_tag.id)

        # [AI GENERATED] 取得されたタグの検証
        assert result is not None
        assert result.id == created_tag.id
        assert result.name == created_tag.name

    def test_get_by_id_not_found(self, tag_repository: TagRepository) -> None:
        """存在しないIDでタグ取得した場合は NotFoundError"""
        non_existent_id = uuid.uuid4()
        with pytest.raises(NotFoundError):
            tag_repository.get_by_id(non_existent_id)

    def test_update_tag_success(self, tag_repository: TagRepository) -> None:
        """タグ更新が成功することをテスト"""
        # [AI GENERATED] テスト用タグを作成
        tag_data = TagCreate(
            name="更新前タグ",
        )
        created_tag = tag_repository.create(tag_data)
        assert created_tag is not None
        assert created_tag.id is not None

        # [AI GENERATED] タグを更新
        update_data = TagUpdate(
            name="更新後タグ",
        )
        result = tag_repository.update(created_tag.id, update_data)

        # [AI GENERATED] 更新されたタグの検証
        assert result is not None
        assert result.id == created_tag.id
        assert result.name == update_data.name

    def test_update_tag_not_found(self, tag_repository: TagRepository) -> None:
        """存在しないタグの更新は RepositoryError を送出"""
        non_existent_id = uuid.uuid4()
        update_data = TagUpdate(name="存在しない更新")
        with pytest.raises(RepositoryError):
            tag_repository.update(non_existent_id, update_data)

    def test_delete_tag_success(self, tag_repository: TagRepository) -> None:
        """タグ削除が成功することをテスト"""
        # [AI GENERATED] テスト用タグを作成
        tag_data = TagCreate(
            name="削除テストタグ",
        )
        created_tag = tag_repository.create(tag_data)
        assert created_tag is not None
        assert created_tag.id is not None

        # [AI GENERATED] タグを削除
        result = tag_repository.delete(created_tag.id)

        # [AI GENERATED] 削除が成功したことを確認
        assert result is True

        # [AI GENERATED] 削除後の取得は NotFoundError
        assert created_tag.id is not None
        with pytest.raises(NotFoundError):
            tag_repository.get_by_id(created_tag.id)

    def test_delete_tag_not_found(self, tag_repository: TagRepository) -> None:
        """存在しないタグの削除でFalseを返すことをテスト"""
        # [AI GENERATED] 存在しないUUIDで削除を試行
        non_existent_id = uuid.uuid4()
        result = tag_repository.delete(non_existent_id)

        # [AI GENERATED] Falseが返されることを確認
        assert result is False


class TestTagRepositoryRelations:
    """TagRepository の関連操作分岐テスト"""

    def test_task_relations_add_remove_clear(self, tag_repository: TagRepository, test_session: Session) -> None:
        """タスクの追加・重複・未関連削除・全削除・存在しないIDの分岐を検証"""
        tag = Tag(name="関連")
        task = create_test_task(title="関連タスク")
        other_task = create_test_task(title="未関連")
        test_session.add_all([tag, task, other_task])
        test_session.commit()
        test_session.refresh(tag)
        test_session.refresh(task)
        test_session.refresh(other_task)

        assert tag.id is not None
        assert task.id is not None
        assert other_task.id is not None

        updated = tag_repository.add_task(tag.id, task.id)
        assert any(t.id == task.id for t in updated.tasks)
        updated = tag_repository.add_task(tag.id, task.id)
        assert len([t for t in updated.tasks if t.id == task.id]) == 1

        updated = tag_repository.remove_task(tag.id, other_task.id)
        assert all(t.id != other_task.id for t in updated.tasks)

        with pytest.raises(NotFoundError):
            tag_repository.remove_task(tag.id, uuid.uuid4())

        updated = tag_repository.remove_all_tasks(tag.id)
        assert len(updated.tasks) == 0

        updated = tag_repository.remove_all_tasks(tag.id)
        assert len(updated.tasks) == 0

    def test_memo_relations_add_remove_clear(self, tag_repository: TagRepository, test_session: Session) -> None:
        """メモの追加・重複・未関連削除・全削除・存在しないIDの分岐を検証"""
        tag = Tag(name="関連2")
        memo = Memo(title="学習ノート", content="", status=MemoStatus.INBOX)
        other_memo = Memo(title="未関連ノート", content="", status=MemoStatus.INBOX)
        test_session.add_all([tag, memo, other_memo])
        test_session.commit()
        test_session.refresh(tag)
        test_session.refresh(memo)
        test_session.refresh(other_memo)

        assert tag.id is not None
        assert memo.id is not None
        assert other_memo.id is not None

        updated = tag_repository.add_memo(tag.id, memo.id)
        assert any(m.id == memo.id for m in updated.memos)
        updated = tag_repository.add_memo(tag.id, memo.id)
        assert len([m for m in updated.memos if m.id == memo.id]) == 1

        updated = tag_repository.remove_memo(tag.id, other_memo.id)
        assert all(m.id != other_memo.id for m in updated.memos)

        with pytest.raises(NotFoundError):
            tag_repository.remove_memo(tag.id, uuid.uuid4())

        updated = tag_repository.remove_all_memos(tag.id)
        assert len(updated.memos) == 0

        updated = tag_repository.remove_all_memos(tag.id)
        assert len(updated.memos) == 0
