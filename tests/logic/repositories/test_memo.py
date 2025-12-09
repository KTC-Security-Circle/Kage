"""メモリポジトリのテスト（現行API対応）"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:  # 型チェック時のみインポート
    from sqlmodel import Session

from errors import NotFoundError, RepositoryError
from logic.repositories.memo import MemoRepository
from models import Memo, MemoCreate, MemoStatus, MemoUpdate, Tag
from tests.logic.helpers import create_test_task

EXPECTED_MEMO_PAIR_COUNT = 2


class TestMemoRepository:
    """MemoRepositoryのテストクラス"""

    def test_create_memo_success(self, test_session: Session) -> None:
        """メモ作成のテスト（正常系）"""
        memo_repo = MemoRepository(test_session)
        memo_data = MemoCreate(
            title="テストメモ",
            content="テスト用のメモ内容です",
            status=MemoStatus.INBOX,
        )

        created_memo = memo_repo.create(memo_data)

        assert created_memo is not None
        assert created_memo.title == "テストメモ"
        assert created_memo.content == "テスト用のメモ内容です"
        assert created_memo.id is not None

    def test_get_by_id_success(self, test_session: Session) -> None:
        """IDでメモ取得のテスト（正常系）"""
        memo = Memo(
            id=uuid.uuid4(),
            title="取得テスト",
            content="取得テスト用メモ",
            status=MemoStatus.INBOX,
        )
        test_session.add(memo)
        test_session.commit()
        test_session.refresh(memo)

        memo_repo = MemoRepository(test_session)
        assert memo.id is not None
        retrieved_memo = memo_repo.get_by_id(memo.id)

        assert retrieved_memo is not None
        assert retrieved_memo.id == memo.id
        assert retrieved_memo.title == "取得テスト"
        assert retrieved_memo.content == "取得テスト用メモ"

    def test_get_by_id_not_found(self, test_session: Session) -> None:
        """IDでメモ取得のテスト（見つからない場合）"""
        memo_repo = MemoRepository(test_session)
        non_existent_id = uuid.uuid4()

        with pytest.raises(NotFoundError):
            memo_repo.get_by_id(non_existent_id)

    def test_get_all_memos(self, test_session: Session) -> None:
        """全メモ取得のテスト"""
        memo1 = Memo(
            id=uuid.uuid4(),
            title="メモ1タイトル",
            content="メモ1",
            status=MemoStatus.INBOX,
        )
        memo2 = Memo(
            id=uuid.uuid4(),
            title="メモ2タイトル",
            content="メモ2",
            status=MemoStatus.INBOX,
        )
        test_session.add_all([memo1, memo2])
        test_session.commit()

        memo_repo = MemoRepository(test_session)
        all_memos = memo_repo.get_all()

        assert len(all_memos) == EXPECTED_MEMO_PAIR_COUNT
        memo_contents = [m.content for m in all_memos]
        assert "メモ1" in memo_contents
        assert "メモ2" in memo_contents

    def test_update_memo_success(self, test_session: Session) -> None:
        """メモ更新のテスト（正常系）"""
        memo = Memo(
            id=uuid.uuid4(),
            title="更新前",
            content="更新前のメモ",
            status=MemoStatus.INBOX,
        )
        test_session.add(memo)
        test_session.commit()
        test_session.refresh(memo)

        memo_repo = MemoRepository(test_session)
        update_data = MemoUpdate(content="更新後のメモ")

        assert memo.id is not None
        updated_memo = memo_repo.update(memo.id, update_data)

        assert updated_memo is not None
        assert updated_memo.content == "更新後のメモ"
        assert updated_memo.id == memo.id

    def test_update_memo_not_found(self, test_session: Session) -> None:
        """メモ更新のテスト（見つからない場合）"""
        memo_repo = MemoRepository(test_session)
        non_existent_id = uuid.uuid4()
        update_data = MemoUpdate(content="更新後のメモ")

        with pytest.raises(RepositoryError):
            memo_repo.update(non_existent_id, update_data)

    def test_delete_memo_success(self, test_session: Session) -> None:
        """メモ削除のテスト（正常系）"""
        memo = Memo(
            id=uuid.uuid4(),
            title="削除テスト",
            content="削除テスト用メモ",
            status=MemoStatus.INBOX,
        )
        test_session.add(memo)
        test_session.commit()
        test_session.refresh(memo)

        memo_repo = MemoRepository(test_session)
        assert memo.id is not None
        success = memo_repo.delete(memo.id)
        assert success is True

        assert memo.id is not None
        with pytest.raises(NotFoundError):
            memo_repo.get_by_id(memo.id)

    def test_search_by_content(self, test_session: Session) -> None:
        """内容で検索のテスト"""
        memo1 = Memo(
            id=uuid.uuid4(),
            title="Pythonの学習",
            content="Pythonのプログラミング学習",
            status=MemoStatus.INBOX,
        )
        memo2 = Memo(
            id=uuid.uuid4(),
            title="JS開発",
            content="JavaScriptとReactの開発",
            status=MemoStatus.INBOX,
        )
        memo3 = Memo(
            id=uuid.uuid4(),
            title="DB基礎",
            content="データベース設計の基礎",
            status=MemoStatus.INBOX,
        )
        test_session.add_all([memo1, memo2, memo3])
        test_session.commit()

        memo_repo = MemoRepository(test_session)

        python_memos = memo_repo.search_by_content("Python")
        programming_memos = memo_repo.search_by_content("プログラミング")
        development_memos = memo_repo.search_by_content("開発")

        assert len(python_memos) == 1
        assert python_memos[0].content == "Pythonのプログラミング学習"

        assert len(programming_memos) == 1
        assert programming_memos[0].content == "Pythonのプログラミング学習"

        assert len(development_memos) == 1
        assert development_memos[0].content == "JavaScriptとReactの開発"

        with pytest.raises(NotFoundError):
            memo_repo.search_by_content("存在しないキーワード")

    def test_search_by_content_case_insensitive(self, test_session: Session) -> None:
        """内容で検索のテスト（大文字小文字を区別しない）"""
        memo = Memo(
            id=uuid.uuid4(),
            title="Python Tutorial",
            content="Python Programming Tutorial",
            status=MemoStatus.INBOX,
        )
        test_session.add(memo)
        test_session.commit()

        memo_repo = MemoRepository(test_session)

        lowercase_search = memo_repo.search_by_content("python")
        uppercase_search = memo_repo.search_by_content("PYTHON")
        mixed_case_search = memo_repo.search_by_content("PyThOn")

        assert len(lowercase_search) == 1
        assert len(uppercase_search) == 1
        assert len(mixed_case_search) == 1

        assert lowercase_search[0].content == "Python Programming Tutorial"
        assert uppercase_search[0].content == "Python Programming Tutorial"
        assert mixed_case_search[0].content == "Python Programming Tutorial"

    def test_list_unprocessed_memos(self, test_session: Session) -> None:
        """棚卸し対象のみが選ばれることを確認する。"""

        memo_repo = MemoRepository(test_session)
        base_time = datetime.now() - timedelta(days=1)

        inbox_memo = Memo(
            id=uuid.uuid4(),
            title="Inbox",
            content="整理対象",
            status=MemoStatus.INBOX,
        )
        inbox_memo.created_at = base_time

        idea_memo = Memo(
            id=uuid.uuid4(),
            title="Idea",
            content="Someday 候補",
            status=MemoStatus.IDEA,
        )
        idea_memo.created_at = base_time

        memo_with_task = Memo(
            id=uuid.uuid4(),
            title="Linked",
            content="すでにタスク化",
            status=MemoStatus.INBOX,
        )
        memo_with_task.created_at = base_time
        linked_task = create_test_task()
        memo_with_task.tasks.append(linked_task)

        test_session.add_all([inbox_memo, idea_memo, memo_with_task, linked_task])
        test_session.commit()

        results = memo_repo.list_unprocessed_memos(created_after=None)
        titles = {memo.title for memo in results}

        assert titles == {"Inbox", "Idea"}

    def test_list_by_status_with_details_and_empty(self, test_session: Session) -> None:
        """list_by_status の with_details 分岐と空結果の NotFound を検証する"""
        memo_repo = MemoRepository(test_session)

        # INBOX のメモを1件用意
        inbox_memo = Memo(
            id=uuid.uuid4(),
            title="受信箱メモ",
            content="詳細読み込みテスト",
            status=MemoStatus.INBOX,
        )
        test_session.add(inbox_memo)
        test_session.commit()

        # with_details=True で取得可能
        results = memo_repo.list_by_status(MemoStatus.INBOX, with_details=True)
        assert any(m.id == inbox_memo.id for m in results)

        # ACTIVE は存在しないため NotFoundError
        with pytest.raises(NotFoundError):
            memo_repo.list_by_status(MemoStatus.ACTIVE)

    def test_list_by_tag_with_details_and_not_found(self, test_session: Session) -> None:
        """list_by_tag の with_details 分岐と未関連/空結果の NotFound を検証する"""
        memo_repo = MemoRepository(test_session)

        # タグとメモを作成し、関連付け
        tag = Tag(id=uuid.uuid4(), name="学習")
        memo = Memo(
            id=uuid.uuid4(),
            title="Python学習",
            content="SQLModel",
            status=MemoStatus.INBOX,
        )
        test_session.add_all([tag, memo])
        test_session.commit()

        # add_tag でリンクを作成
        assert memo.id is not None
        assert tag.id is not None
        memo_repo.add_tag(memo.id, tag.id)

        # with_details 分岐
        results = memo_repo.list_by_tag(tag.id, with_details=True)
        assert len(results) == 1
        assert results[0].id == memo.id

        # 別タグ（存在するが未関連）では NotFoundError
        other_tag = Tag(id=uuid.uuid4(), name="未関連")
        test_session.add(other_tag)
        test_session.commit()
        assert other_tag.id is not None
        with pytest.raises(NotFoundError):
            memo_repo.list_by_tag(other_tag.id)

    def test_add_remove_tag_and_task_branches(self, test_session: Session) -> None:
        """タグ/タスクの追加・重複・未関連削除・存在しないIDでの NotFound を検証する"""
        memo_repo = MemoRepository(test_session)

        # メモ/タグ/タスクを作成
        tag = Tag(id=uuid.uuid4(), name="重要")
        memo = Memo(
            id=uuid.uuid4(),
            title="関連テスト",
            content="",
            status=MemoStatus.INBOX,
        )
        task = create_test_task(title="関連タスク")
        test_session.add_all([tag, memo, task])
        test_session.commit()

        assert memo.id is not None
        assert tag.id is not None
        assert task.id is not None

        # add_tag で関連付け、重複追加しても重複しない
        memo_repo.add_tag(memo.id, tag.id)
        memo_repo.add_tag(memo.id, tag.id)
        updated = memo_repo.get_by_id(memo.id, with_details=True)
        assert len(updated.tags) == 1
        assert updated.tags[0].id == tag.id

        # remove_tag: 未関連の別タグは例外にならない（存在する場合）
        other_tag = Tag(id=uuid.uuid4(), name="別")
        test_session.add(other_tag)
        test_session.commit()
        assert other_tag.id is not None
        memo_repo.remove_tag(memo.id, other_tag.id)

        # remove_tag: 存在しないタグIDは NotFoundError
        with pytest.raises(NotFoundError):
            memo_repo.remove_tag(memo.id, uuid.uuid4())

        # add_task で関連付け、重複追加しても重複しない
        memo_repo.add_task(memo.id, task.id)
        memo_repo.add_task(memo.id, task.id)
        updated = memo_repo.get_by_id(memo.id, with_details=True)
        assert len(updated.tasks) == 1
        assert updated.tasks[0].id == task.id

        # remove_task: 未関連の別タスクは例外にならない（存在する場合）
        other_task = create_test_task(title="未関連")
        test_session.add(other_task)
        test_session.commit()
        assert other_task.id is not None
        memo_repo.remove_task(memo.id, other_task.id)

        # remove_task: 存在しないタスクIDは NotFoundError
        with pytest.raises(NotFoundError):
            memo_repo.remove_task(memo.id, uuid.uuid4())

    def test_search_by_title_with_details_and_not_found(self, test_session: Session) -> None:
        """search_by_title の with_details 分岐と NotFound を検証する"""
        memo_repo = MemoRepository(test_session)
        memo = Memo(
            id=uuid.uuid4(),
            title="Flet UI",
            content="",
            status=MemoStatus.INBOX,
        )
        test_session.add(memo)
        test_session.commit()

        results = memo_repo.search_by_title("FLET", with_details=True)
        assert len(results) == 1
        assert results[0].id == memo.id

        with pytest.raises(NotFoundError):
            memo_repo.search_by_title("見つからない")
