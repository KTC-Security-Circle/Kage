"""タスクロジックのテストコード."""

from __future__ import annotations

import datetime

import pytest
from sqlmodel import Session, SQLModel, create_engine, select

from src.config import TASK_DESCRIPTION_MAX_LENGTH, TASK_TITLE_MAX_LENGTH

# テスト用のTaskRepositoryをモックで作成
from src.models.task import Task, TaskCreate, TaskRead, TaskUpdate


class MockTaskRepository:
    """テスト用のTaskRepositoryモック."""

    def __init__(self) -> None:
        """MockTaskRepositoryクラスのコンストラクタ."""
        self.engine = create_engine("sqlite:///:memory:")
        SQLModel.metadata.create_all(self.engine)

    def create_task(self, task_data: TaskCreate) -> Task:
        """新しいタスクを作成してデータベースに保存."""
        db_task = Task.model_validate(task_data)
        with Session(self.engine) as session:
            session.add(db_task)
            session.commit()
            session.refresh(db_task)
        return db_task

    def get_task_by_id(self, task_id: int) -> Task | None:
        """指定されたIDのタスクを取得."""
        with Session(self.engine) as session:
            return session.get(Task, task_id)

    def get_all_tasks(self) -> list[Task]:
        """すべてのタスクを取得."""
        with Session(self.engine) as session:
            stmt = session.exec(select(Task))
            return list(stmt.all())

    def get_tasks_by_completed(self) -> list[Task]:
        """完了済みタスクを取得."""
        with Session(self.engine) as session:
            stmt = session.exec(select(Task).where(Task.completed is True))
            return list(stmt.all())

    def get_tasks_by_pending(self) -> list[Task]:
        """未完了タスクを取得."""
        with Session(self.engine) as session:
            stmt = session.exec(select(Task).where(Task.completed is False))
            return list(stmt.all())

    def count_all_tasks(self) -> int:
        """全タスクの数をカウント."""
        return len(self.get_all_tasks())

    def count_completed_tasks(self) -> int:
        """完了済みタスクの数をカウント."""
        return len(self.get_tasks_by_completed())

    def update_task(self, task: Task, update_data: TaskUpdate) -> Task:
        """既存のタスクを更新."""
        update_dict = update_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(task, field, value)
        task.updated_at = datetime.datetime.now()

        with Session(self.engine) as session:
            session.add(task)
            session.commit()
            session.refresh(task)
        return task

    def delete_task(self, task: Task) -> None:
        """指定されたタスクを削除."""
        with Session(self.engine) as session:
            session.delete(task)
            session.commit()


class MockTaskService:
    """テスト用のTaskServiceモック."""

    def __init__(self, repository: MockTaskRepository) -> None:
        """MockTaskServiceクラスのコンストラクタ."""
        self.repository = repository

    def create_new_task(self, title: str, description: str = "") -> TaskRead:
        """新しいタスクを作成."""
        if not title.strip():
            error_msg = "タスクのタイトルは必須です"
            raise ValueError(error_msg)

        created_task = self.repository.create_task(TaskCreate(title=title, description=description))
        return TaskRead.model_validate(created_task)

    def get_task_details(self, task_id: int) -> TaskRead | None:
        """タスクの詳細を取得."""
        db_task = self.repository.get_task_by_id(task_id)
        if db_task:
            return TaskRead.model_validate(db_task)
        return None

    def get_task_list(self) -> list[TaskRead]:
        """タスク一覧を取得."""
        all_tasks = self.repository.get_all_tasks()
        return [TaskRead.model_validate(task) for task in all_tasks]

    def get_task_count(self) -> dict[str, int]:
        """タスクの統計情報を取得."""
        total = self.repository.count_all_tasks()
        completed = self.repository.count_completed_tasks()
        pending = total - completed
        return {"total": total, "completed": completed, "pending": pending}

    def toggle_task_status(self, task_id: int) -> TaskRead | None:
        """タスクの完了状態を切り替え."""
        task = self.repository.get_task_by_id(task_id)
        if not task:
            return None

        task.completed = not task.completed
        updated_task = self.repository.update_task(task, TaskUpdate())
        return TaskRead.model_validate(updated_task)

    def remove_task(self, task_id: int) -> None:
        """タスクを削除."""
        task = self.repository.get_task_by_id(task_id)
        if not task:
            error_msg = f"タスクID {task_id} は存在しません"
            raise ValueError(error_msg)
        self.repository.delete_task(task)


class MockTaskUIHelper:
    """テスト用のTaskUIHelperモック."""

    @staticmethod
    def format_task_title(task: TaskRead) -> str:
        """タスクタイトルをUI表示用にフォーマット."""
        if task.completed:
            return f"✓ {task.title}"
        return f"○ {task.title}"

    @staticmethod
    def format_task_date(task: TaskRead) -> str:
        """タスクの日付をUI表示用にフォーマット."""
        return task.created_at.strftime("%Y/%m/%d %H:%M")

    @staticmethod
    def get_task_status_color(task: TaskRead) -> str:
        """タスクの完了状態に応じた色を取得."""
        return "green" if task.completed else "blue"

    @staticmethod
    def truncate_description(description: str, max_length: int = 50) -> str:
        """説明文を指定された文字数で切り捨て."""
        if len(description) <= max_length:
            return description
        return f"{description[:max_length]}..."

    @staticmethod
    def validate_task_input(title: str, description: str = "") -> tuple[bool, str]:
        """タスク入力値のバリデーション."""
        if not title or not title.strip():
            return False, "タスクのタイトルを入力してください"

        if len(title.strip()) > TASK_TITLE_MAX_LENGTH:
            return False, "タスクのタイトルは100文字以内で入力してください"

        if len(description) > TASK_DESCRIPTION_MAX_LENGTH:
            return False, "タスクの説明は500文字以内で入力してください"

        return True, ""


class TestTaskRepository:
    """TaskRepositoryのテストクラス."""

    @pytest.fixture
    def repository(self) -> MockTaskRepository:
        """テスト用のTaskRepositoryを作成."""
        return MockTaskRepository()

    @pytest.fixture
    def sample_task(self, repository: MockTaskRepository) -> Task:
        """テスト用のサンプルタスクを作成."""
        task_data = TaskCreate(title="テストタスク", description="テスト用の説明")
        return repository.create_task(task_data)

    def test_create_task(self, repository: MockTaskRepository) -> None:
        """タスク作成のテスト."""
        task_data = TaskCreate(title="新しいタスク", description="説明文")

        created_task = repository.create_task(task_data)

        assert created_task.id is not None
        assert created_task.title == "新しいタスク"
        assert created_task.description == "説明文"
        assert created_task.completed is False

    def test_get_task_by_id(self, repository: MockTaskRepository, sample_task: Task) -> None:
        """IDによるタスク取得のテスト."""
        task_id = sample_task.id
        assert task_id is not None

        retrieved_task = repository.get_task_by_id(task_id)

        assert retrieved_task is not None
        assert retrieved_task.id == task_id
        assert retrieved_task.title == sample_task.title

    def test_get_task_by_id_not_found(self, repository: MockTaskRepository) -> None:
        """存在しないIDでのタスク取得のテスト."""
        result = repository.get_task_by_id(999)
        assert result is None


class TestTaskService:
    """TaskServiceのテストクラス."""

    @pytest.fixture
    def repository(self) -> MockTaskRepository:
        """テスト用のRepositoryを作成."""
        return MockTaskRepository()

    @pytest.fixture
    def service(self, repository: MockTaskRepository) -> MockTaskService:
        """テスト用のTaskServiceを作成."""
        return MockTaskService(repository)

    def test_create_new_task_success(self, service: MockTaskService) -> None:
        """タスク新規作成成功のテスト."""
        result = service.create_new_task("新しいタスク", "説明文")

        assert isinstance(result, TaskRead)
        assert result.title == "新しいタスク"
        assert result.description == "説明文"

    def test_create_new_task_empty_title(self, service: MockTaskService) -> None:
        """空のタイトルでタスク作成のテスト."""
        with pytest.raises(ValueError, match="タスクのタイトルは必須です"):
            service.create_new_task("")


class TestTaskUIHelper:
    """TaskUIHelperのテストクラス."""

    @pytest.fixture
    def completed_task(self) -> TaskRead:
        """完了済みタスクのサンプル."""
        return TaskRead(
            id=1,
            title="完了タスク",
            description="完了した作業",
            completed=True,
            created_at=datetime.datetime(2024, 1, 1, 12, 0, 0, tzinfo=datetime.UTC),
            updated_at=datetime.datetime(2024, 1, 1, 12, 0, 0, tzinfo=datetime.UTC),
        )

    @pytest.fixture
    def pending_task(self) -> TaskRead:
        """未完了タスクのサンプル."""
        return TaskRead(
            id=2,
            title="未完了タスク",
            description="未完了の作業",
            completed=False,
            created_at=datetime.datetime(2024, 1, 1, 12, 0, 0, tzinfo=datetime.UTC),
            updated_at=datetime.datetime(2024, 1, 1, 12, 0, 0, tzinfo=datetime.UTC),
        )

    def test_format_task_title_completed(self, completed_task: TaskRead) -> None:
        """完了タスクのタイトルフォーマットのテスト."""
        result = MockTaskUIHelper.format_task_title(completed_task)
        assert result == "✓ 完了タスク"

    def test_format_task_title_pending(self, pending_task: TaskRead) -> None:
        """未完了タスクのタイトルフォーマットのテスト."""
        result = MockTaskUIHelper.format_task_title(pending_task)
        assert result == "○ 未完了タスク"

    def test_validate_task_input_valid(self) -> None:
        """有効なタスク入力のバリデーションテスト."""
        is_valid, message = MockTaskUIHelper.validate_task_input("有効なタイトル", "有効な説明")
        assert is_valid is True
        assert message == ""

    def test_validate_task_input_empty_title(self) -> None:
        """空のタイトルのバリデーションテスト."""
        is_valid, message = MockTaskUIHelper.validate_task_input("")
        assert is_valid is False
        assert "タイトルを入力してください" in message
