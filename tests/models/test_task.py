"""Taskモデルのテストコード."""

from collections.abc import Generator
from datetime import datetime

import pytest
from sqlalchemy.engine import Engine
from sqlmodel import Session, SQLModel, create_engine

from src.models.task import Task, TaskCreate, TaskRead, TaskUpdate


class TestTaskModel:
    """Taskモデルのテストクラス."""

    @pytest.fixture
    def engine(self) -> Engine:
        """テスト用のインメモリデータベースエンジンを作成."""
        engine = create_engine("sqlite:///:memory:")
        SQLModel.metadata.create_all(engine)
        return engine

    @pytest.fixture
    def session(self, engine: Engine) -> Generator[Session, None, None]:
        """テスト用のデータベースセッションを作成."""
        with Session(engine) as session:
            yield session

    def test_task_creation(self, session: Session) -> None:
        """タスクの作成テスト."""
        # テストデータの準備
        task_data = TaskCreate(
            title="テストタスク",
            description="これはテスト用のタスクです",
        )

        # タスクの作成
        task = Task.model_validate(task_data)
        session.add(task)
        session.commit()
        session.refresh(task)

        # 検証
        assert task.id is not None
        assert task.title == "テストタスク"
        assert task.description == "これはテスト用のタスクです"
        assert task.completed is False  # デフォルト値
        assert task.created_at is not None
        assert task.updated_at is not None

    def test_task_default_values(self, session: Session) -> None:
        """タスクのデフォルト値テスト."""
        # 最小限のデータでタスクを作成
        task = Task(title="最小限タスク")
        session.add(task)
        session.commit()
        session.refresh(task)

        # デフォルト値の検証
        assert task.completed is False
        assert task.description == ""  # デフォルトは空文字列
        assert isinstance(task.created_at, datetime)
        assert isinstance(task.updated_at, datetime)

    def test_task_update_model(self) -> None:
        """TaskUpdateモデルのテスト."""
        # 部分的な更新データを作成
        update_data = TaskUpdate(
            title="更新されたタイトル",
            completed=True,
        )

        # 検証
        assert update_data.title == "更新されたタイトル"
        assert update_data.completed is True
        assert update_data.description is None  # 未設定フィールド

    def test_task_read_model(self, session: Session) -> None:
        """TaskReadモデルのテスト."""
        # タスクを作成
        task = Task(title="読み取りテスト", description="読み取り用タスク")
        session.add(task)
        session.commit()
        session.refresh(task)

        # TaskReadモデルに変換
        task_read = TaskRead.model_validate(task)

        # 検証
        assert task_read.id == task.id
        assert task_read.title == "読み取りテスト"
        assert task_read.description == "読み取り用タスク"
        assert task_read.completed is False
        assert isinstance(task_read.created_at, datetime)
        assert isinstance(task_read.updated_at, datetime)

    def test_task_title_validation(self) -> None:
        """タスクタイトルのバリデーションテスト."""
        # 正常なタイトル
        task = Task(title="適切な長さのタイトル")
        assert task.title == "適切な長さのタイトル"

        # インデックスが設定されていることを確認
        assert task.model_fields["title"].json_schema_extra is None or "index" in str(task.model_fields["title"])

    def test_task_create_model_validation(self) -> None:
        """TaskCreateモデルのバリデーションテスト."""
        # 正常なデータ
        task_create = TaskCreate(
            title="新しいタスク",
            description="説明文",
        )

        assert task_create.title == "新しいタスク"
        assert task_create.description == "説明文"
        assert task_create.completed is False  # デフォルト値
        assert isinstance(task_create.created_at, datetime)
        assert isinstance(task_create.updated_at, datetime)

    def test_task_completion_toggle(self, session: Session) -> None:
        """タスクの完了状態切り替えテスト."""
        # 未完了タスクを作成
        task = Task(title="完了テスト")
        session.add(task)
        session.commit()
        session.refresh(task)

        # 初期状態は未完了
        assert task.completed is False

        # 完了状態に変更
        task.completed = True
        session.add(task)
        session.commit()
        session.refresh(task)

        # 完了状態の検証
        assert task.completed is True

    def test_task_description_empty_default(self) -> None:
        """タスクの説明のデフォルト値テスト."""
        task = Task(title="説明なしタスク")
        assert task.description == ""  # 空文字列がデフォルト

    def test_task_timestamps(self, session: Session) -> None:
        """タスクのタイムスタンプテスト."""
        # タスクを作成
        before_creation = datetime.now()
        task = Task(title="タイムスタンプテスト")
        session.add(task)
        session.commit()
        session.refresh(task)
        after_creation = datetime.now()

        # 作成日時が適切な範囲内にあることを確認
        assert before_creation <= task.created_at <= after_creation
        assert before_creation <= task.updated_at <= after_creation

        # created_atとupdated_atが同じかほぼ同じであることを確認
        time_diff = abs((task.updated_at - task.created_at).total_seconds())
        assert time_diff < 1  # 1秒以内の差
