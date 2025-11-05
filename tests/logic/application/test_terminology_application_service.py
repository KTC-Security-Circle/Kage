"""TerminologyApplicationServiceのテストケース(モックベース)

このモジュールは、Application層の用語管理サービスの
テストを提供します。Unit of Workをモック化して、
サービス層への依存を分離したユニットテストを実施します。
"""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING
from unittest.mock import Mock

import pytest

from logic.application.terminology_application_service import (
    TerminologyApplicationService,
    TermKeyValidationError,
)
from models import TermRead, TermStatus

if TYPE_CHECKING:
    from pathlib import Path

# マジックナンバー定数化
EXPECTED_CSV_IMPORT_SUCCESS = 2
EXPECTED_CSV_EXPORT_COUNT = 1


class TestTerminologyApplicationService:
    """TerminologyApplicationServiceのApplication Service層機能をテストするクラス"""

    @pytest.fixture
    def mock_unit_of_work(self) -> Mock:
        """モックのUnit of Workを作成"""
        mock_uow = Mock()
        mock_service_factory = Mock()
        mock_term_service = Mock()

        mock_uow.service_factory = mock_service_factory
        mock_service_factory.get_service.return_value = mock_term_service

        # コンテキストマネージャとして機能させる
        mock_uow.__enter__ = Mock(return_value=mock_uow)
        mock_uow.__exit__ = Mock(return_value=None)

        return mock_uow

    @pytest.fixture
    def mock_unit_of_work_factory(self, mock_unit_of_work: Mock) -> Mock:
        """モックのUnit of Work Factoryを作成"""
        return Mock(return_value=mock_unit_of_work)

    @pytest.fixture
    def term_application_service(self, mock_unit_of_work_factory: Mock) -> TerminologyApplicationService:
        """TerminologyApplicationServiceのインスタンスを作成"""
        return TerminologyApplicationService(mock_unit_of_work_factory)  # type: ignore[arg-type]

    @pytest.fixture
    def sample_term_read(self) -> TermRead:
        """テスト用のTermReadデータを作成"""
        return TermRead(
            id=uuid.uuid4(),
            key="test-key",
            title="テスト用語",
            description="説明文",
            status=TermStatus.DRAFT,
            source_url=None,
        )

    def test_create_term(
        self,
        term_application_service: TerminologyApplicationService,
        mock_unit_of_work: Mock,
        sample_term_read: TermRead,
    ) -> None:
        """正常系: 用語作成成功"""
        mock_term_service = mock_unit_of_work.service_factory.get_service.return_value
        mock_term_service.create.return_value = sample_term_read
        # create後にget_by_idが呼ばれるため、その戻り値もモック設定
        mock_term_service.get_by_id.return_value = sample_term_read

        result = term_application_service.create(key="test-key", title="テスト用語")

        assert isinstance(result, TermRead)
        assert result.key == "test-key"
        assert result.title == "テスト用語"
        mock_term_service.create.assert_called_once()
        mock_term_service.get_by_id.assert_called_once()

    def test_create_term_validation_error(self, term_application_service: TerminologyApplicationService) -> None:
        """異常系: 用語作成時のバリデーションエラー"""
        with pytest.raises(TermKeyValidationError, match="用語キーを入力してください"):
            term_application_service.create(key="", title="テスト用語")

    def test_get_by_key(
        self,
        term_application_service: TerminologyApplicationService,
        mock_unit_of_work: Mock,
        sample_term_read: TermRead,
    ) -> None:
        """正常系: キーで用語取得"""
        mock_term_service = mock_unit_of_work.service_factory.get_service.return_value
        mock_term_service.get_by_key.return_value = sample_term_read

        result = term_application_service.get_by_key("test-key")

        assert isinstance(result, TermRead)
        assert result == sample_term_read
        mock_term_service.get_by_key.assert_called_once_with("test-key")

    def test_get_all(
        self,
        term_application_service: TerminologyApplicationService,
        mock_unit_of_work: Mock,
        sample_term_read: TermRead,
    ) -> None:
        """正常系: 全用語取得"""
        mock_term_service = mock_unit_of_work.service_factory.get_service.return_value
        mock_term_service.get_all.return_value = [sample_term_read]

        result = term_application_service.get_all()

        assert len(result) == 1
        assert result[0].key == sample_term_read.key
        mock_term_service.get_all.assert_called_once()

    def test_delete(
        self,
        term_application_service: TerminologyApplicationService,
        mock_unit_of_work: Mock,
    ) -> None:
        """正常系: 用語削除成功"""
        mock_term_service = mock_unit_of_work.service_factory.get_service.return_value
        # deleteメソッドはboolを返す
        mock_term_service.delete.return_value = True

        term_id = uuid.uuid4()
        result = term_application_service.delete(term_id)

        assert result is True
        mock_term_service.delete.assert_called_once_with(term_id)

    def test_import_from_csv(
        self,
        term_application_service: TerminologyApplicationService,
        mock_unit_of_work: Mock,
        tmp_path: Path,
    ) -> None:
        """正常系: CSV インポート"""
        mock_term_service = mock_unit_of_work.service_factory.get_service.return_value

        # ImportResultオブジェクトをモック
        mock_import_result = Mock()
        mock_import_result.success_count = EXPECTED_CSV_IMPORT_SUCCESS
        mock_import_result.failed_count = 0
        mock_import_result.errors = []
        mock_term_service.import_from_csv.return_value = mock_import_result

        csv_file = tmp_path / "terms.csv"
        csv_file.write_text("key,title,description\ntest1,用語1,説明1\n")

        result = term_application_service.import_from_csv(str(csv_file))

        assert result["success_count"] == EXPECTED_CSV_IMPORT_SUCCESS
        assert result["failed_count"] == 0
        mock_term_service.import_from_csv.assert_called_once()

    def test_export_to_csv(
        self,
        term_application_service: TerminologyApplicationService,
        mock_unit_of_work: Mock,
        sample_term_read: TermRead,
        tmp_path: Path,
    ) -> None:
        """正常系: CSV エクスポート"""
        mock_term_service = mock_unit_of_work.service_factory.get_service.return_value
        # export_to_csvは直接件数を返す
        mock_term_service.export_to_csv.return_value = EXPECTED_CSV_EXPORT_COUNT

        csv_file = tmp_path / "export.csv"
        count = term_application_service.export_to_csv(str(csv_file))

        assert count == EXPECTED_CSV_EXPORT_COUNT
        mock_term_service.export_to_csv.assert_called_once()

    def test_search_delegates(
        self,
        term_application_service: TerminologyApplicationService,
        mock_unit_of_work: Mock,
        sample_term_read: TermRead,
    ) -> None:
        mock_term_service = mock_unit_of_work.service_factory.get_service.return_value
        mock_term_service.search.return_value = [sample_term_read]

        out = term_application_service.search(
            "llm", tags=[uuid.uuid4()], status=TermStatus.APPROVED, include_synonyms=False
        )
        assert out == [sample_term_read]
        mock_term_service.search.assert_called_once()
