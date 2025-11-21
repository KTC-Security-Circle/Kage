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
from models import Tag, Task, TaskStatus


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

    def test_list_by_status_with_details(self, task_repository: TaskRepository, test_session: Session) -> None:
        """正常系: with_details=True で関連読み込み分岐を通す"""
        # タグやプロジェクトの関連はDB側にテーブルがある前提。ここでは存在有無の例外にならないことのみ確認。
        progress_task = create_test_task(title="進行中D", status=TaskStatus.PROGRESS)
        test_session.add(progress_task)
        test_session.commit()

        results = task_repository.list_by_status(TaskStatus.PROGRESS, with_details=True)
        assert any(t.title == "進行中D" for t in results)

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

    def test_search_by_title_with_details_and_not_found(
        self, task_repository: TaskRepository, test_session: Session
    ) -> None:
        """with_details=True 分岐とヒットなしでの NotFoundError を検証"""
        task = create_test_task(title="Alpha")
        test_session.add(task)
        test_session.commit()

        # with_details=True でヒット
        found = task_repository.search_by_title("alpha", with_details=True)
        assert len(found) == 1
        assert found[0].title == "Alpha"

        # ヒットなしで NotFoundError
        with pytest.raises(NotFoundError):
            task_repository.search_by_title("Gamma")

    def test_list_by_project_with_details(self, task_repository: TaskRepository, test_session: Session) -> None:
        """with_details=True での list_by_project 分岐を通す"""
        project_id = uuid.uuid4()
        t1 = create_test_task(title="P-1", project_id=project_id)
        t2 = create_test_task(title="P-2", project_id=project_id)
        other = create_test_task(title="Other")
        test_session.add_all([t1, t2, other])
        test_session.commit()

        results = task_repository.list_by_project(project_id, with_details=True)
        titles = {t.title for t in results}
        assert titles == {"P-1", "P-2"}

    def test_add_remove_and_clear_tags(self, task_repository: TaskRepository, test_session: Session) -> None:
        """タグの追加/重複追加/未関連削除/全削除/空時全削除/存在しないIDエラーの分岐を網羅"""
        # エンティティ作成
        task = create_test_task(title="TagTarget")
        tag_attached = Tag(name="T-A")
        tag_other = Tag(name="T-B")
        test_session.add_all([task, tag_attached, tag_other])
        test_session.commit()
        test_session.refresh(task)
        test_session.refresh(tag_attached)
        test_session.refresh(tag_other)

        assert task.id is not None
        assert tag_attached.id is not None
        assert tag_other.id is not None

        task_id = task.id
        tag_id = tag_attached.id
        other_tag_id = tag_other.id

        # 追加（初回）
        updated = task_repository.add_tag(task_id, tag_id)
        assert any(t.name == "T-A" for t in updated.tags)

        # 重複追加は冪等
        updated2 = task_repository.add_tag(task_id, tag_id)
        names = [t.name for t in updated2.tags]
        assert names.count("T-A") == 1

        # 未関連タグの削除は何も起きない（例外なし）
        updated3 = task_repository.remove_tag(task_id, other_tag_id)
        assert any(t.name == "T-A" for t in updated3.tags)

        # 存在しないタグIDは NotFoundError
        with pytest.raises(NotFoundError):
            task_repository.remove_tag(task_id, uuid.uuid4())

        # 全削除（1件あり）
        cleared = task_repository.remove_all_tags(task_id)
        assert cleared.tags == []

        # 既に空の状態で全削除（分岐通過）
        cleared2 = task_repository.remove_all_tags(task_id)
        assert cleared2.tags == []

        # 存在しないタスクIDへの追加は NotFoundError
        with pytest.raises(NotFoundError):
            task_repository.add_tag(uuid.uuid4(), tag_id)

    def test_search_by_description(self, task_repository: TaskRepository, test_session: Session) -> None:
        """説明による検索（部分一致・大文字小文字無視）"""
        t1 = create_test_task(title="A", description="Implement feature X")
        t2 = create_test_task(title="B", description="implement integration tests")
        t3 = create_test_task(title="C", description="Review PR")
        test_session.add_all([t1, t2, t3])
        test_session.commit()

        hits = task_repository.search_by_description("implement")
        titles = {t.title for t in hits}
        assert titles == {"A", "B"}

    def test_search_by_description_no_hit(self, task_repository: TaskRepository, test_session: Session) -> None:
        """説明検索でヒットなしは NotFoundError"""
        t = create_test_task(title="Z", description="Something else")
        test_session.add(t)
        test_session.commit()

        with pytest.raises(NotFoundError):
            task_repository.search_by_description("nope")

    def test_search_by_description_with_details(self, task_repository: TaskRepository, test_session: Session) -> None:
        """with_details=True 分岐を通す"""
        t = create_test_task(title="D", description="Document work")
        test_session.add(t)
        test_session.commit()
        res = task_repository.search_by_description("doc", with_details=True)
        assert len(res) == 1
        assert res[0].title == "D"
