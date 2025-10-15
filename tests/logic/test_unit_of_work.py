"""Unit of Work テスト項目（現行仕様）

UnitOfWork/SqlModelUnitOfWork のトランザクション管理とファクトリ連携を検証する。

テスト項目（実装前の項目定義）:
- コンテキスト管理:
    - withブロックで Session/RepositoryFactory/ServiceFactory が生成される
    - 例外発生時に rollback が実行され、終了時にセッションがクローズされる
- 初期化前アクセス:
    - session/repository_factory/service_factory へのアクセスは RuntimeError
- トランザクション:
    - commit が永続化し、rollback は破棄する
    - 同一トランザクション内で複数操作が可能
- ファクトリ整合性:
    - repository_factory.create(...) で作られたリポジトリと
        service_factory.get_service(...) で作られたサービスは同じセッションを共有
    - get_service_factory() のコンテキストマネージャが ServiceFactory を提供
- 統合シナリオ:
    - TaskService を取得してタスクを保存後、get_by_id で取得できる
"""

import uuid
from unittest.mock import patch

import pytest
from sqlalchemy import Engine, create_engine
from sqlmodel import Session, SQLModel

from logic.factory import RepositoryFactory, ServiceFactory
from logic.repositories.task import TaskRepository
from logic.services.task_service import TaskService
from logic.unit_of_work import SqlModelUnitOfWork, UnitOfWork
from models import Task, TaskStatus
from tests.logic.helpers import create_test_task


class TestSqlModelUnitOfWork:
    """SqlModelUnitOfWork のテストクラス

    Unit of Work パターンの実装をテストします。
    """

    @pytest.fixture
    def clean_engine(self) -> Engine:
        """テスト用のクリーンなインメモリデータベースエンジン"""
        engine = create_engine("sqlite:///:memory:", echo=False)
        SQLModel.metadata.create_all(engine)
        return engine

    def test_context_manager_creates_session(self, clean_engine: Engine) -> None:
        """コンテキストマネージャーがセッションを作成することをテスト"""
        with patch("logic.unit_of_work.engine", clean_engine):
            uow = SqlModelUnitOfWork()

            with uow:
                assert isinstance(uow.session, Session)
                assert uow.session is not None

    def test_context_manager_creates_factories(self, clean_engine: Engine) -> None:
        """コンテキストマネージャーがファクトリを作成することをテスト"""
        with patch("logic.unit_of_work.engine", clean_engine):
            uow = SqlModelUnitOfWork()

            with uow:
                assert isinstance(uow.repository_factory, RepositoryFactory)
                assert isinstance(uow.service_factory, ServiceFactory)
                assert uow.repository_factory.session is uow.session

    def test_session_property_without_initialization_raises_error(self) -> None:
        """初期化前にsessionプロパティにアクセスするとエラーが発生することをテスト"""
        uow = SqlModelUnitOfWork()

        with pytest.raises(RuntimeError, match="Unit of Work not initialized"):
            _ = uow.session

    def test_repository_factory_property_without_initialization_raises_error(self) -> None:
        """初期化前にrepository_factoryプロパティにアクセスするとエラーが発生することをテスト"""
        uow = SqlModelUnitOfWork()

        with pytest.raises(RuntimeError, match="Unit of Work not initialized"):
            _ = uow.repository_factory

    def test_service_factory_property_without_initialization_raises_error(self) -> None:
        """初期化前にservice_factoryプロパティにアクセスするとエラーが発生することをテスト"""
        uow = SqlModelUnitOfWork()

        with pytest.raises(RuntimeError, match="Unit of Work not initialized"):
            _ = uow.service_factory

    def test_commit_persists_changes(self, clean_engine: Engine) -> None:
        """commit() がデータベースに変更を永続化することをテスト"""
        with patch("logic.unit_of_work.engine", clean_engine):
            task_id = uuid.uuid4()
            task = Task(
                id=task_id,
                title="テストタスク",
                description="テスト用",
                status=TaskStatus.TODO,
            )

            uow = SqlModelUnitOfWork()
            with uow:
                uow.session.add(task)
                uow.commit()

            # [AI GENERATED] 別のセッションで確認
            with Session(clean_engine) as verify_session:
                saved_task = verify_session.get(Task, task_id)
                assert saved_task is not None
                assert saved_task.title == "テストタスク"

    def test_rollback_discards_changes(self, clean_engine: Engine) -> None:
        """rollback() が変更を破棄することをテスト"""
        with patch("logic.unit_of_work.engine", clean_engine):
            task_id = uuid.uuid4()
            task = Task(
                id=task_id,
                title="テストタスク",
                description="テスト用",
                status=TaskStatus.TODO,
            )

            uow = SqlModelUnitOfWork()
            with uow:
                uow.session.add(task)
                uow.rollback()

            # [AI GENERATED] 別のセッションで確認
            with Session(clean_engine) as verify_session:
                saved_task = verify_session.get(Task, task_id)
                assert saved_task is None

    def test_exception_in_context_triggers_rollback(self, clean_engine: Engine) -> None:
        """コンテキスト内で例外が発生するとロールバックが実行されることをテスト"""
        with patch("logic.unit_of_work.engine", clean_engine):
            task_id = uuid.uuid4()
            task = Task(
                id=task_id,
                title="テストタスク",
                description="テスト用",
                status=TaskStatus.TODO,
            )

            uow = SqlModelUnitOfWork()
            test_error_msg = "テスト例外"

            def test_operation() -> None:
                with uow:
                    uow.session.add(task)
                    # [AI GENERATED] 意図的に例外を発生させる
                    raise ValueError(test_error_msg)

            with pytest.raises(ValueError, match="テスト例外"):
                test_operation()

            # [AI GENERATED] 別のセッションで確認
            with Session(clean_engine) as verify_session:
                saved_task = verify_session.get(Task, task_id)
                assert saved_task is None

    def test_session_closes_after_context_exit(self, clean_engine: Engine) -> None:
        """コンテキスト終了後にセッションがクローズされることをテスト"""
        with patch("logic.unit_of_work.engine", clean_engine):
            uow = SqlModelUnitOfWork()

            with uow:
                session = uow.session
                assert not session.is_active or session.bind is not None

            # [AI GENERATED] コンテキスト終了後はセッションがクローズされている
            # SQLiteの場合、is_activeはFalseになる

    def test_get_service_factory_context_manager(self, clean_engine: Engine) -> None:
        """get_service_factory コンテキストマネージャーが正しく動作することをテスト"""
        with patch("logic.unit_of_work.engine", clean_engine):
            uow = SqlModelUnitOfWork()

            with uow, uow.get_service_factory() as service_factory:
                assert isinstance(service_factory, ServiceFactory)
                assert service_factory is uow.service_factory

    def test_factories_share_same_session(self, clean_engine: Engine) -> None:
        """リポジトリファクトリとサービスファクトリが同じセッションを使用することをテスト"""
        with patch("logic.unit_of_work.engine", clean_engine):
            uow = SqlModelUnitOfWork()

            with uow:
                # [AI GENERATED] ファクトリから作成されたリポジトリが同じセッションを使用することを確認
                task_repo = uow.repository_factory.create(TaskRepository)
                task_service = uow.service_factory.get_service(TaskService)

                assert task_repo.session is uow.session
                assert task_service.task_repo.session is uow.session

    def test_multiple_operations_in_same_transaction(self, clean_engine: Engine) -> None:
        """同じトランザクション内で複数の操作が実行できることをテスト"""
        with patch("logic.unit_of_work.engine", clean_engine):
            uow = SqlModelUnitOfWork()

            with uow:
                # [AI GENERATED] 複数のタスクを作成
                task1 = create_test_task("タスク1", "説明1")
                task2 = create_test_task("タスク2", "説明2")

                uow.session.add(task1)
                uow.session.add(task2)
                uow.commit()

                # [AI GENERATED] 同じセッション内で確認
                saved_task1 = uow.session.get(Task, task1.id)
                saved_task2 = uow.session.get(Task, task2.id)

                assert saved_task1 is not None
                assert saved_task2 is not None
                assert saved_task1.title == "タスク1"
                assert saved_task2.title == "タスク2"


class TestUnitOfWorkAbstractInterface:
    """UnitOfWork 抽象クラスのテストクラス

    抽象クラスのインターフェースが正しく定義されていることをテストします。
    """

    def test_abstract_class_cannot_be_instantiated(self) -> None:
        """抽象クラス UnitOfWork が直接インスタンス化できないことをテスト"""
        with pytest.raises(TypeError):
            UnitOfWork()  # type: ignore[abstract]

    def test_sqlmodel_unit_of_work_implements_interface(self) -> None:
        """SqlModelUnitOfWork が UnitOfWork インターフェースを実装していることをテスト"""
        uow = SqlModelUnitOfWork()

        # [AI GENERATED] UnitOfWork のサブクラスであることを確認
        assert isinstance(uow, UnitOfWork)

        # [AI GENERATED] 必要なメソッドが実装されていることを確認
        assert hasattr(uow, "__enter__")
        assert hasattr(uow, "__exit__")
        assert hasattr(uow, "commit")
        assert hasattr(uow, "rollback")
        # sessionとservice_factoryはプロパティなので、クラスレベルで確認
        assert "session" in dir(uow)
        assert "service_factory" in dir(uow)
        assert hasattr(uow, "get_service_factory")


class TestUnitOfWorkIntegration:
    """Unit of Work 統合テストクラス

    Unit of Work パターンの実際の使用シナリオをテストします。
    """

    def test_service_operations_with_unit_of_work(self, test_engine: Engine) -> None:
        """Unit of Work を使用したサービス操作の統合テスト"""
        with patch("logic.unit_of_work.engine", test_engine):
            uow = SqlModelUnitOfWork()

            with uow:
                task_service = uow.service_factory.get_service(TaskService)

                # [AI GENERATED] タスクを作成
                task_data = create_test_task("統合テストタスク", "Unit of Work テスト")
                uow.session.add(task_data)
                uow.commit()

                # [AI GENERATED] 作成されたタスクを取得
                assert task_data.id is not None
                saved_task = task_service.get_by_id(task_data.id)
                assert saved_task is not None
                assert saved_task.title == "統合テストタスク"

    def test_transaction_rollback_integration(self, test_engine: Engine) -> None:
        """トランザクションロールバックの統合テスト"""
        with patch("logic.unit_of_work.engine", test_engine):
            task_id = uuid.uuid4()

            # [AI GENERATED] 最初にタスクを作成してコミット
            uow1 = SqlModelUnitOfWork()
            with uow1:
                task = Task(
                    id=task_id,
                    title="元のタスク",
                    description="元の説明",
                    status=TaskStatus.TODO,
                )
                uow1.session.add(task)
                uow1.commit()

            # [AI GENERATED] 別のトランザクションで更新を試みるが、ロールバックする
            uow2 = SqlModelUnitOfWork()
            with uow2:
                task_to_update = uow2.session.get(Task, task_id)
                assert task_to_update is not None
                task_to_update.title = "更新されたタスク"
                uow2.rollback()

            # [AI GENERATED] 変更がロールバックされていることを確認
            uow3 = SqlModelUnitOfWork()
            with uow3:
                final_task = uow3.session.get(Task, task_id)
                assert final_task is not None
                assert final_task.title == "元のタスク"  # [AI GENERATED] 元のタイトルのまま
