"""BaseRepositoryのテストケース

このモジュールは、BaseRepositoryクラスの基本的なCRUD操作を
テストするためのテストケースを提供します。

テスト対象：
- create: 新しいエンティティの作成
- get_by_id: IDによるエンティティの取得
- get_all: 全エンティティの取得
- update: エンティティの更新
- delete: エンティティの削除
- エラーハンドリング
"""

import uuid

from sqlmodel import Session

from logic.repositories.task import TaskRepository
from models import TaskStatus
from tests.logic.helpers import create_test_task, create_test_task_create


class TestBaseRepository:
    """BaseRepositoryの基本的なCRUD操作をテストするクラス

    TaskRepositoryを通じてBaseRepositoryの機能をテストします。
    """

    def test_create_success(self, task_repository: TaskRepository) -> None:
        """正常系: 新しいタスクの作成"""
        # テストデータの準備
        task_create = create_test_task_create(title="新しいタスク", description="作成テスト用のタスクです")

        # 実行
        created_task = task_repository.create(task_create)

        # 検証
        assert created_task is not None
        assert created_task.id is not None
        assert created_task.title == "新しいタスク"
        assert created_task.description == "作成テスト用のタスクです"
        assert created_task.status == TaskStatus.INBOX

    def test_get_by_id_success(self, task_repository: TaskRepository, test_session: Session) -> None:
        """正常系: IDによるタスクの取得"""
        # テストデータの準備
        test_task = create_test_task(title="取得テスト")
        test_session.add(test_task)
        test_session.commit()
        test_session.refresh(test_task)

        # test_task.idがNoneでないことを確認
        assert test_task.id is not None

        # 実行
        retrieved_task = task_repository.get_by_id(test_task.id)

        # 検証
        assert retrieved_task is not None
        assert retrieved_task.id == test_task.id
        assert retrieved_task.title == "取得テスト"

    def test_get_by_id_not_found(self, task_repository: TaskRepository) -> None:
        """異常系: 存在しないIDでの取得"""
        # 存在しないIDを指定
        non_existent_id = uuid.uuid4()

        # 実行
        result = task_repository.get_by_id(non_existent_id)

        # 検証
        assert result is None

    def test_get_all_empty(self, task_repository: TaskRepository) -> None:
        """正常系: 空のデータベースからの全件取得"""
        # 実行
        all_tasks = task_repository.get_all()

        # 検証
        assert all_tasks == []

    def test_get_all_with_data(self, task_repository: TaskRepository, test_session: Session) -> None:
        """正常系: データが存在する場合の全件取得"""
        # テストデータの準備
        task1 = create_test_task(title="タスク1")
        task2 = create_test_task(title="タスク2")
        task3 = create_test_task(title="タスク3")

        test_session.add_all([task1, task2, task3])
        test_session.commit()

        expected_count = 3

        # 実行
        all_tasks = task_repository.get_all()

        # 検証
        assert len(all_tasks) == expected_count
        task_titles = {task.title for task in all_tasks}
        assert task_titles == {"タスク1", "タスク2", "タスク3"}

    def test_update_success(self, task_repository: TaskRepository, test_session: Session) -> None:
        """正常系: タスクの更新"""
        # テストデータの準備
        test_task = create_test_task(title="更新前タスク", description="更新前の説明")
        test_session.add(test_task)
        test_session.commit()
        test_session.refresh(test_task)

        # test_task.idがNoneでないことを確認
        assert test_task.id is not None

        # 更新データの準備
        from models import TaskUpdate

        update_data = TaskUpdate(title="更新後タスク", status=TaskStatus.NEXT_ACTION)

        # 実行
        updated_task = task_repository.update(test_task.id, update_data)

        # 検証
        assert updated_task is not None
        assert updated_task.id == test_task.id
        assert updated_task.title == "更新後タスク"
        assert updated_task.status == TaskStatus.NEXT_ACTION
        # 更新されていない項目は元の値を保持
        assert updated_task.description == "更新前の説明"

    def test_update_not_found(self, task_repository: TaskRepository) -> None:
        """異常系: 存在しないIDでの更新"""
        # 存在しないIDを指定
        non_existent_id = uuid.uuid4()

        # 更新データの準備
        from models import TaskUpdate

        update_data = TaskUpdate(title="存在しないタスク")

        # 実行
        result = task_repository.update(non_existent_id, update_data)

        # 検証
        assert result is None

    def test_delete_success(self, task_repository: TaskRepository, test_session: Session) -> None:
        """正常系: タスクの削除"""
        # テストデータの準備
        test_task = create_test_task(title="削除対象タスク")
        test_session.add(test_task)
        test_session.commit()
        test_session.refresh(test_task)

        # test_task.idがNoneでないことを確認
        assert test_task.id is not None

        # 実行
        result = task_repository.delete(test_task.id)

        # 検証
        assert result is True

        # 削除されたことを確認
        deleted_task = task_repository.get_by_id(test_task.id)
        assert deleted_task is None

    def test_delete_not_found(self, task_repository: TaskRepository) -> None:
        """異常系: 存在しないIDでの削除"""
        # 存在しないIDを指定
        non_existent_id = uuid.uuid4()

        # 実行
        result = task_repository.delete(non_existent_id)

        # 検証
        assert result is False

    def test_create_with_empty_title(self, task_repository: TaskRepository) -> None:
        """現在の実装では空のタイトルでもタスクが作成可能

        Note: 将来的にはタイトルのバリデーションを追加し、
              空のタイトルでの作成を防ぐ仕様に変更する可能性があります。
        """
        # 空のタイトルでタスク作成データを準備
        task_create = create_test_task_create(title="")

        # 実行
        created_task = task_repository.create(task_create)

        # 検証: 現在の実装では空タイトルでも作成可能
        assert created_task is not None
        assert created_task.title == ""
        assert isinstance(created_task.id, uuid.UUID)

    def test_multiple_operations_consistency(self, task_repository: TaskRepository, test_session: Session) -> None:
        """統合テスト: 複数操作の一貫性確認"""
        # 1. 作成
        task_create = create_test_task_create(title="統合テストタスク")
        created_task = task_repository.create(task_create)
        assert created_task.title == "統合テストタスク"
        assert created_task.id is not None

        # 2. 取得
        retrieved_task = task_repository.get_by_id(created_task.id)
        assert retrieved_task is not None
        assert retrieved_task.title == "統合テストタスク"

        # 3. 更新
        from models import TaskUpdate

        update_data = TaskUpdate(status=TaskStatus.COMPLETED)
        updated_task = task_repository.update(created_task.id, update_data)
        assert updated_task is not None
        assert updated_task.status == TaskStatus.COMPLETED

        # 4. 削除
        delete_result = task_repository.delete(created_task.id)
        assert delete_result is True

        # 5. 削除後確認
        final_check = task_repository.get_by_id(created_task.id)
        assert final_check is None
