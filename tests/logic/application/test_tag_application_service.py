"""TagApplicationServiceのテストケース（現行API対応）

このモジュールは、TagApplicationServiceクラスの
Application Service層の機能をテストする。

対象API:
- create(name, description?, color?)
- update(tag_id, TagUpdate)
- delete(tag_id)
- get_by_id(tag_id)
- get_all_tags()
- search_by_name(query)
"""

import uuid
from unittest.mock import Mock

import pytest

from errors import NotFoundError
from logic.application.tag_application_service import TagApplicationService
from models import TagRead, TagUpdate


class TestTagApplicationService:
    """TagApplicationServiceのApplication Service層機能をテストするクラス"""

    @pytest.fixture
    def mock_unit_of_work(self) -> Mock:
        """モックのUnit of Workを作成"""
        mock_uow = Mock()
        mock_service_factory = Mock()
        mock_tag_service = Mock()

        # [AI GENERATED] モックの階層構造を設定
        mock_uow.service_factory = mock_service_factory
        mock_service_factory.get_service.return_value = mock_tag_service

        # [AI GENERATED] コンテキストマネージャとして機能させる
        mock_uow.__enter__ = Mock(return_value=mock_uow)
        mock_uow.__exit__ = Mock(return_value=None)

        return mock_uow

    @pytest.fixture
    def mock_unit_of_work_factory(self, mock_unit_of_work: Mock) -> Mock:
        """モックのUnit of Work Factoryを作成"""
        return Mock(return_value=mock_unit_of_work)

    @pytest.fixture
    def tag_application_service(self, mock_unit_of_work_factory: Mock) -> TagApplicationService:
        """TagApplicationServiceのインスタンスを作成"""
        return TagApplicationService(mock_unit_of_work_factory)  # type: ignore[arg-type]

    @pytest.fixture
    def sample_tag_read(self) -> TagRead:
        """テスト用のTagReadデータを作成"""
        return TagRead(
            id=uuid.uuid4(),
            name="サンプルタグ",
        )

    def test_create_success(
        self,
        tag_application_service: TagApplicationService,
        mock_unit_of_work: Mock,
        sample_tag_read: TagRead,
    ) -> None:
        """正常系: タグ作成成功"""
        # モックの設定
        mock_tag_service = mock_unit_of_work.service_factory.get_service.return_value
        mock_tag_service.create.return_value = sample_tag_read

        # 実行
        result = tag_application_service.create(name="新しいタグ")

        # 検証
        assert isinstance(result, TagRead)
        assert result.name == sample_tag_read.name
        mock_tag_service.create.assert_called_once()

    def test_create_validation_error(self, tag_application_service: TagApplicationService) -> None:
        """異常系: タグ作成時のバリデーションエラー"""
        # 実行と検証
        from logic.application.tag_application_service import TagValidationError

        with pytest.raises(TagValidationError, match="タグ名を入力してください"):
            tag_application_service.create("")

    def test_get_by_id_success(
        self,
        tag_application_service: TagApplicationService,
        mock_unit_of_work: Mock,
        sample_tag_read: TagRead,
    ) -> None:
        """正常系: ID指定タグ取得成功"""
        # モックの設定
        mock_tag_service = mock_unit_of_work.service_factory.get_service.return_value
        mock_tag_service.get_by_id.return_value = sample_tag_read

        # 実行
        result = tag_application_service.get_by_id(sample_tag_read.id)

        # 検証
        assert result == sample_tag_read
        mock_tag_service.get_by_id.assert_called_once_with(sample_tag_read.id)

    def test_get_by_id_not_found(
        self,
        tag_application_service: TagApplicationService,
        mock_unit_of_work: Mock,
    ) -> None:
        """異常系: ID指定タグ取得でタグが見つからない"""
        # モックの設定
        mock_tag_service = mock_unit_of_work.service_factory.get_service.return_value
        mock_tag_service.get_by_id.side_effect = NotFoundError("not found")

        tag_id = uuid.uuid4()
        # 実行と検証
        with pytest.raises(NotFoundError, match="not found"):
            tag_application_service.get_by_id(tag_id)

    def test_get_all_tags(
        self,
        tag_application_service: TagApplicationService,
        mock_unit_of_work: Mock,
        sample_tag_read: TagRead,
    ) -> None:
        """正常系: 全タグ取得"""
        # モックの設定
        mock_tag_service = mock_unit_of_work.service_factory.get_service.return_value
        mock_tag_service.get_all.return_value = [sample_tag_read]

        # 実行
        result = tag_application_service.get_all_tags()

        # 検証
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0] == sample_tag_read
        mock_tag_service.get_all.assert_called_once()

    def test_search_by_name(
        self,
        tag_application_service: TagApplicationService,
        mock_unit_of_work: Mock,
        sample_tag_read: TagRead,
    ) -> None:
        """正常系: 名前検索"""
        # モックの設定
        mock_tag_service = mock_unit_of_work.service_factory.get_service.return_value
        mock_tag_service.search_by_name.return_value = [sample_tag_read]

        search_name = "サンプル"

        # 実行
        result = tag_application_service.search_by_name(search_name)

        # 検証
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0] == sample_tag_read
        mock_tag_service.search_by_name.assert_called_once_with(search_name)

    def test_update_success(
        self,
        tag_application_service: TagApplicationService,
        mock_unit_of_work: Mock,
        sample_tag_read: TagRead,
    ) -> None:
        """正常系: タグ更新成功"""
        # モックの設定
        mock_tag_service = mock_unit_of_work.service_factory.get_service.return_value
        updated_tag = TagRead(
            id=sample_tag_read.id,
            name="更新されたタグ",
        )
        mock_tag_service.update.return_value = updated_tag

        update_data = TagUpdate(name="更新されたタグ")

        # 実行
        result = tag_application_service.update(sample_tag_read.id, update_data)

        # 検証
        assert isinstance(result, TagRead)
        assert result.name == "更新されたタグ"
        mock_tag_service.update.assert_called_once()

    def test_update_validation_error(self, tag_application_service: TagApplicationService) -> None:
        """異常系: タグ更新時のバリデーションエラー"""
        # 実行と検証
        from logic.application.tag_application_service import TagValidationError

        with pytest.raises(TagValidationError, match="タグ名を入力してください"):
            tag_application_service.create("")

    def test_delete_success(
        self,
        tag_application_service: TagApplicationService,
        mock_unit_of_work: Mock,
    ) -> None:
        """正常系: タグ削除成功"""
        # モックの設定
        mock_tag_service = mock_unit_of_work.service_factory.get_service.return_value
        mock_tag_service.delete.return_value = True  # 削除成功

        tag_id = uuid.uuid4()
        # 実行
        tag_application_service.delete(tag_id)

        # 検証
        mock_tag_service.delete.assert_called_once_with(tag_id)

    def test_delete_failure(
        self,
        tag_application_service: TagApplicationService,
        mock_unit_of_work: Mock,
    ) -> None:
        """異常系: タグ削除失敗"""
        # モックの設定
        mock_tag_service = mock_unit_of_work.service_factory.get_service.return_value
        mock_tag_service.delete.return_value = False  # 削除失敗

        tag_id = uuid.uuid4()
        # 実行と検証
        result = tag_application_service.delete(tag_id)
        assert result is False

    def test_search_alias(
        self,
        tag_application_service: TagApplicationService,
        mock_unit_of_work: Mock,
        sample_tag_read: TagRead,
    ) -> None:
        """search は search_by_name のエイリアスとして動作する"""
        mock_tag_service = mock_unit_of_work.service_factory.get_service.return_value
        mock_tag_service.search_by_name.return_value = [sample_tag_read]

        res = tag_application_service.search("x")
        assert res == [sample_tag_read]
        mock_tag_service.search_by_name.assert_called_once_with("x")
