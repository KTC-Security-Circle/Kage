"""BaseApplicationServiceのテストケース

このモジュールは、BaseApplicationServiceクラスの
基本機能をテストするためのテストケースを提供します。

テスト対象：
- 初期化処理
- Unit of Work Factory の設定
"""

from unittest.mock import Mock

import pytest

from logic.application.base import BaseApplicationService


class TestBaseApplicationService:
    """BaseApplicationServiceの基本機能をテストするクラス"""

    @pytest.fixture
    def mock_unit_of_work_factory(self) -> Mock:
        """モックのUnit of Work Factoryを作成"""
        mock_factory = Mock()
        mock_factory.__name__ = "MockUnitOfWork"  # [AI GENERATED] クラス名設定
        return mock_factory

    @pytest.fixture
    def base_service(self, mock_unit_of_work_factory: Mock) -> BaseApplicationService:
        """BaseApplicationServiceのインスタンスを作成"""
        return BaseApplicationService(mock_unit_of_work_factory)  # type: ignore[arg-type]

    def test_init_success(self, mock_unit_of_work_factory: Mock) -> None:
        """正常系: BaseApplicationServiceの初期化成功"""
        # 実行
        service = BaseApplicationService(mock_unit_of_work_factory)  # type: ignore[arg-type]

        # 検証
        assert hasattr(service, "_unit_of_work_factory")
        assert service._unit_of_work_factory is mock_unit_of_work_factory

    def test_unit_of_work_factory_attribute(
        self, base_service: BaseApplicationService, mock_unit_of_work_factory: Mock
    ) -> None:
        """正常系: Unit of Work Factoryの設定確認"""
        # 検証
        assert hasattr(base_service, "_unit_of_work_factory")
        assert base_service._unit_of_work_factory is mock_unit_of_work_factory

    def test_get_instance_returns_singleton(self, mock_unit_of_work_factory: Mock) -> None:
        """正常系: get_instance はシングルトンとしてインスタンスを返す"""

        class DummyService(BaseApplicationService):
            """テスト用のダミー Application Service"""

        try:
            instance1 = DummyService.get_instance(mock_unit_of_work_factory)  # type: ignore[arg-type]
            instance2 = DummyService.get_instance(mock_unit_of_work_factory)  # type: ignore[arg-type]

            assert instance1 is instance2
            assert instance1._unit_of_work_factory is mock_unit_of_work_factory
        finally:
            if hasattr(DummyService, "_instance"):
                delattr(DummyService, "_instance")

    def test_get_instance_reinitializes_with_new_factory(self, mock_unit_of_work_factory: Mock) -> None:
        """正常系: get_instance 再呼び出しで依存が再設定される"""

        class DummyService(BaseApplicationService):
            """テスト用のダミー Application Service"""

        other_factory = Mock()

        try:
            DummyService.get_instance(mock_unit_of_work_factory)  # type: ignore[arg-type]
            instance = DummyService.get_instance(other_factory)  # type: ignore[arg-type]

            assert instance._unit_of_work_factory is other_factory
        finally:
            if hasattr(DummyService, "_instance"):
                delattr(DummyService, "_instance")
