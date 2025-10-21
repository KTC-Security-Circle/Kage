"""Logic層テスト用の共通設定とフィクスチャ

このモジュールは、logic層のテストで使用する共通的なセットアップ、
フィクスチャ、ユーティリティ関数を提供します。

主な機能：
- インメモリデータベースの設定
- テスト用のRepositoryとServiceインスタンス
- テストデータのファクトリ関数
"""

# import sys
from collections.abc import Generator
from datetime import UTC, datetime, timedelta

import pytest
from loguru import logger
from sqlalchemy import Engine, create_engine
from sqlmodel import Session, SQLModel

from logic.repositories.memo import MemoRepository
from logic.repositories.project import ProjectRepository
from logic.repositories.tag import TagRepository
from logic.repositories.task import TaskRepository
from logic.repositories.term import TermRepository
from models import Task, TaskStatus
from tests.logic.helpers import create_test_task


@pytest.fixture(scope="session", autouse=True)
def setup_loguru_for_pytest_capture() -> None:
    """
    loguruのデフォルトハンドラを削除し、
    pytestがキャプチャできるsys.stderrにハンドラを再設定する。
    """

    logger.remove()  # デフォルトハンドラを削除

    # pytestのキャプチャが機能するように、sys.stderrにハンドラを追加
    # enqueue=True にすると非同期になり出力が混ざることがあるため、
    # テスト中は enqueue=False (同期) にするのが一般的です。
    # logger.add(
    #     sys.stderr,
    #     level="ERROR",  # テスト中はERRORレベル以上を出力
    #     enqueue=False,  # テスト中は同期的に出力
    # )

    # 2. ログメッセージを破棄する「何もしない」ハンドラを追加
    #    これがないと、loguruが「ハンドラがない」と判断して
    #    デフォルトハンドラを再度追加してしまう可能性があるため。
    #    sinkにはファイルパスや関数を指定できます。
    #    ここでは、受け取ったメッセージを単に無視するラムダ関数をsinkに指定します。
    logger.add(lambda _: None, level="DEBUG")


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
def memo_repository(test_session: Session) -> MemoRepository:
    """テスト用MemoRepositoryインスタンスを作成"""
    return MemoRepository(test_session)


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
def term_repository(test_session: Session) -> TermRepository:
    """テスト用TermRepositoryインスタンスを作成"""
    return TermRepository(test_session)


# 不存在の TaskTag 系は現行実装に合わせて削除（必要になれば復活させる）


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
        create_test_task("TODOタスク", "新しく追加されたタスク", TaskStatus.TODO),
        create_test_task("今日のタスク", "本日中に行うタスク", TaskStatus.TODAYS, tomorrow),
        create_test_task("進行中タスク", "現在進行中", TaskStatus.PROGRESS),
        create_test_task("待機中タスク", "他の対応待ち", TaskStatus.WAITING),
        create_test_task("完了済みタスク", "既に完了", TaskStatus.COMPLETED),
    ]

    # [AI GENERATED] データベースにサンプルタスクを保存
    for task in tasks:
        test_session.add(task)

    test_session.commit()

    # [AI GENERATED] 保存後にリフレッシュしてIDを確実に取得
    for task in tasks:
        test_session.refresh(task)

    return tasks
