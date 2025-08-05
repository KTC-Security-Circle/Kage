"""Logic層テスト用の共通設定とフィクスチャ

このモジュールは、logic層のテストで使用する共通的なセットアップ、
フィクスチャ、ユーティリティ関数を提供します。

主な機能：
- インメモリデータベースの設定
- テスト用のRepositoryとServiceインスタンス
- テストデータのファクトリ関数
"""

from collections.abc import Generator
from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import Engine, create_engine
from sqlmodel import Session, SQLModel

from logic.repositories.project import ProjectRepository
from logic.repositories.tag import TagRepository
from logic.repositories.task import TaskRepository
from logic.repositories.task_tag import TaskTagRepository
from logic.services.project_service import ProjectService
from logic.services.tag_service import TagService
from logic.services.task_service import TaskService
from logic.services.task_tag_service import TaskTagService
from models import Task, TaskStatus
from tests.logic.helpers import create_test_task


@pytest.fixture
def test_engine() -> Engine:
    """テスト用のインメモリデータベースエンジンを作成

    各テスト関数ごとに新しいインメモリデータベースを作成し、
    テスト間の状態分離を保証します。

    Returns:
        Engine: テスト用データベースエンジン
    """
    # [AI GENERATED] インメモリデータベースエンジンの作成
    engine = create_engine("sqlite:///:memory:", echo=False)

    # [AI GENERATED] 全テーブルの作成
    SQLModel.metadata.create_all(engine)

    return engine


@pytest.fixture
def test_session(test_engine: Engine) -> Generator[Session, None, None]:
    """テスト用のデータベースセッションを作成

    テスト関数内でデータベース操作を行うためのセッションを提供します。
    テスト完了後は自動的にセッションをクローズします。

    Args:
        test_engine: テスト用データベースエンジン

    Yields:
        Session: テスト用データベースセッション
    """
    with Session(test_engine) as session:
        yield session


@pytest.fixture
def task_repository(test_session: Session) -> TaskRepository:
    """テスト用TaskRepositoryインスタンスを作成

    Args:
        test_session: テスト用データベースセッション

    Returns:
        TaskRepository: テスト用TaskRepositoryインスタンス
    """
    return TaskRepository(test_session)


@pytest.fixture
def project_repository(test_session: Session) -> ProjectRepository:
    """テスト用ProjectRepositoryインスタンスを作成"""
    return ProjectRepository(test_session)


@pytest.fixture
def tag_repository(test_session: Session) -> TagRepository:
    """テスト用TagRepositoryインスタンスを作成"""
    return TagRepository(test_session)


@pytest.fixture
def task_tag_repository(test_session: Session) -> TaskTagRepository:
    """テスト用TaskTagRepositoryインスタンスを作成"""
    return TaskTagRepository(test_session)


@pytest.fixture
def task_service(
    task_repository: TaskRepository,
    project_repository: ProjectRepository,
    tag_repository: TagRepository,
    task_tag_repository: TaskTagRepository,
) -> TaskService:
    """テスト用TaskServiceインスタンスを作成

    Args:
        task_repository: テスト用TaskRepositoryインスタンス
        project_repository: テスト用ProjectRepositoryインスタンス
        tag_repository: テスト用TagRepositoryインスタンス
        task_tag_repository: テスト用TaskTagRepositoryインスタンス

    Returns:
        TaskService: テスト用TaskServiceインスタンス
    """
    return TaskService(task_repository, project_repository, tag_repository, task_tag_repository)


@pytest.fixture
def project_service(
    project_repository: ProjectRepository,
    task_repository: TaskRepository,
) -> ProjectService:
    """テスト用ProjectServiceインスタンスを作成

    Args:
        project_repository: テスト用ProjectRepositoryインスタンス
        task_repository: テスト用TaskRepositoryインスタンス

    Returns:
        ProjectService: テスト用ProjectServiceインスタンス
    """
    return ProjectService(project_repository, task_repository)


@pytest.fixture
def tag_service(
    tag_repository: TagRepository,
    task_tag_repository: TaskTagRepository,
) -> TagService:
    """テスト用TagServiceインスタンスを作成

    Args:
        tag_repository: テスト用TagRepositoryインスタンス
        task_tag_repository: テスト用TaskTagRepositoryインスタンス

    Returns:
        TagService: テスト用TagServiceインスタンス
    """
    return TagService(tag_repository, task_tag_repository)


@pytest.fixture
def task_tag_service(
    task_tag_repository: TaskTagRepository,
) -> TaskTagService:
    """テスト用TaskTagServiceインスタンスを作成

    Args:
        task_tag_repository: テスト用TaskTagRepositoryインスタンス

    Returns:
        TaskTagService: テスト用TaskTagServiceインスタンス
    """
    return TaskTagService(task_tag_repository)


@pytest.fixture
def sample_tasks(test_session: Session) -> list[Task]:
    """テスト用のサンプルタスクを作成してデータベースに保存

    各種ステータスのタスクを含むサンプルデータを作成します。

    Args:
        test_session: テスト用データベースセッション

    Returns:
        list[Task]: 作成されたサンプルタスクのリスト
    """
    today = datetime.now(tz=UTC).date()
    tomorrow = today + timedelta(days=1)

    tasks = [
        create_test_task("INBOXタスク", "新しく追加されたタスク", TaskStatus.INBOX),
        create_test_task("次のアクション", "すぐに実行すべきタスク", TaskStatus.NEXT_ACTION, tomorrow),
        create_test_task("完了済みタスク", "既に完了したタスク", TaskStatus.COMPLETED),
        create_test_task("待機中タスク", "他の人の対応待ち", TaskStatus.WAITING_FOR),
        create_test_task("いつかやる", "緊急ではないタスク", TaskStatus.SOMEDAY_MAYBE),
    ]

    # [AI GENERATED] データベースにサンプルタスクを保存
    for task in tasks:
        test_session.add(task)

    test_session.commit()

    # [AI GENERATED] 保存後にリフレッシュしてIDを確実に取得
    for task in tasks:
        test_session.refresh(task)

    return tasks
