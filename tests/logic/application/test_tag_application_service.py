"""TagApplicationServiceのテストケース

このモジュールは、TagApplicationServiceクラスの
Application Service層の機能をテストするためのテストケースを提供します。

テスト対象：
- create_tag: タグ作成のApplication Service層ロジック
- update_tag: タグ更新のApplication Service層ロジック
- delete_tag: タグ削除のApplication Service層ロジック
- get_tag_by_id: ID指定タグ取得
- get_all_tags: 全タグ取得
- search_tags_by_name: 名前検索
"""

import uuid
from unittest.mock import Mock

import pytest

from logic.application.tag_application_service import TagApplicationService
from logic.commands.tag_commands import (
    CreateTagCommand,
    DeleteTagCommand,
    UpdateTagCommand,
)
from logic.queries.tag_queries import (
    GetAllTagsQuery,
    GetTagByIdQuery,
    SearchTagsByNameQuery,
)
from models import TagRead


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
        mock_service_factory.create_tag_service.return_value = mock_tag_service

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

    def test_create_tag_success(
        self,
        tag_application_service: TagApplicationService,
        mock_unit_of_work: Mock,
        sample_tag_read: TagRead,
    ) -> None:
        """正常系: タグ作成成功"""
        # モックの設定
        mock_tag_service = mock_unit_of_work.service_factory.create_tag_service.return_value
        mock_tag_service.create_tag.return_value = sample_tag_read

        # コマンド作成
        command = CreateTagCommand(
            name="新しいタグ",
        )

        # 実行
        result = tag_application_service.create_tag(command)

        # 検証
        assert isinstance(result, TagRead)
        assert result.name == sample_tag_read.name
        mock_tag_service.create_tag.assert_called_once()
        mock_unit_of_work.commit.assert_called_once()

    def test_create_tag_validation_error(self, tag_application_service: TagApplicationService) -> None:
        """異常系: タグ作成時のバリデーションエラー"""
        # 空の名前でコマンド作成
        command = CreateTagCommand(name="")

        # 実行と検証
        with pytest.raises(ValueError, match="タグ名を入力してください"):
            tag_application_service.create_tag(command)

    def test_get_tag_by_id_success(
        self,
        tag_application_service: TagApplicationService,
        mock_unit_of_work: Mock,
        sample_tag_read: TagRead,
    ) -> None:
        """正常系: ID指定タグ取得成功"""
        # モックの設定
        mock_tag_service = mock_unit_of_work.service_factory.create_tag_service.return_value
        mock_tag_service.get_tag_by_id.return_value = sample_tag_read

        # クエリ作成
        query = GetTagByIdQuery(tag_id=sample_tag_read.id)

        # 実行
        result = tag_application_service.get_tag_by_id(query)

        # 検証
        assert result == sample_tag_read
        mock_tag_service.get_tag_by_id.assert_called_once_with(sample_tag_read.id)

    def test_get_tag_by_id_not_found(
        self,
        tag_application_service: TagApplicationService,
        mock_unit_of_work: Mock,
    ) -> None:
        """異常系: ID指定タグ取得でタグが見つからない"""
        # モックの設定
        mock_tag_service = mock_unit_of_work.service_factory.create_tag_service.return_value
        mock_tag_service.get_tag_by_id.return_value = None

        tag_id = uuid.uuid4()
        query = GetTagByIdQuery(tag_id=tag_id)

        # 実行と検証
        with pytest.raises(ValueError, match=f"タグが見つかりません: {tag_id}"):
            tag_application_service.get_tag_by_id(query)

    def test_get_all_tags(
        self,
        tag_application_service: TagApplicationService,
        mock_unit_of_work: Mock,
        sample_tag_read: TagRead,
    ) -> None:
        """正常系: 全タグ取得"""
        # モックの設定
        mock_tag_service = mock_unit_of_work.service_factory.create_tag_service.return_value
        mock_tag_service.get_all_tags.return_value = [sample_tag_read]

        # クエリ作成
        query = GetAllTagsQuery()

        # 実行
        result = tag_application_service.get_all_tags(query)

        # 検証
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0] == sample_tag_read
        mock_tag_service.get_all_tags.assert_called_once()

    def test_search_tags_by_name(
        self,
        tag_application_service: TagApplicationService,
        mock_unit_of_work: Mock,
        sample_tag_read: TagRead,
    ) -> None:
        """正常系: 名前検索"""
        # モックの設定
        mock_tag_service = mock_unit_of_work.service_factory.create_tag_service.return_value
        mock_tag_service.search_tags.return_value = [sample_tag_read]

        # クエリ作成
        search_name = "サンプル"
        query = SearchTagsByNameQuery(name_query=search_name)

        # 実行
        result = tag_application_service.search_tags_by_name(query)

        # 検証
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0] == sample_tag_read
        mock_tag_service.search_tags.assert_called_once_with(search_name)

    def test_update_tag_success(
        self,
        tag_application_service: TagApplicationService,
        mock_unit_of_work: Mock,
        sample_tag_read: TagRead,
    ) -> None:
        """正常系: タグ更新成功"""
        # モックの設定
        mock_tag_service = mock_unit_of_work.service_factory.create_tag_service.return_value
        updated_tag = TagRead(
            id=sample_tag_read.id,
            name="更新されたタグ",
        )
        mock_tag_service.update_tag.return_value = updated_tag

        # コマンド作成
        command = UpdateTagCommand(
            tag_id=sample_tag_read.id,
            name="更新されたタグ",
        )

        # 実行
        result = tag_application_service.update_tag(command)

        # 検証
        assert isinstance(result, TagRead)
        assert result.name == "更新されたタグ"
        mock_tag_service.update_tag.assert_called_once()
        mock_unit_of_work.commit.assert_called_once()

    def test_update_tag_validation_error(self, tag_application_service: TagApplicationService) -> None:
        """異常系: タグ更新時のバリデーションエラー"""
        # 空の名前でコマンド作成
        command = UpdateTagCommand(
            tag_id=uuid.uuid4(),
            name="",  # 空の名前
        )

        # 実行と検証
        with pytest.raises(ValueError, match="タグ名を入力してください"):
            tag_application_service.update_tag(command)

    def test_delete_tag_success(
        self,
        tag_application_service: TagApplicationService,
        mock_unit_of_work: Mock,
    ) -> None:
        """正常系: タグ削除成功"""
        # モックの設定
        mock_tag_service = mock_unit_of_work.service_factory.create_tag_service.return_value
        mock_tag_service.delete_tag.return_value = True  # 削除成功

        tag_id = uuid.uuid4()
        command = DeleteTagCommand(tag_id=tag_id)

        # 実行
        tag_application_service.delete_tag(command)

        # 検証
        mock_tag_service.delete_tag.assert_called_once_with(tag_id)
        mock_unit_of_work.commit.assert_called_once()

    def test_delete_tag_failure(
        self,
        tag_application_service: TagApplicationService,
        mock_unit_of_work: Mock,
    ) -> None:
        """異常系: タグ削除失敗"""
        # モックの設定
        mock_tag_service = mock_unit_of_work.service_factory.create_tag_service.return_value
        mock_tag_service.delete_tag.return_value = False  # 削除失敗

        tag_id = uuid.uuid4()
        command = DeleteTagCommand(tag_id=tag_id)

        # 実行と検証
        with pytest.raises(ValueError, match=f"タグの削除に失敗しました: {tag_id}"):
            tag_application_service.delete_tag(command)
