# filepath: c:\Users\yukik\dev\Kage\src\logic\task.py
"""タスク管理のビジネスロジック層

このモジュールは、タスクのCRUD操作およびUI表示に必要な
ビジネスロジックを提供します。単一責任原則に基づいて設計されています。
"""

from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlmodel import Session, desc, func, select

from config import (
    DESCRIPTION_TRUNCATE_LENGTH,
    TASK_DESCRIPTION_MAX_LENGTH,
    TASK_TITLE_MAX_LENGTH,
    engine,
)
from models.task import Task, TaskCreate, TaskRead, TaskUpdate

if TYPE_CHECKING:
    from sqlmodel.sql.expression import SelectOfScalar


class TaskRepository:
    """タスクのデータアクセス層

    データベースとの直接的なやり取りを担当するクラス。
    SQLModelを使用してタスクの永続化操作を行います。
    """

    def __init__(self) -> None:
        """TaskRepositoryクラスのコンストラクタ"""
        self.engine = engine

    def create_task(self, task_data: TaskCreate) -> Task:
        """新しいタスクを作成してデータベースに保存

        Args:
            task_data: タスクのデータを含むTaskCreateオブジェクト

        Returns:
            Task: 作成されたタスクオブジェクト
        """
        db_task = Task.model_validate(task_data)

        with Session(self.engine) as session:
            session.add(db_task)
            session.commit()
            session.refresh(db_task)

        return db_task

    def get_task_by_id(self, task_id: int) -> Task | None:
        """指定されたIDのタスクを取得

        Args:
            task_id: 取得するタスクのID

        Returns:
            Task | None: 見つかったタスクオブジェクト、存在しない場合はNone
        """
        with Session(self.engine) as session:
            return session.get(Task, task_id)

    def _get_tasks_by_stmt(self, stmt: SelectOfScalar[Task]) -> list[Task]:
        """指定されたSQLAlchemyのステートメントに基づいてタスクを取得

        Args:
            stmt: SQLAlchemyのselectステートメント

        Returns:
            list[Task]: 見つかったタスクのリスト
        """
        with Session(self.engine) as session:
            return list(session.exec(stmt).all())

    def get_all_tasks(self) -> list[Task]:
        """すべてのタスクを取得

        Returns:
            list[Task]: 全タスクのリスト（作成日時の降順）
        """
        stmt = select(Task).order_by(desc(Task.created_at))
        return self._get_tasks_by_stmt(stmt)

    def get_task_by_date(self, target_date: datetime | date) -> list[Task]:
        """指定した日付のタスクを取得

        Args:
            target_date: 取得するタスクの日付

        Returns:
            list[Task]: 指定した日付のタスクのリスト
        """
        # 日付のみで比較するため、時刻部分を除外
        if isinstance(target_date, datetime):
            target_date = target_date.date()

        stmt = select(Task).where(func.date(Task.created_at) == target_date)
        return self._get_tasks_by_stmt(stmt)

    def get_tasks_by_completed(self) -> list[Task]:
        """完了済みタスクを取得

        Returns:
            list[Task]: 完了済みタスクのリスト
        """
        stmt = select(Task).where(Task.completed is True).order_by(desc(Task.created_at))
        return self._get_tasks_by_stmt(stmt)

    def get_tasks_by_pending(self) -> list[Task]:
        """未完了タスクを取得

        Returns:
            list[Task]: 未完了タスクのリスト
        """
        stmt = select(Task).where(Task.completed is False).order_by(desc(Task.created_at))
        return self._get_tasks_by_stmt(stmt)

    def _count_tasks_by_stmt(self, stmt: SelectOfScalar[int]) -> int:
        """指定されたSQLAlchemyのステートメントに基づいてタスクの数をカウント

        Args:
            stmt: SQLAlchemyのselectステートメント

        Returns:
            int: タスクの総数
        """
        with Session(self.engine) as session:
            return session.exec(stmt).one()

    def count_all_tasks(self) -> int:
        """全タスクの数をカウント

        Returns:
            int: タスクの総数
        """
        stmt = select(func.count()).select_from(Task)
        return self._count_tasks_by_stmt(stmt)

    def count_completed_tasks(self) -> int:
        """完了済みタスクの数をカウント

        Returns:
            int: 完了済みタスクの総数
        """
        stmt = select(func.count()).select_from(Task).where(Task.completed is True)
        return self._count_tasks_by_stmt(stmt)

    def update_task(self, task: Task, update_data: TaskUpdate) -> Task:
        """既存のタスクを更新

        Args:
            task: 更新するタスクオブジェクト
            update_data: 更新するデータを含むTaskUpdateオブジェクト
        """
        # TaskUpdateから値を取得して更新
        update_dict = update_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(task, field, value)

        # 更新日時を現在時刻に設定
        task.updated_at = datetime.now()

        with Session(self.engine) as session:
            session.add(task)
            session.commit()
            session.refresh(task)
        return task

    def delete_task(self, task: Task) -> None:
        """指定されたタスクを削除

        Args:
            task: 削除するタスクオブジェクト

        Returns:
            bool: 削除に成功した場合True
        """
        with Session(self.engine) as session:
            session.delete(task)
            session.commit()


class TaskService:
    """タスク管理のビジネスロジック層

    アプリケーションのビジネスルールやロジックを担当するクラス。
    UIレイヤーとデータアクセス層の仲介役として機能します。
    """

    def __init__(self, repository: TaskRepository) -> None:
        """TaskServiceクラスのコンストラクタ"""
        self.repository = repository

    def create_new_task(self, title: str, description: str = "") -> TaskRead:
        """新しいタスクを作成

        Args:
            title: タスクのタイトル
            description: タスクの説明

        Returns:
            TaskRead: 作成されたタスクオブジェクト

        Raises:
            ValueError: 入力値が不正な場合
        """
        if not title.strip():
            error_msg = "タスクのタイトルは必須です"
            raise ValueError(error_msg)

        created_task = self.repository.create_task(
            TaskCreate(
                title=title,
                description=description,
            )
        )
        return TaskRead.model_validate(created_task)

    def get_task_details(self, task_id: int) -> TaskRead | None:
        """タスクの詳細を取得

        Args:
            task_id: 取得するタスクのID

        Returns:
            TaskRead | None: タスクオブジェクト、存在しない場合はNone
        """
        db_task = self.repository.get_task_by_id(task_id)
        if db_task:
            return TaskRead.model_validate(db_task)
        return None

    def get_task_list(self) -> list[TaskRead]:
        """タスク一覧を取得

        Returns:
            list[TaskRead]: 全タスクのリスト
        """
        all_tasks = self.repository.get_all_tasks()
        return [TaskRead.model_validate(task) for task in all_tasks]

    def get_completed_tasks(self) -> list[TaskRead]:
        """完了済みタスクの一覧を取得

        Returns:
            list[TaskRead]: 完了済みタスクのリスト
        """
        completed_tasks = self.repository.get_tasks_by_completed()
        return [TaskRead.model_validate(task) for task in completed_tasks]

    def get_pending_tasks(self) -> list[TaskRead]:
        """未完了タスクの一覧を取得

        Returns:
            list[TaskRead]: 未完了タスクのリスト
        """
        pending_tasks = self.repository.get_tasks_by_pending()
        return [TaskRead.model_validate(task) for task in pending_tasks]

    def get_task_count(self) -> dict[str, int]:
        """タスクの統計情報を取得

        Returns:
            dict[str, int]: タスクの統計情報
        """
        total = self.repository.count_all_tasks()
        completed = self.repository.count_completed_tasks()
        pending = total - completed
        return {
            "total": total,
            "completed": completed,
            "pending": pending,
        }

    def get_task_count_by_date(self, target_date: datetime | date) -> int:
        """指定した日付のタスク数を取得

        Args:
            target_date: タスク数を取得する日付

        Returns:
            int: 指定した日付のタスク数
        """
        tasks = self.repository.get_task_by_date(target_date)
        return len(tasks)

    def get_task_count_by_today(self) -> int:
        """今日のタスク数を取得

        Returns:
            int: 今日のタスク数
        """
        today = datetime.now().date()
        return self.get_task_count_by_date(today)

    def get_task_by_date(self, target_date: datetime | date) -> list[TaskRead]:
        """指定した日付のタスクを取得

        Args:
            target_date: 取得するタスクの日付

        Returns:
            list[TaskRead]: 指定した日付のタスクのリスト
        """
        tasks = self.repository.get_task_by_date(target_date)
        return [TaskRead.model_validate(task) for task in tasks]

    def get_task_by_today(self) -> list[TaskRead]:
        """今日のタスクを取得

        Returns:
            list[TaskRead]: 今日のタスクのリスト
        """
        today = datetime.now().date()
        return self.get_task_by_date(today)

    def update_task(self, task_id: int, update_data: TaskUpdate) -> TaskRead | None:
        """タスク情報を更新

        Args:
            task_id: 更新するタスクのID
            update_data: 更新するデータを含むTaskUpdateオブジェクト

        Returns:
            TaskRead | None: 更新されたタスクオブジェクト、存在しない場合はNone

        Raises:
            ValueError: 入力値が不正な場合
        """
        if not update_data.title or not update_data.title.strip():
            error_msg = "タスクのタイトルは必須です"
            raise ValueError(error_msg)
        if len(update_data.title.strip()) > TASK_TITLE_MAX_LENGTH:
            error_msg = "タスクのタイトルは100文字以内で入力してください"
            raise ValueError(error_msg)

        task = self.repository.get_task_by_id(task_id)
        if not task:
            return None

        updated_task = self.repository.update_task(task, update_data)
        return TaskRead.model_validate(updated_task)

    def mark_task_completed(self, task_id: int) -> TaskRead | None:
        """タスクを完了としてマーク

        Args:
            task_id: 完了するタスクのID

        Returns:
            TaskRead | None: 更新されたタスクオブジェクト、存在しない場合はNone
        """
        task = self.repository.get_task_by_id(task_id)
        if task and not task.completed:
            task.completed = True
            updated_task = self.repository.update_task(task, TaskUpdate())
            return TaskRead.model_validate(updated_task)
        return TaskRead.model_validate(task) if task else None

    def mark_task_pending(self, task_id: int) -> TaskRead | None:
        """タスクを未完了としてマーク

        Args:
            task_id: 未完了にするタスクのID

        Returns:
            TaskRead | None: 更新されたタスクオブジェクト、存在しない場合はNone
        """
        task = self.repository.get_task_by_id(task_id)
        if task and task.completed:
            task.completed = False
            updated_task = self.repository.update_task(task, TaskUpdate())
            return TaskRead.model_validate(updated_task)
        return TaskRead.model_validate(task) if task else None

    def toggle_task_status(self, task_id: int) -> TaskRead | None:
        """タスクの完了状態を切り替え

        Args:
            task_id: 切り替えるタスクのID

        Returns:
            TaskRead | None: 更新されたタスクオブジェクト、存在しない場合はNone
        """
        task = self.repository.get_task_by_id(task_id)
        if not task:
            return None

        # 完了状態を反転
        task.completed = not task.completed
        updated_task = self.repository.update_task(task, TaskUpdate())
        return TaskRead.model_validate(updated_task)

    def remove_task(self, task_id: int) -> None:
        """タスクを削除

        Args:
            task_id: 削除するタスクのID

        Raises:
            ValueError: タスクIDが存在しない場合
        """
        task = self.repository.get_task_by_id(task_id)
        if not task:
            error_msg = f"タスクID {task_id} は存在しません"
            raise ValueError(error_msg)

        self.repository.delete_task(task)


class TaskUIHelper:
    """タスクUI表示のヘルパークラス

    UIコンポーネントの作成やフォーマット処理など、
    UI関連の補助機能を提供するクラス。
    """

    @staticmethod
    def format_task_title(task: TaskRead) -> str:
        """タスクタイトルをUI表示用にフォーマット

        Args:
            task: フォーマットするタスクオブジェクト

        Returns:
            str: フォーマットされたタスクタイトル
        """
        if task.completed:
            return f"✓ {task.title}"
        return f"○ {task.title}"

    @staticmethod
    def format_task_date(task: TaskRead) -> str:
        """タスクの日付をUI表示用にフォーマット

        Args:
            task: フォーマットするタスクオブジェクト

        Returns:
            str: フォーマットされた日付文字列
        """
        return task.created_at.strftime("%Y/%m/%d %H:%M")

    @staticmethod
    def get_task_status_color(task: TaskRead) -> str:
        """タスクの完了状態に応じた色を取得

        Args:
            task: タスクオブジェクト

        Returns:
            str: 色コード（完了済み: green、未完了: blue）
        """
        return "green" if task.completed else "blue"

    @staticmethod
    def truncate_description(description: str, max_length: int = DESCRIPTION_TRUNCATE_LENGTH) -> str:
        """説明文を指定された文字数で切り捨て

        Args:
            description: 元の説明文
            max_length: 最大文字数

        Returns:
            str: 切り捨てられた説明文
        """
        if len(description) <= max_length:
            return description
        return f"{description[:max_length]}..."

    @staticmethod
    def validate_task_input(title: str, description: str = "") -> tuple[bool, str]:
        """タスク入力値のバリデーション

        Args:
            title: タスクタイトル
            description: タスク説明

        Returns:
            tuple[bool, str]: (バリデーション結果, エラーメッセージ)
        """
        if not title or not title.strip():
            return False, "タスクのタイトルを入力してください"

        if len(title.strip()) > TASK_TITLE_MAX_LENGTH:
            return False, "タスクのタイトルは100文字以内で入力してください"

        if len(description) > TASK_DESCRIPTION_MAX_LENGTH:
            return False, "タスクの説明は500文字以内で入力してください"

        return True, ""
