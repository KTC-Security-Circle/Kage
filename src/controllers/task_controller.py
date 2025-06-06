# controller/task_controller.py
from __future__ import annotations

from models.task import (
    Task,
    create_task,
    delete_task,
    get_all_tasks,
    get_completed_tasks,
    get_pending_tasks,
    get_task,
    update_task,
    update_task_status,
)


class TaskController:
    """タスク管理コントローラー

    ビジネスロジックとモデル層の間の仲介としてタスク管理機能を提供します。
    UI層はこのクラスを通じてタスクデータにアクセスします。
    """

    @staticmethod
    def add_task(title: str, description: str | None = None) -> Task:
        """新しいタスクを追加する

        Args:
            title: タスクのタイトル
            description: タスクの説明（オプション）

        Returns:
            Task: 作成されたタスクオブジェクト

        Raises:
            ValueError: タイトルが空の場合
        """
        return create_task(title, description)

    @staticmethod
    def fetch_all_tasks() -> list[Task]:
        """すべてのタスクを取得する

        Returns:
            list[Task]: タスクのリスト
        """
        return get_all_tasks()

    @staticmethod
    def fetch_task(task_id: int) -> Task | None:
        """指定されたIDのタスクを取得する

        Args:
            task_id: 取得するタスクのID

        Returns:
            Task | None: 見つかったタスク、存在しない場合はNone
        """
        return get_task(task_id)

    @staticmethod
    def update_task(
        task_id: int,
        title: str | None = None,
        description: str | None = None,
        is_done: bool | None = None,
    ) -> Task | None:
        """タスクを更新する

        Args:
            task_id: 更新するタスクのID
            title: 新しいタイトル（指定がなければ変更なし）
            description: 新しい説明（指定がなければ変更なし）
            is_done: 新しい完了状態（指定がなければ変更なし）

        Returns:
            Task | None: 更新されたタスク、存在しない場合はNone
        """
        return update_task(task_id, title, description, is_done)

    @staticmethod
    def toggle_task_completion(task_id: int, *, completed: bool) -> Task | None:
        """タスクの完了状態を切り替える

        Args:
            task_id: 更新するタスクのID
            completed: 新しい完了状態

        Returns:
            Task | None: 更新されたタスク、存在しない場合はNone
        """
        return update_task_status(task_id, completed=completed)

    @staticmethod
    def remove_task(task_id: int) -> bool:
        """タスクを削除する

        Args:
            task_id: 削除するタスクのID

        Returns:
            bool: 削除が成功したかどうか
        """
        return delete_task(task_id)

    @staticmethod
    def fetch_completed_tasks() -> list[Task]:
        """完了済みのタスクのみを取得する

        Returns:
            list[Task]: 完了済みタスクのリスト
        """
        return get_completed_tasks()

    @staticmethod
    def fetch_pending_tasks() -> list[Task]:
        """未完了のタスクのみを取得する

        Returns:
            list[Task]: 未完了タスクのリスト
        """
        return get_pending_tasks()
