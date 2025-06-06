# filepath: c:\Users\yukik\dev\SigotoDekiruKun\src\logic\task.py
"""タスク管理のビジネスロジック層

このモジュールは、タスクのCRUD操作およびUI表示に必要な
ビジネスロジックを提供します。単一責任原則に基づいて設計されています。
"""

from __future__ import annotations

from datetime import datetime

from sqlmodel import Session, desc, select

from config import (
    DESCRIPTION_TRUNCATE_LENGTH,
    TASK_DESCRIPTION_MAX_LENGTH,
    TASK_TITLE_MAX_LENGTH,
    engine,
)
from models.task import Task, validate_task_id


class TaskRepository:
    """タスクのデータアクセス層

    データベースとの直接的なやり取りを担当するクラス。
    SQLModelを使用してタスクの永続化操作を行います。
    """

    def __init__(self) -> None:
        """TaskRepositoryクラスのコンストラクタ"""
        self.engine = engine

    def create_task(self, title: str, description: str = "") -> Task:
        """新しいタスクを作成してデータベースに保存

        Args:
            title: タスクのタイトル
            description: タスクの説明（オプション）

        Returns:
            Task: 作成されたタスクオブジェクト

        Raises:
            ValueError: タイトルが空の場合
        """
        if not title.strip():
            error_msg = "タスクのタイトルは必須です"
            raise ValueError(error_msg)

        task = Task(
            title=title.strip(),
            description=description.strip(),
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        with Session(self.engine) as session:
            session.add(task)
            session.commit()
            session.refresh(task)

        return task

    def get_task_by_id(self, task_id: int) -> Task | None:
        """指定されたIDのタスクを取得

        Args:
            task_id: 取得するタスクのID

        Returns:
            Task | None: 見つかったタスクオブジェクト、存在しない場合はNone
        """
        validated_id = validate_task_id(task_id)

        with Session(self.engine) as session:
            statement = select(Task).where(Task.id == validated_id)
            return session.exec(statement).first()

    def get_all_tasks(self) -> list[Task]:
        """すべてのタスクを取得

        Returns:
            list[Task]: 全タスクのリスト（作成日時の降順）
        """
        with Session(self.engine) as session:
            statement = select(Task).order_by(desc(Task.created_at))
            return list(session.exec(statement).all())

    def get_task_by_date(self, date: datetime) -> list[Task]:
        """指定した日付のタスクを取得

        Args:
            date: 取得するタスクの日付

        Returns:
            list[Task]: 指定した日付のタスクのリスト
        """
        with Session(self.engine) as session:
            statement = select(Task).where(Task.created_at == date)
            return list(session.exec(statement).all())

    def update_task(
        self,
        task_id: int,
        title: str | None = None,
        description: str | None = None,
    ) -> Task | None:
        """既存のタスクを更新

        Args:
            task_id: 更新するタスクのID
            title: 新しいタイトル（Noneの場合は更新しない）
            description: 新しい説明（Noneの場合は更新しない）

        Returns:
            Task | None: 更新されたタスクオブジェクト、存在しない場合はNone
        """
        validated_id = validate_task_id(task_id)

        with Session(self.engine) as session:
            task = session.get(Task, validated_id)
            if not task:
                return None

            # 更新対象のフィールドのみ変更
            if title is not None:
                if not title.strip():
                    error_msg = "タスクのタイトルは必須です"
                    raise ValueError(error_msg)
                task.title = title.strip()

            if description is not None:
                task.description = description.strip()

            # 更新日時を現在時刻に設定
            task.updated_at = datetime.now()

            session.add(task)
            session.commit()
            session.refresh(task)

        return task

    def toggle_task_completion(self, task_id: int) -> Task | None:
        """タスクの完了状態を切り替え

        Args:
            task_id: 切り替えるタスクのID

        Returns:
            Task | None: 更新されたタスクオブジェクト、存在しない場合はNone
        """
        validated_id = validate_task_id(task_id)

        with Session(self.engine) as session:
            task = session.get(Task, validated_id)
            if not task:
                return None

            task.completed = not task.completed
            task.updated_at = datetime.now()

            session.add(task)
            session.commit()
            session.refresh(task)

        return task

    def delete_task(self, task_id: int) -> bool:
        """指定されたIDのタスクを削除

        Args:
            task_id: 削除するタスクのID

        Returns:
            bool: 削除に成功した場合True、タスクが存在しない場合False
        """
        validated_id = validate_task_id(task_id)

        with Session(self.engine) as session:
            task = session.get(Task, validated_id)
            if not task:
                return False

            session.delete(task)
            session.commit()

        return True


class TaskService:
    """タスク管理のビジネスロジック層

    アプリケーションのビジネスルールやロジックを担当するクラス。
    UIレイヤーとデータアクセス層の仲介役として機能します。
    """

    def __init__(self) -> None:
        """TaskServiceクラスのコンストラクタ"""
        self.repository = TaskRepository()

    def create_new_task(self, title: str, description: str = "") -> Task:
        """新しいタスクを作成

        Args:
            title: タスクのタイトル
            description: タスクの説明

        Returns:
            Task: 作成されたタスクオブジェクト

        Raises:
            ValueError: 入力値が不正な場合
        """
        return self.repository.create_task(title, description)

    def get_task_details(self, task_id: int) -> Task | None:
        """タスクの詳細を取得

        Args:
            task_id: 取得するタスクのID

        Returns:
            Task | None: タスクオブジェクト、存在しない場合はNone
        """
        return self.repository.get_task_by_id(task_id)

    def get_task_list(self) -> list[Task]:
        """タスク一覧を取得

        Returns:
            list[Task]: 全タスクのリスト
        """
        return self.repository.get_all_tasks()

    def get_completed_tasks(self) -> list[Task]:
        """完了済みタスクの一覧を取得

        Returns:
            list[Task]: 完了済みタスクのリスト
        """
        all_tasks = self.repository.get_all_tasks()
        return [task for task in all_tasks if task.completed]

    def get_pending_tasks(self) -> list[Task]:
        """未完了タスクの一覧を取得

        Returns:
            list[Task]: 未完了タスクのリスト
        """
        all_tasks = self.repository.get_all_tasks()
        return [task for task in all_tasks if not task.completed]

    def get_task_by_date(self, date: datetime) -> list[Task]:
        """指定した日付のタスクを取得

        Args:
            date: 取得するタスクの日付

        Returns:
            list[Task]: 指定した日付のタスクのリスト
        """
        return self.repository.get_task_by_date(date)

    def get_task_by_today(self) -> list[Task]:
        """今日のタスクを取得

        Returns:
            list[Task]: 今日のタスクのリスト
        """
        today = datetime.now()
        return self.repository.get_task_by_date(today)

    def update_task_info(
        self,
        task_id: int,
        title: str | None = None,
        description: str | None = None,
    ) -> Task | None:
        """タスク情報を更新

        Args:
            task_id: 更新するタスクのID
            title: 新しいタイトル
            description: 新しい説明

        Returns:
            Task | None: 更新されたタスクオブジェクト、存在しない場合はNone
        """
        return self.repository.update_task(task_id, title, description)

    def mark_task_completed(self, task_id: int) -> Task | None:
        """タスクを完了としてマーク

        Args:
            task_id: 完了するタスクのID

        Returns:
            Task | None: 更新されたタスクオブジェクト、存在しない場合はNone
        """
        task = self.repository.get_task_by_id(task_id)
        if not task:
            return None

        if not task.completed:
            return self.repository.toggle_task_completion(task_id)
        return task

    def mark_task_pending(self, task_id: int) -> Task | None:
        """タスクを未完了としてマーク

        Args:
            task_id: 未完了にするタスクのID

        Returns:
            Task | None: 更新されたタスクオブジェクト、存在しない場合はNone
        """
        task = self.repository.get_task_by_id(task_id)
        if not task:
            return None

        if task.completed:
            return self.repository.toggle_task_completion(task_id)
        return task

    def toggle_task_status(self, task_id: int) -> Task | None:
        """タスクの完了状態を切り替え

        Args:
            task_id: 切り替えるタスクのID

        Returns:
            Task | None: 更新されたタスクオブジェクト、存在しない場合はNone
        """
        return self.repository.toggle_task_completion(task_id)

    def remove_task(self, task_id: int) -> bool:
        """タスクを削除

        Args:
            task_id: 削除するタスクのID

        Returns:
            bool: 削除に成功した場合True
        """
        return self.repository.delete_task(task_id)

    def get_task_count(self) -> dict[str, int]:
        """タスクの統計情報を取得

        Returns:
            dict[str, int]: タスクの統計情報
        """
        all_tasks = self.repository.get_all_tasks()
        completed_count = sum(1 for task in all_tasks if task.completed)
        pending_count = len(all_tasks) - completed_count

        return {
            "total": len(all_tasks),
            "completed": completed_count,
            "pending": pending_count,
        }


class TaskUIHelper:
    """タスクUI表示のヘルパークラス

    UIコンポーネントの作成やフォーマット処理など、
    UI関連の補助機能を提供するクラス。
    """

    @staticmethod
    def format_task_title(task: Task) -> str:
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
    def format_task_date(task: Task) -> str:
        """タスクの日付をUI表示用にフォーマット

        Args:
            task: フォーマットするタスクオブジェクト

        Returns:
            str: フォーマットされた日付文字列
        """
        return task.created_at.strftime("%Y/%m/%d %H:%M")

    @staticmethod
    def get_task_status_color(task: Task) -> str:
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
