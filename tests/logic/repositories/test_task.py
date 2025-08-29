"""TaskRepositoryのテストケース

このモジュールは、TaskRepositoryクラスのタスク固有の操作を
テストするためのテストケースを提供します。

テスト対象：
- get_by_project_id: プロジェクトIDによるタスク取得
- get_by_status: ステータス別タスク取得
- get_by_due_date: 期限日別タスク取得
- get_subtasks: サブタスク取得
- search_by_title: タイトル検索
- get_inbox_tasks, get_next_action_tasks, get_completed_tasks
- get_overdue_tasks: 期限切れタスク取得
"""

import uuid
from datetime import UTC, date, datetime, timedelta

from sqlmodel import Session

from logic.repositories.task import TaskRepository
from models import Task, TaskStatus


def create_test_task(
    title: str = "テストタスク",
    description: str | None = None,
    status: TaskStatus = TaskStatus.INBOX,
    project_id: uuid.UUID | None = None,
    parent_id: uuid.UUID | None = None,
    due_date: date | None = None,
) -> Task:
    """テスト用のTaskオブジェクトを作成する

    Args:
        title: タスクのタイトル
        description: タスクの説明
        status: タスクのステータス
        project_id: プロジェクトID
        parent_id: 親タスクID
        due_date: 期限日

    Returns:
        作成されたTaskオブジェクト
    """
    return Task(
        title=title,
        description=description or "",
        status=status,
        project_id=project_id,
        parent_id=parent_id,
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
        project_tasks = task_repository.get_by_project_id(project_id)

        # 検証
        expected_task_count = 2
        assert len(project_tasks) == expected_task_count
        task_titles = {task.title for task in project_tasks}
        assert task_titles == {"プロジェクトタスク1", "プロジェクトタスク2"}

    def test_get_by_project_id_empty(self, task_repository: TaskRepository) -> None:
        """正常系: 存在しないプロジェクトIDでの取得"""
        # 存在しないプロジェクトIDを指定
        non_existent_project_id = uuid.uuid4()

        # 実行
        project_tasks = task_repository.get_by_project_id(non_existent_project_id)

        # 検証
        assert project_tasks == []

    def test_get_by_status_success(self, task_repository: TaskRepository, test_session: Session) -> None:
        """正常系: ステータス別タスク取得"""
        # テストデータの準備
        inbox_task = create_test_task(title="INBOXタスク", status=TaskStatus.INBOX)
        next_action_task1 = create_test_task(title="次のアクション1", status=TaskStatus.NEXT_ACTION)
        next_action_task2 = create_test_task(title="次のアクション2", status=TaskStatus.NEXT_ACTION)
        completed_task = create_test_task(title="完了タスク", status=TaskStatus.COMPLETED)

        test_session.add_all([inbox_task, next_action_task1, next_action_task2, completed_task])
        test_session.commit()

        # 実行
        next_action_tasks = task_repository.get_by_status(TaskStatus.NEXT_ACTION)

        # 検証
        expected_task_count = 2
        assert len(next_action_tasks) == expected_task_count
        task_titles = {task.title for task in next_action_tasks}
        assert task_titles == {"次のアクション1", "次のアクション2"}

    def test_get_by_status_empty(self, task_repository: TaskRepository) -> None:
        """正常系: 該当ステータスのタスクが存在しない場合"""
        # 実行
        delegated_tasks = task_repository.get_by_status(TaskStatus.DELEGATED)

        # 検証
        assert delegated_tasks == []

    def test_get_by_due_date(self, task_repository: TaskRepository, test_session: Session) -> None:
        """正常系: 期限日別タスク取得"""
        # テストデータの準備
        today = datetime.now(tz=UTC).date()
        tomorrow = today + timedelta(days=1)

        task_today = create_test_task(title="今日のタスク", due_date=today)
        task_tomorrow = create_test_task(title="明日のタスク", due_date=tomorrow)
        task_no_due_date = create_test_task(title="期限なしタスク")

        test_session.add_all([task_today, task_tomorrow, task_no_due_date])
        test_session.commit()

        # 実行
        today_tasks = task_repository.get_by_due_date(today)

        # 検証
        assert len(today_tasks) == 1
        assert today_tasks[0].title == "今日のタスク"

    def test_get_subtasks(self, task_repository: TaskRepository, test_session: Session) -> None:
        """正常系: サブタスクの取得"""
        # テストデータの準備
        parent_task = create_test_task(title="親タスク")
        test_session.add(parent_task)
        test_session.commit()
        test_session.refresh(parent_task)

        assert parent_task.id is not None

        subtask1 = create_test_task(title="サブタスク1", parent_id=parent_task.id)
        subtask2 = create_test_task(title="サブタスク2", parent_id=parent_task.id)
        independent_task = create_test_task(title="独立タスク")

        test_session.add_all([subtask1, subtask2, independent_task])
        test_session.commit()

        # 実行
        subtasks = task_repository.get_subtasks(parent_task.id)

        # 検証
        expected_subtask_count = 2
        assert len(subtasks) == expected_subtask_count
        task_titles = {task.title for task in subtasks}
        assert task_titles == {"サブタスク1", "サブタスク2"}

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

    def test_get_inbox_tasks(self, task_repository: TaskRepository, test_session: Session) -> None:
        """正常系: INBOXタスクの取得"""
        # テストデータの準備
        inbox_task1 = create_test_task(title="INBOX1", status=TaskStatus.INBOX)
        inbox_task2 = create_test_task(title="INBOX2", status=TaskStatus.INBOX)
        next_action_task = create_test_task(title="次のアクション", status=TaskStatus.NEXT_ACTION)

        test_session.add_all([inbox_task1, inbox_task2, next_action_task])
        test_session.commit()

        # 実行
        inbox_tasks = task_repository.get_inbox_tasks()

        # 検証
        expected_inbox_count = 2
        assert len(inbox_tasks) == expected_inbox_count
        task_titles = {task.title for task in inbox_tasks}
        assert task_titles == {"INBOX1", "INBOX2"}

    def test_get_next_action_tasks(self, task_repository: TaskRepository, test_session: Session) -> None:
        """正常系: 次のアクションタスクの取得"""
        # テストデータの準備
        next_action1 = create_test_task(title="次のアクション1", status=TaskStatus.NEXT_ACTION)
        next_action2 = create_test_task(title="次のアクション2", status=TaskStatus.NEXT_ACTION)
        inbox_task = create_test_task(title="INBOX", status=TaskStatus.INBOX)

        test_session.add_all([next_action1, next_action2, inbox_task])
        test_session.commit()

        # 実行
        next_action_tasks = task_repository.get_next_action_tasks()

        # 検証
        expected_next_action_count = 2
        assert len(next_action_tasks) == expected_next_action_count
        task_titles = {task.title for task in next_action_tasks}
        assert task_titles == {"次のアクション1", "次のアクション2"}

    def test_get_completed_tasks(self, task_repository: TaskRepository, test_session: Session) -> None:
        """正常系: 完了済みタスクの取得"""
        # テストデータの準備
        completed1 = create_test_task(title="完了1", status=TaskStatus.COMPLETED)
        completed2 = create_test_task(title="完了2", status=TaskStatus.COMPLETED)
        pending_task = create_test_task(title="未完了", status=TaskStatus.NEXT_ACTION)

        test_session.add_all([completed1, completed2, pending_task])
        test_session.commit()

        # 実行
        completed_tasks = task_repository.get_completed_tasks()

        # 検証
        expected_completed_count = 2
        assert len(completed_tasks) == expected_completed_count
        task_titles = {task.title for task in completed_tasks}
        assert task_titles == {"完了1", "完了2"}

    def test_get_overdue_tasks(self, task_repository: TaskRepository, test_session: Session) -> None:
        """正常系: 期限切れタスクの取得"""
        # テストデータの準備
        today = datetime.now(tz=UTC).date()
        yesterday = today - timedelta(days=1)
        tomorrow = today + timedelta(days=1)

        overdue_task = create_test_task(title="期限切れタスク", status=TaskStatus.NEXT_ACTION, due_date=yesterday)
        future_task = create_test_task(title="未来のタスク", status=TaskStatus.NEXT_ACTION, due_date=tomorrow)
        completed_overdue = create_test_task(title="完了済み期限切れ", status=TaskStatus.COMPLETED, due_date=yesterday)

        test_session.add_all([overdue_task, future_task, completed_overdue])
        test_session.commit()

        # 実行
        overdue_tasks = task_repository.get_overdue_tasks()

        # 検証
        assert len(overdue_tasks) == 1
        assert overdue_tasks[0].title == "期限切れタスク"
