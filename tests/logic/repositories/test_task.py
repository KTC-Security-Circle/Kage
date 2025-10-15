"""TaskRepositoryのテストケース（現行API対応）

このモジュールは、TaskRepositoryクラスのタスク固有の操作をテストする。

対象：
- list_by_project: プロジェクトIDによるタスク一覧
- list_by_status: ステータス別タスク一覧
- search_by_title: タイトル検索

注意：
- BaseRepository方針により、該当データがない場合は NotFoundError を送出する
"""

import uuid
from datetime import date

import pytest
from sqlmodel import Session

from errors import NotFoundError
from logic.repositories.task import TaskRepository
from models import Task, TaskStatus


def create_test_task(
    title: str = "テストタスク",
    description: str | None = None,
    status: TaskStatus = TaskStatus.TODO,
    project_id: uuid.UUID | None = None,
    due_date: date | None = None,
) -> Task:
    """テスト用のTaskオブジェクトを作成する

    Args:
        title: タスクのタイトル
        description: タスクの説明
        status: タスクのステータス
        project_id: プロジェクトID
        due_date: 期限日

    Returns:
        作成されたTaskオブジェクト
    """
    return Task(
        title=title,
        description=description or "",
        status=status,
        project_id=project_id,
        due_date=due_date,
    )


class TestTaskRepository:
    """TaskRepositoryのタスク固有機能をテストするクラス"""

    def test_get_by_project_id_success(self, task_repository: TaskRepository, test_session: Session) -> None:
        """正常系: プロジェクトIDによるタスク取得"""
        # テストデータの準備
        project_id = uuid.uuid4()
        task1 = create_test_task(title="プロジェクトタスク1", project_id=project_id)
        task2 = create_test_task(title="プロジェクトタスク2", project_id=project_id)
        task3 = create_test_task(title="別プロジェクトタスク")  # 別プロジェクト

        test_session.add_all([task1, task2, task3])
        test_session.commit()

        # 実行
        project_tasks = task_repository.list_by_project(project_id)

        # 検証
        expected_task_count = 2
        assert len(project_tasks) == expected_task_count
        task_titles = {task.title for task in project_tasks}
        assert task_titles == {"プロジェクトタスク1", "プロジェクトタスク2"}

    def test_list_by_project_not_found(self, task_repository: TaskRepository) -> None:
        """異常系: 存在しないプロジェクトの一覧取得は NotFoundError"""
        non_existent_project_id = uuid.uuid4()
        with pytest.raises(NotFoundError):
            task_repository.list_by_project(non_existent_project_id)

    def test_list_by_status_success(self, task_repository: TaskRepository, test_session: Session) -> None:
        """正常系: ステータス別タスク取得"""
        # テストデータの準備
        todo_task = create_test_task(title="TODOタスク", status=TaskStatus.TODO)
        progress_task1 = create_test_task(title="進行中1", status=TaskStatus.PROGRESS)
        progress_task2 = create_test_task(title="進行中2", status=TaskStatus.PROGRESS)
        completed_task = create_test_task(title="完了タスク", status=TaskStatus.COMPLETED)

        test_session.add_all([todo_task, progress_task1, progress_task2, completed_task])
        test_session.commit()

        # 実行
        progress_tasks = task_repository.list_by_status(TaskStatus.PROGRESS)

        # 検証
        expected_task_count = 2
        assert len(progress_tasks) == expected_task_count
        task_titles = {task.title for task in progress_tasks}
        assert task_titles == {"進行中1", "進行中2"}

    def test_list_by_status_not_found(self, task_repository: TaskRepository) -> None:
        """異常系: 該当ステータスが存在しない場合は NotFoundError"""
        with pytest.raises(NotFoundError):
            task_repository.list_by_status(TaskStatus.WAITING)

    # 期限日やサブタスク関連は現行TaskRepository未実装のため省略

    def test_search_by_title(self, task_repository: TaskRepository, test_session: Session) -> None:
        """正常系: タイトルによる検索"""
        # テストデータの準備
        task1 = create_test_task(title="プロジェクトの設計")
        task2 = create_test_task(title="プロジェクトの実装")
        task3 = create_test_task(title="テスト実行")

        test_session.add_all([task1, task2, task3])
        test_session.commit()

        # 実行
        search_results = task_repository.search_by_title("プロジェクト")

        # 検証
        expected_result_count = 2
        assert len(search_results) == expected_result_count
        task_titles = {task.title for task in search_results}
        assert task_titles == {"プロジェクトの設計", "プロジェクトの実装"}

    def test_search_by_title_case_insensitive(self, task_repository: TaskRepository, test_session: Session) -> None:
        """正常系: タイトル検索の大文字小文字不区別"""
        # テストデータの準備
        task = create_test_task(title="Project Management")
        test_session.add(task)
        test_session.commit()

        # 実行（小文字で検索）
        search_results = task_repository.search_by_title("project")

        # 検証
        assert len(search_results) == 1
        assert search_results[0].title == "Project Management"

    # 旧 get_inbox/get_next_action/get_completed/get_overdue は現行実装に無いため削除
