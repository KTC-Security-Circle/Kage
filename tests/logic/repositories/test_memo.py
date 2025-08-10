"""メモリポジトリのテスト"""

import uuid

import pytest
from sqlmodel import Session

from logic.repositories.memo import MemoRepository
from models import Memo, MemoCreate, MemoUpdate
from tests.logic.helpers import create_test_task


class TestMemoRepository:
    """MemoRepositoryのテストクラス"""

    def test_create_memo_success(self, test_session: Session) -> None:
        """メモ作成のテスト（正常系）"""
        # [AI GENERATED] テスト用タスクを作成してデータベースに保存
        task = create_test_task()
        test_session.add(task)
        test_session.commit()
        test_session.refresh(task)

        memo_repo = MemoRepository(test_session)
        memo_data = MemoCreate(
            content="テスト用のメモ内容です",
            task_id=task.id,
        )

        # Act
        created_memo = memo_repo.create(memo_data)

        # Assert
        assert created_memo is not None
        assert created_memo.content == "テスト用のメモ内容です"
        assert created_memo.task_id == task.id
        assert created_memo.id is not None

    def test_get_by_id_success(self, test_session: Session) -> None:
        """IDでメモ取得のテスト（正常系）"""
        # [AI GENERATED] テスト用タスクとメモを作成
        task = create_test_task()
        test_session.add(task)
        test_session.commit()
        test_session.refresh(task)

        memo = Memo(
            id=uuid.uuid4(),
            content="取得テスト用メモ",
            task_id=task.id,
        )
        test_session.add(memo)
        test_session.commit()
        test_session.refresh(memo)

        memo_repo = MemoRepository(test_session)

        # Act
        retrieved_memo = memo_repo.get_by_id(memo.id)

        # Assert
        assert retrieved_memo is not None
        assert retrieved_memo.id == memo.id
        assert retrieved_memo.content == "取得テスト用メモ"
        assert retrieved_memo.task_id == task.id

    def test_get_by_id_not_found(self, test_session: Session) -> None:
        """IDでメモ取得のテスト（見つからない場合）"""
        memo_repo = MemoRepository(test_session)
        non_existent_id = uuid.uuid4()

        # Act
        result = memo_repo.get_by_id(non_existent_id)

        # Assert
        assert result is None

    def test_get_all_memos(self, test_session: Session) -> None:
        """全メモ取得のテスト"""
        # [AI GENERATED] テスト用タスクを作成
        task1 = create_test_task("タスク1")
        task2 = create_test_task("タスク2")
        test_session.add_all([task1, task2])
        test_session.commit()
        test_session.refresh(task1)
        test_session.refresh(task2)

        # [AI GENERATED] 複数のメモを作成
        memo1 = Memo(
            id=uuid.uuid4(),
            content="メモ1",
            task_id=task1.id,
        )
        memo2 = Memo(
            id=uuid.uuid4(),
            content="メモ2",
            task_id=task2.id,
        )
        test_session.add_all([memo1, memo2])
        test_session.commit()

        memo_repo = MemoRepository(test_session)

        # Act
        all_memos = memo_repo.get_all()

        # Assert
        assert len(all_memos) == 2
        memo_contents = [memo.content for memo in all_memos]
        assert "メモ1" in memo_contents
        assert "メモ2" in memo_contents

    def test_update_memo_success(self, test_session: Session) -> None:
        """メモ更新のテスト（正常系）"""
        # [AI GENERATED] テスト用タスクとメモを作成
        task = create_test_task()
        test_session.add(task)
        test_session.commit()
        test_session.refresh(task)

        memo = Memo(
            id=uuid.uuid4(),
            content="更新前のメモ",
            task_id=task.id,
        )
        test_session.add(memo)
        test_session.commit()
        test_session.refresh(memo)

        memo_repo = MemoRepository(test_session)
        update_data = MemoUpdate(content="更新後のメモ")

        # Act
        updated_memo = memo_repo.update(memo.id, update_data)

        # Assert
        assert updated_memo is not None
        assert updated_memo.content == "更新後のメモ"
        assert updated_memo.id == memo.id
        assert updated_memo.task_id == task.id

    def test_update_memo_not_found(self, test_session: Session) -> None:
        """メモ更新のテスト（見つからない場合）"""
        memo_repo = MemoRepository(test_session)
        non_existent_id = uuid.uuid4()
        update_data = MemoUpdate(content="更新後のメモ")

        # Act
        result = memo_repo.update(non_existent_id, update_data)

        # Assert
        assert result is None

    def test_delete_memo_success(self, test_session: Session) -> None:
        """メモ削除のテスト（正常系）"""
        # [AI GENERATED] テスト用タスクとメモを作成
        task = create_test_task()
        test_session.add(task)
        test_session.commit()
        test_session.refresh(task)

        memo = Memo(
            id=uuid.uuid4(),
            content="削除テスト用メモ",
            task_id=task.id,
        )
        test_session.add(memo)
        test_session.commit()
        test_session.refresh(memo)

        memo_repo = MemoRepository(test_session)

        # Act
        success = memo_repo.delete(memo.id)

        # Assert
        assert success is True
        
        # [AI GENERATED] 削除されたことを確認
        deleted_memo = memo_repo.get_by_id(memo.id)
        assert deleted_memo is None

    def test_delete_memo_not_found(self, test_session: Session) -> None:
        """メモ削除のテスト（見つからない場合）"""
        memo_repo = MemoRepository(test_session)
        non_existent_id = uuid.uuid4()

        # Act
        success = memo_repo.delete(non_existent_id)

        # Assert
        assert success is False

    def test_get_by_task_id(self, test_session: Session) -> None:
        """タスクIDでメモ取得のテスト"""
        # [AI GENERATED] テスト用タスクを作成
        task1 = create_test_task("タスク1")
        task2 = create_test_task("タスク2")
        test_session.add_all([task1, task2])
        test_session.commit()
        test_session.refresh(task1)
        test_session.refresh(task2)

        # [AI GENERATED] タスク1に複数のメモ、タスク2に1つのメモを作成
        memo1_1 = Memo(
            id=uuid.uuid4(),
            content="タスク1のメモ1",
            task_id=task1.id,
        )
        memo1_2 = Memo(
            id=uuid.uuid4(),
            content="タスク1のメモ2",
            task_id=task1.id,
        )
        memo2_1 = Memo(
            id=uuid.uuid4(),
            content="タスク2のメモ1",
            task_id=task2.id,
        )
        test_session.add_all([memo1_1, memo1_2, memo2_1])
        test_session.commit()

        memo_repo = MemoRepository(test_session)

        # Act
        task1_memos = memo_repo.get_by_task_id(task1.id)
        task2_memos = memo_repo.get_by_task_id(task2.id)

        # Assert
        assert len(task1_memos) == 2
        assert len(task2_memos) == 1
        
        task1_contents = [memo.content for memo in task1_memos]
        assert "タスク1のメモ1" in task1_contents
        assert "タスク1のメモ2" in task1_contents
        
        assert task2_memos[0].content == "タスク2のメモ1"

    def test_get_by_task_id_empty(self, test_session: Session) -> None:
        """タスクIDでメモ取得のテスト（存在しないタスクの場合）"""
        memo_repo = MemoRepository(test_session)
        non_existent_task_id = uuid.uuid4()

        # Act
        memos = memo_repo.get_by_task_id(non_existent_task_id)

        # Assert
        assert len(memos) == 0

    def test_search_by_content(self, test_session: Session) -> None:
        """内容で検索のテスト"""
        # [AI GENERATED] テスト用タスクを作成
        task = create_test_task()
        test_session.add(task)
        test_session.commit()
        test_session.refresh(task)

        # [AI GENERATED] 様々な内容のメモを作成
        memo1 = Memo(
            id=uuid.uuid4(),
            content="Pythonのプログラミング学習",
            task_id=task.id,
        )
        memo2 = Memo(
            id=uuid.uuid4(),
            content="JavaScriptとReactの開発",
            task_id=task.id,
        )
        memo3 = Memo(
            id=uuid.uuid4(),
            content="データベース設計の基礎",
            task_id=task.id,
        )
        test_session.add_all([memo1, memo2, memo3])
        test_session.commit()

        memo_repo = MemoRepository(test_session)

        # Act
        python_memos = memo_repo.search_by_content("Python")
        programming_memos = memo_repo.search_by_content("プログラミング")
        development_memos = memo_repo.search_by_content("開発")
        empty_result = memo_repo.search_by_content("存在しないキーワード")

        # Assert
        assert len(python_memos) == 1
        assert python_memos[0].content == "Pythonのプログラミング学習"
        
        assert len(programming_memos) == 1
        assert programming_memos[0].content == "Pythonのプログラミング学習"
        
        assert len(development_memos) == 1
        assert development_memos[0].content == "JavaScriptとReactの開発"
        
        assert len(empty_result) == 0

    def test_search_by_content_case_insensitive(self, test_session: Session) -> None:
        """内容で検索のテスト（大文字小文字を区別しない）"""
        # [AI GENERATED] テスト用タスクとメモを作成
        task = create_test_task()
        test_session.add(task)
        test_session.commit()
        test_session.refresh(task)

        memo = Memo(
            id=uuid.uuid4(),
            content="Python Programming Tutorial",
            task_id=task.id,
        )
        test_session.add(memo)
        test_session.commit()

        memo_repo = MemoRepository(test_session)

        # Act
        lowercase_search = memo_repo.search_by_content("python")
        uppercase_search = memo_repo.search_by_content("PYTHON")
        mixed_case_search = memo_repo.search_by_content("PyThOn")

        # Assert
        assert len(lowercase_search) == 1
        assert len(uppercase_search) == 1
        assert len(mixed_case_search) == 1
        
        assert lowercase_search[0].content == "Python Programming Tutorial"
        assert uppercase_search[0].content == "Python Programming Tutorial"
        assert mixed_case_search[0].content == "Python Programming Tutorial"