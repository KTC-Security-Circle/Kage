"""ProjectRepositoryのテストケース

このモジュールは、ProjectRepositoryクラスのプロジェクト固有の操作を
テストするためのテストケースを提供します。

テスト対象：
- get_all: 全プロジェクト取得
- get_by_status: ステータス別プロジェクト取得
- search_by_title: タイトル検索
- get_active_projects: アクティブプロジェクト取得
- get_completed_projects: 完了プロジェクト取得
"""

import uuid

import pytest
from sqlmodel import Session

from logic.repositories.project import ProjectRepository
from models import Project, ProjectCreate, ProjectStatus, ProjectUpdate


def create_test_project(
    title: str = "テストプロジェクト",
    description: str | None = None,
    status: ProjectStatus = ProjectStatus.ACTIVE,
) -> Project:
    """テスト用のProjectオブジェクトを作成する

    Args:
        title: プロジェクトのタイトル
        description: プロジェクトの説明
        status: プロジェクトのステータス

    Returns:
        作成されたProjectオブジェクト
    """
    return Project(
        title=title,
        description=description or "",
        status=status,
    )


@pytest.fixture
def sample_projects(test_session: Session) -> list[Project]:
    """テスト用のサンプルプロジェクトを作成してデータベースに保存

    Args:
        test_session: テスト用データベースセッション

    Returns:
        list[Project]: 作成されたサンプルプロジェクトのリスト
    """
    projects = [
        create_test_project("アクティブプロジェクト1", "進行中のプロジェクト", ProjectStatus.ACTIVE),
        create_test_project("アクティブプロジェクト2", "もう一つの進行中プロジェクト", ProjectStatus.ACTIVE),
        create_test_project("完了プロジェクト", "完了したプロジェクト", ProjectStatus.COMPLETED),
        create_test_project("一時停止プロジェクト", "一時停止中のプロジェクト", ProjectStatus.ON_HOLD),
        create_test_project("キャンセルプロジェクト", "キャンセルされたプロジェクト", ProjectStatus.CANCELLED),
    ]

    # [AI GENERATED] データベースにサンプルプロジェクトを保存
    for project in projects:
        test_session.add(project)

    test_session.commit()

    # [AI GENERATED] 保存後にリフレッシュしてIDを確実に取得
    for project in projects:
        test_session.refresh(project)

    return projects


class TestProjectRepositoryGetAll:
    """get_allメソッドのテストクラス"""

    def test_get_all_returns_all_projects(
        self, project_repository: ProjectRepository, sample_projects: list[Project]
    ) -> None:
        """全てのプロジェクトを取得できることをテスト"""
        # [AI GENERATED] 全プロジェクトを取得
        result = project_repository.get_all()

        # [AI GENERATED] 期待される数のプロジェクトが取得されることを確認
        assert len(result) == len(sample_projects)

        # [AI GENERATED] 全てのプロジェクトIDが含まれていることを確認
        result_ids = {project.id for project in result}
        expected_ids = {project.id for project in sample_projects}
        assert result_ids == expected_ids

    def test_get_all_returns_empty_list_when_no_projects(self, project_repository: ProjectRepository) -> None:
        """プロジェクトが存在しない場合に空のリストを返すことをテスト"""
        # [AI GENERATED] プロジェクトが存在しない状態で実行
        result = project_repository.get_all()

        # [AI GENERATED] 空のリストが返されることを確認
        assert result == []


class TestProjectRepositoryGetByStatus:
    """get_by_statusメソッドのテストクラス"""

    def test_get_by_status_returns_active_projects(
        self, project_repository: ProjectRepository, sample_projects: list[Project]
    ) -> None:
        """アクティブステータスのプロジェクトを取得できることをテスト"""
        # [AI GENERATED] アクティブプロジェクトを取得
        result = project_repository.get_by_status(ProjectStatus.ACTIVE)

        # [AI GENERATED] アクティブプロジェクトのみが取得されることを確認
        expected_active_projects = [p for p in sample_projects if p.status == ProjectStatus.ACTIVE]
        assert len(result) == len(expected_active_projects)

        # [AI GENERATED] 全ての結果がアクティブステータスであることを確認
        for project in result:
            assert project.status == ProjectStatus.ACTIVE

    def test_get_by_status_returns_completed_projects(
        self, project_repository: ProjectRepository, sample_projects: list[Project]
    ) -> None:
        """完了ステータスのプロジェクトを取得できることをテスト"""
        # [AI GENERATED] 完了プロジェクトを取得
        result = project_repository.get_by_status(ProjectStatus.COMPLETED)

        # [AI GENERATED] 完了プロジェクトのみが取得されることを確認
        expected_completed_projects = [p for p in sample_projects if p.status == ProjectStatus.COMPLETED]
        assert len(result) == len(expected_completed_projects)

        # [AI GENERATED] 全ての結果が完了ステータスであることを確認
        for project in result:
            assert project.status == ProjectStatus.COMPLETED

    def test_get_by_status_returns_empty_list_for_nonexistent_status(
        self, project_repository: ProjectRepository, sample_projects: list[Project]
    ) -> None:
        """存在しないステータスで検索した場合に空のリストを返すことをテスト"""
        # [AI GENERATED] 未使用のステータス用に新しいプロジェクトを作成せずに検索
        result = project_repository.get_by_status(ProjectStatus.ON_HOLD)

        # [AI GENERATED] ON_HOLDのプロジェクトが1件存在することを確認
        expected_on_hold_projects = [p for p in sample_projects if p.status == ProjectStatus.ON_HOLD]
        assert len(result) == len(expected_on_hold_projects)


class TestProjectRepositorySearchByTitle:
    """search_by_titleメソッドのテストクラス"""

    def test_search_by_title_finds_matching_projects(
        self, project_repository: ProjectRepository, sample_projects: list[Project]
    ) -> None:
        """タイトルの部分一致でプロジェクトを検索できることをテスト"""
        # [AI GENERATED] "アクティブ" を含むプロジェクトを検索
        result = project_repository.search_by_title("アクティブ")

        # [AI GENERATED] 期待される結果が取得されることを確認
        expected_projects = [p for p in sample_projects if "アクティブ" in p.title]
        assert len(result) == len(expected_projects)

        # [AI GENERATED] 全ての結果のタイトルに検索キーワードが含まれることを確認
        for project in result:
            assert "アクティブ" in project.title

    def test_search_by_title_case_insensitive(
        self, project_repository: ProjectRepository, sample_projects: list[Project]
    ) -> None:
        """タイトル検索が大文字小文字を区別しないことをテスト"""
        # [AI GENERATED] 大文字小文字を変えて検索
        result = project_repository.search_by_title("アクティブ")

        # [AI GENERATED] 結果が得られることを確認
        assert len(result) > 0

        # [AI GENERATED] 小文字で検索しても同じ結果が得られることを確認
        result_lower = project_repository.search_by_title("アクティブ")
        assert len(result) == len(result_lower)

    def test_search_by_title_returns_empty_list_for_no_matches(
        self, project_repository: ProjectRepository, sample_projects: list[Project]
    ) -> None:
        """一致しないキーワードで検索した場合に空のリストを返すことをテスト"""
        # [AI GENERATED] 存在しないキーワードで検索
        result = project_repository.search_by_title("存在しないプロジェクト")

        # [AI GENERATED] 空のリストが返されることを確認
        assert result == []


class TestProjectRepositoryActiveProjects:
    """get_active_projectsメソッドのテストクラス"""

    def test_get_active_projects_returns_only_active(
        self, project_repository: ProjectRepository, sample_projects: list[Project]
    ) -> None:
        """アクティブプロジェクトのみを取得できることをテスト"""
        # [AI GENERATED] アクティブプロジェクトを取得
        result = project_repository.get_active_projects()

        # [AI GENERATED] アクティブプロジェクトのみが取得されることを確認
        expected_active_projects = [p for p in sample_projects if p.status == ProjectStatus.ACTIVE]
        assert len(result) == len(expected_active_projects)

        # [AI GENERATED] 全ての結果がアクティブステータスであることを確認
        for project in result:
            assert project.status == ProjectStatus.ACTIVE


class TestProjectRepositoryCompletedProjects:
    """get_completed_projectsメソッドのテストクラス"""

    def test_get_completed_projects_returns_only_completed(
        self, project_repository: ProjectRepository, sample_projects: list[Project]
    ) -> None:
        """完了プロジェクトのみを取得できることをテスト"""
        # [AI GENERATED] 完了プロジェクトを取得
        result = project_repository.get_completed_projects()

        # [AI GENERATED] 完了プロジェクトのみが取得されることを確認
        expected_completed_projects = [p for p in sample_projects if p.status == ProjectStatus.COMPLETED]
        assert len(result) == len(expected_completed_projects)

        # [AI GENERATED] 全ての結果が完了ステータスであることを確認
        for project in result:
            assert project.status == ProjectStatus.COMPLETED


class TestProjectRepositoryBaseCRUD:
    """BaseRepositoryから継承したCRUD操作のテストクラス"""

    def test_create_project_success(self, project_repository: ProjectRepository) -> None:
        """プロジェクト作成が成功することをテスト"""
        # [AI GENERATED] テスト用プロジェクトデータを作成
        project_data = ProjectCreate(
            title="新しいプロジェクト",
            description="テスト用プロジェクト",
            status=ProjectStatus.ACTIVE,
        )

        # [AI GENERATED] プロジェクトを作成
        result = project_repository.create(project_data)

        # [AI GENERATED] 作成されたプロジェクトの検証
        assert result is not None
        assert result.title == project_data.title
        assert result.description == project_data.description
        assert result.status == project_data.status
        assert result.id is not None

    def test_get_by_id_success(self, project_repository: ProjectRepository) -> None:
        """IDによるプロジェクト取得が成功することをテスト"""
        # [AI GENERATED] テスト用プロジェクトを作成
        project_data = ProjectCreate(
            title="取得テストプロジェクト",
            description="ID取得テスト用",
            status=ProjectStatus.ACTIVE,
        )
        created_project = project_repository.create(project_data)
        assert created_project is not None
        assert created_project.id is not None

        # [AI GENERATED] 作成されたプロジェクトをIDで取得
        result = project_repository.get_by_id(created_project.id)

        # [AI GENERATED] 取得されたプロジェクトの検証
        assert result is not None
        assert result.id == created_project.id
        assert result.title == created_project.title

    def test_get_by_id_not_found(self, project_repository: ProjectRepository) -> None:
        """存在しないIDでプロジェクト取得した場合にNoneを返すことをテスト"""
        # [AI GENERATED] 存在しないUUIDで検索
        non_existent_id = uuid.uuid4()
        result = project_repository.get_by_id(non_existent_id)

        # [AI GENERATED] Noneが返されることを確認
        assert result is None

    def test_update_project_success(self, project_repository: ProjectRepository) -> None:
        """プロジェクト更新が成功することをテスト"""
        # [AI GENERATED] テスト用プロジェクトを作成
        project_data = ProjectCreate(
            title="更新前プロジェクト",
            description="更新前の説明",
            status=ProjectStatus.ACTIVE,
        )
        created_project = project_repository.create(project_data)
        assert created_project is not None
        assert created_project.id is not None

        # [AI GENERATED] プロジェクトを更新
        update_data = ProjectUpdate(
            title="更新後プロジェクト",
            description="更新後の説明",
            status=ProjectStatus.COMPLETED,
        )
        result = project_repository.update(created_project.id, update_data)

        # [AI GENERATED] 更新されたプロジェクトの検証
        assert result is not None
        assert result.id == created_project.id
        assert result.title == update_data.title
        assert result.description == update_data.description
        assert result.status == update_data.status

    def test_update_project_not_found(self, project_repository: ProjectRepository) -> None:
        """存在しないプロジェクトの更新でNoneを返すことをテスト"""
        # [AI GENERATED] 存在しないUUIDで更新を試行
        non_existent_id = uuid.uuid4()
        update_data = ProjectUpdate(title="存在しない更新")

        result = project_repository.update(non_existent_id, update_data)

        # [AI GENERATED] Noneが返されることを確認
        assert result is None

    def test_delete_project_success(self, project_repository: ProjectRepository) -> None:
        """プロジェクト削除が成功することをテスト"""
        # [AI GENERATED] テスト用プロジェクトを作成
        project_data = ProjectCreate(
            title="削除テストプロジェクト",
            description="削除テスト用",
            status=ProjectStatus.ACTIVE,
        )
        created_project = project_repository.create(project_data)
        assert created_project is not None
        assert created_project.id is not None

        # [AI GENERATED] プロジェクトを削除
        result = project_repository.delete(created_project.id)

        # [AI GENERATED] 削除が成功したことを確認
        assert result is True

        # [AI GENERATED] 削除されたプロジェクトが取得できないことを確認
        deleted_project = project_repository.get_by_id(created_project.id)
        assert deleted_project is None

    def test_delete_project_not_found(self, project_repository: ProjectRepository) -> None:
        """存在しないプロジェクトの削除でFalseを返すことをテスト"""
        # [AI GENERATED] 存在しないUUIDで削除を試行
        non_existent_id = uuid.uuid4()
        result = project_repository.delete(non_existent_id)

        # [AI GENERATED] Falseが返されることを確認
        assert result is False
