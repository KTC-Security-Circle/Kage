"""ProjectApplicationServiceのテストケース

このモジュールは、ProjectApplicationServiceクラスの
Application Service層の機能をテストするためのテストケースを提供します。

テスト対象：
- create_project: プロジェクト作成のApplication Service層ロジック
- update_project: プロジェクト更新のApplication Service層ロジック
- delete_project: プロジェクト削除のApplication Service層ロジック
- get_project_by_id: ID指定プロジェクト取得
- get_all_projects: 全プロジェクト取得
- search_projects_by_title: タイトル検索
"""

import uuid
from unittest.mock import Mock

import pytest

from logic.application.project_application_service import ProjectApplicationService
from logic.commands.project_commands import (
    CreateProjectCommand,
    DeleteProjectCommand,
    UpdateProjectCommand,
)
from logic.queries.project_queries import (
    GetAllProjectsQuery,
    GetProjectByIdQuery,
    SearchProjectsByTitleQuery,
)
from models import ProjectRead, ProjectStatus


class TestProjectApplicationService:
    """ProjectApplicationServiceのApplication Service層機能をテストするクラス"""

    @pytest.fixture
    def mock_unit_of_work(self) -> Mock:
        """モックのUnit of Workを作成"""
        mock_uow = Mock()
        mock_service_factory = Mock()
        mock_project_service = Mock()

        # [AI GENERATED] モックの階層構造を設定
        mock_uow.service_factory = mock_service_factory
        mock_service_factory.create_project_service.return_value = mock_project_service

        # [AI GENERATED] コンテキストマネージャとして機能させる
        mock_uow.__enter__ = Mock(return_value=mock_uow)
        mock_uow.__exit__ = Mock(return_value=None)

        return mock_uow

    @pytest.fixture
    def mock_unit_of_work_factory(self, mock_unit_of_work: Mock) -> Mock:
        """モックのUnit of Work Factoryを作成"""
        return Mock(return_value=mock_unit_of_work)

    @pytest.fixture
    def project_application_service(self, mock_unit_of_work_factory: Mock) -> ProjectApplicationService:
        """ProjectApplicationServiceのインスタンスを作成"""
        return ProjectApplicationService(mock_unit_of_work_factory)  # type: ignore[arg-type]

    @pytest.fixture
    def sample_project_read(self) -> ProjectRead:
        """テスト用のProjectReadデータを作成"""
        return ProjectRead(
            id=uuid.uuid4(),
            title="サンプルプロジェクト",
            description="テスト用のプロジェクト",
            status=ProjectStatus.ACTIVE,
        )

    def test_create_project_success(
        self,
        project_application_service: ProjectApplicationService,
        mock_unit_of_work: Mock,
        sample_project_read: ProjectRead,
    ) -> None:
        """正常系: プロジェクト作成成功"""
        # モックの設定
        mock_project_service = mock_unit_of_work.service_factory.create_project_service.return_value
        mock_project_service.create_project.return_value = sample_project_read

        # コマンド作成
        command = CreateProjectCommand(
            title="新しいプロジェクト",
            description="テスト用プロジェクト",
            status=ProjectStatus.ACTIVE,
        )

        # 実行
        result = project_application_service.create_project(command)

        # 検証
        assert isinstance(result, ProjectRead)
        assert result.title == sample_project_read.title
        mock_project_service.create_project.assert_called_once()
        mock_unit_of_work.commit.assert_called_once()

    def test_create_project_validation_error(self, project_application_service: ProjectApplicationService) -> None:
        """異常系: プロジェクト作成時のバリデーションエラー"""
        # 空のタイトルでコマンド作成
        command = CreateProjectCommand(title="", description="テスト用プロジェクト")

        # 実行と検証
        with pytest.raises(ValueError, match="プロジェクトタイトルを入力してください"):
            project_application_service.create_project(command)

    def test_get_project_by_id_success(
        self,
        project_application_service: ProjectApplicationService,
        mock_unit_of_work: Mock,
        sample_project_read: ProjectRead,
    ) -> None:
        """正常系: ID指定プロジェクト取得成功"""
        # モックの設定
        mock_project_service = mock_unit_of_work.service_factory.create_project_service.return_value
        mock_project_service.get_project_by_id.return_value = sample_project_read

        # クエリ作成
        query = GetProjectByIdQuery(project_id=sample_project_read.id)

        # 実行
        result = project_application_service.get_project_by_id(query)

        # 検証
        assert result == sample_project_read
        mock_project_service.get_project_by_id.assert_called_once_with(sample_project_read.id)

    def test_get_project_by_id_not_found(
        self,
        project_application_service: ProjectApplicationService,
        mock_unit_of_work: Mock,
    ) -> None:
        """異常系: ID指定プロジェクト取得でプロジェクトが見つからない"""
        # モックの設定
        mock_project_service = mock_unit_of_work.service_factory.create_project_service.return_value
        mock_project_service.get_project_by_id.return_value = None

        project_id = uuid.uuid4()
        query = GetProjectByIdQuery(project_id=project_id)

        # 実行と検証
        with pytest.raises(ValueError, match=f"プロジェクトが見つかりません: {project_id}"):
            project_application_service.get_project_by_id(query)

    def test_get_all_projects(
        self,
        project_application_service: ProjectApplicationService,
        mock_unit_of_work: Mock,
        sample_project_read: ProjectRead,
    ) -> None:
        """正常系: 全プロジェクト取得"""
        # モックの設定
        mock_project_service = mock_unit_of_work.service_factory.create_project_service.return_value
        mock_project_service.get_all_projects.return_value = [sample_project_read]

        # クエリ作成
        query = GetAllProjectsQuery()

        # 実行
        result = project_application_service.get_all_projects(query)

        # 検証
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0] == sample_project_read
        mock_project_service.get_all_projects.assert_called_once()

    def test_search_projects_by_title(
        self,
        project_application_service: ProjectApplicationService,
        mock_unit_of_work: Mock,
        sample_project_read: ProjectRead,
    ) -> None:
        """正常系: タイトル検索"""
        # モックの設定
        mock_project_service = mock_unit_of_work.service_factory.create_project_service.return_value
        mock_project_service.search_projects.return_value = [sample_project_read]

        # クエリ作成
        search_title = "サンプル"
        query = SearchProjectsByTitleQuery(title_query=search_title)

        # 実行
        result = project_application_service.search_projects_by_title(query)

        # 検証
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0] == sample_project_read
        mock_project_service.search_projects.assert_called_once_with(search_title)

    def test_update_project_success(
        self,
        project_application_service: ProjectApplicationService,
        mock_unit_of_work: Mock,
        sample_project_read: ProjectRead,
    ) -> None:
        """正常系: プロジェクト更新成功"""
        # モックの設定
        mock_project_service = mock_unit_of_work.service_factory.create_project_service.return_value
        updated_project = ProjectRead(
            id=sample_project_read.id,
            title="更新されたプロジェクト",
            description=sample_project_read.description,
            status=sample_project_read.status,
        )
        mock_project_service.update_project.return_value = updated_project

        # コマンド作成
        command = UpdateProjectCommand(
            project_id=sample_project_read.id,
            title="更新されたプロジェクト",
            description=sample_project_read.description,
        )

        # 実行
        result = project_application_service.update_project(command)

        # 検証
        assert isinstance(result, ProjectRead)
        assert result.title == "更新されたプロジェクト"
        mock_project_service.update_project.assert_called_once()
        mock_unit_of_work.commit.assert_called_once()

    def test_update_project_validation_error(self, project_application_service: ProjectApplicationService) -> None:
        """異常系: プロジェクト更新時のバリデーションエラー"""
        # 空のタイトルでコマンド作成
        command = UpdateProjectCommand(
            project_id=uuid.uuid4(),
            title="",  # 空のタイトル
        )

        # 実行と検証
        with pytest.raises(ValueError, match="プロジェクトタイトルを入力してください"):
            project_application_service.update_project(command)

    def test_update_project_no_title_update(
        self,
        project_application_service: ProjectApplicationService,
        mock_unit_of_work: Mock,
        sample_project_read: ProjectRead,
    ) -> None:
        """正常系: タイトル更新なしのプロジェクト更新"""
        # モックの設定
        mock_project_service = mock_unit_of_work.service_factory.create_project_service.return_value
        updated_project = ProjectRead(
            id=sample_project_read.id,
            title=sample_project_read.title,
            description="更新された説明",
            status=sample_project_read.status,
        )
        mock_project_service.update_project.return_value = updated_project

        # コマンド作成（titleはNone）
        command = UpdateProjectCommand(
            project_id=sample_project_read.id,
            description="更新された説明",
        )

        # 実行
        result = project_application_service.update_project(command)

        # 検証
        assert isinstance(result, ProjectRead)
        assert result.description == "更新された説明"
        mock_project_service.update_project.assert_called_once()
        mock_unit_of_work.commit.assert_called_once()

    def test_delete_project_success(
        self,
        project_application_service: ProjectApplicationService,
        mock_unit_of_work: Mock,
    ) -> None:
        """正常系: プロジェクト削除成功"""
        # モックの設定
        mock_project_service = mock_unit_of_work.service_factory.create_project_service.return_value
        mock_project_service.delete_project.return_value = True  # 削除成功

        project_id = uuid.uuid4()
        command = DeleteProjectCommand(project_id=project_id)

        # 実行
        project_application_service.delete_project(command)

        # 検証
        mock_project_service.delete_project.assert_called_once_with(project_id)
        mock_unit_of_work.commit.assert_called_once()

    def test_delete_project_failure(
        self,
        project_application_service: ProjectApplicationService,
        mock_unit_of_work: Mock,
    ) -> None:
        """異常系: プロジェクト削除失敗"""
        # モックの設定
        mock_project_service = mock_unit_of_work.service_factory.create_project_service.return_value
        mock_project_service.delete_project.return_value = False  # 削除失敗

        project_id = uuid.uuid4()
        command = DeleteProjectCommand(project_id=project_id)

        # 実行と検証
        with pytest.raises(ValueError, match=f"プロジェクトの削除に失敗しました: {project_id}"):
            project_application_service.delete_project(command)
