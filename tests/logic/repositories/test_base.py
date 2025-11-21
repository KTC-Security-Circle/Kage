"""BaseRepositoryのテスト項目（現行仕様）

このモジュールは、BaseRepository（TaskRepository経由）のCRUDと取得系、
および例外方針（errors.pyに準拠）を検証する。

テスト項目（実装前の項目定義）:
- create: 正常作成でモデルが返る（必要フィールドのみでOK）
- get_by_id:
    - 正常: 既存IDで取得できる
    - 異常: 存在しないIDは NotFoundError を送出
- get_all:
    - 正常: データがある場合に一覧取得できる
    - 異常: データが0件のとき NotFoundError を送出（[]ではない）
- update:
    - 正常: 差分更新が反映される
    - 異常: 存在しないID指定時は RepositoryError（内部でNotFoundが集約）
- delete:
    - 正常: True を返す（削除後に get_by_id は NotFoundError）
    - 異常: 存在しないID指定時は False を返す
- eager load:
    - with_details=True で関連（tags/project/memo等）にアクセス可能で例外にならない
- find/list API（必要に応じてTaskRepositoryの search_by_title / list_by_status を使用）:
    - 条件一致時: リストが返る
    - 条件不一致時: NotFoundError を送出

注記:
- BaseRepository._gets_by_statement は0件時に NotFoundError を送出するため、
    空リストを期待する旧テストは例外期待に置き換える。
- update の存在しないIDは check_exists の NotFoundError が try 範囲で捕捉され
    RepositoryError に集約される実装のため、RepositoryError を期待する。
"""

import uuid

import pytest
from sqlmodel import Session

from errors import NotFoundError, RepositoryError
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
        assert created_task.status == TaskStatus.TODO

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
        """異常系: 存在しないIDでの取得は NotFoundError"""
        non_existent_id = uuid.uuid4()
        with pytest.raises(NotFoundError):
            task_repository.get_by_id(non_existent_id)

    def test_get_all_empty(self, task_repository: TaskRepository) -> None:
        """異常系: データ0件時 get_all は NotFoundError"""
        with pytest.raises(NotFoundError):
            task_repository.get_all()

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

        update_data = TaskUpdate(title="更新後タスク", status=TaskStatus.PROGRESS)

        # 実行
        updated_task = task_repository.update(test_task.id, update_data)

        # 検証
        assert updated_task is not None
        assert updated_task.id == test_task.id
        assert updated_task.title == "更新後タスク"
        assert updated_task.status == TaskStatus.PROGRESS
        # 更新されていない項目は元の値を保持
        assert updated_task.description == "更新前の説明"

    def test_update_not_found(self, task_repository: TaskRepository) -> None:
        """異常系: 存在しないIDでの更新は RepositoryError 集約"""
        non_existent_id = uuid.uuid4()
        from models import TaskUpdate

        update_data = TaskUpdate(title="存在しないタスク")
        with pytest.raises(RepositoryError):
            task_repository.update(non_existent_id, update_data)

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

        # 削除されたことを確認（NotFoundError）
        with pytest.raises(NotFoundError):
            task_repository.get_by_id(test_task.id)

    def test_delete_not_found(self, task_repository: TaskRepository) -> None:
        """異常系: 存在しないIDでの削除"""
        # 存在しないIDを指定
        non_existent_id = uuid.uuid4()

        # 実行 / 検証
        assert task_repository.delete(non_existent_id) is False

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
        with pytest.raises(NotFoundError):
            task_repository.get_by_id(created_task.id)
