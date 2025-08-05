"""ProjectServiceのテストケース

このモジュールは、ProjectServiceクラスのプロジェクト関連のビジネスロジックを
テストするためのテストケースを提供します。

テスト対象：
- create_project: プロジェクト作成
- update_project: プロジェクト更新
- delete_project: プロジェクト削除（関連タスクチェック含む）
- get_project: プロジェクト取得
- get_all_projects: 全プロジェクト取得
- get_projects_by_status: ステータス別プロジェクト取得
"""

import uuid
from unittest.mock import Mock

import pytest

from logic.repositories.project import ProjectRepository
from logic.repositories.task import TaskRepository
from logic.services.project_service import (
    ProjectService,
    ProjectServiceCheckError,
    ProjectServiceCreateError,
    ProjectServiceDeleteError,
    ProjectServiceUpdateError,
)
from models import Project, ProjectCreate, ProjectRead, ProjectStatus, ProjectUpdate, Task, TaskStatus


class TestProjectServiceCreate:
    """create_projectメソッドのテストクラス"""

    def test_create_project_success(self) -> None:
        """プロジェクト作成が成功することをテスト"""
        # [AI GENERATED] モックを作成
        project_repo = Mock(spec=ProjectRepository)
        task_repo = Mock(spec=TaskRepository)
        service = ProjectService(project_repo, task_repo)

        # [AI GENERATED] 作成するプロジェクトデータ
        project_data = ProjectCreate(
            title="新しいプロジェクト",
            description="テスト用プロジェクト",
            status=ProjectStatus.ACTIVE,
        )

        # [AI GENERATED] モックの戻り値を設定
        created_project = Project(
            id=uuid.uuid4(),
            title=project_data.title,
            description=project_data.description,
            status=project_data.status,
        )
        project_repo.create.return_value = created_project

        # [AI GENERATED] プロジェクトを作成
        result = service.create_project(project_data)

        # [AI GENERATED] 結果の検証
        assert isinstance(result, ProjectRead)
        assert result.title == project_data.title
        assert result.description == project_data.description
        assert result.status == project_data.status
        assert result.id == created_project.id

        # [AI GENERATED] モックの呼び出しを確認
        project_repo.create.assert_called_once_with(project_data)

    def test_create_project_failure(self) -> None:
        """プロジェクト作成が失敗することをテスト"""
        # [AI GENERATED] モックを作成
        project_repo = Mock(spec=ProjectRepository)
        task_repo = Mock(spec=TaskRepository)
        service = ProjectService(project_repo, task_repo)

        # [AI GENERATED] 作成するプロジェクトデータ
        project_data = ProjectCreate(
            title="失敗プロジェクト",
            description="テスト用プロジェクト",
            status=ProjectStatus.ACTIVE,
        )

        # [AI GENERATED] リポジトリの作成が失敗する設定
        project_repo.create.return_value = None

        # [AI GENERATED] 例外が発生することを確認
        with pytest.raises(ProjectServiceCreateError):
            service.create_project(project_data)


class TestProjectServiceUpdate:
    """update_projectメソッドのテストクラス"""

    def test_update_project_success(self) -> None:
        """プロジェクト更新が成功することをテスト"""
        # [AI GENERATED] モックを作成
        project_repo = Mock(spec=ProjectRepository)
        task_repo = Mock(spec=TaskRepository)
        service = ProjectService(project_repo, task_repo)

        # [AI GENERATED] 更新対象のプロジェクト
        project_id = uuid.uuid4()
        existing_project = Project(
            id=project_id,
            title="更新前プロジェクト",
            description="更新前の説明",
            status=ProjectStatus.ACTIVE,
        )

        # [AI GENERATED] 更新データ
        update_data = ProjectUpdate(
            title="更新後プロジェクト",
            description="更新後の説明",
            status=ProjectStatus.COMPLETED,
        )

        # [AI GENERATED] 更新後のプロジェクト
        updated_project = Project(
            id=project_id,
            title=update_data.title or "デフォルトタイトル",
            description=update_data.description or "デフォルト説明",
            status=update_data.status or ProjectStatus.ACTIVE,
        )

        # [AI GENERATED] モックの戻り値を設定
        project_repo.get_by_id.return_value = existing_project
        project_repo.update.return_value = updated_project

        # [AI GENERATED] プロジェクトを更新
        result = service.update_project(project_id, update_data)

        # [AI GENERATED] 結果の検証
        assert isinstance(result, ProjectRead)
        assert result.id == project_id
        assert result.title == (update_data.title or "デフォルトタイトル")
        assert result.description == (update_data.description or "デフォルト説明")
        assert result.status == (update_data.status or ProjectStatus.ACTIVE)

        # [AI GENERATED] モックの呼び出しを確認
        project_repo.get_by_id.assert_called_once_with(project_id)
        project_repo.update.assert_called_once_with(project_id, update_data)

    def test_update_project_not_found(self) -> None:
        """存在しないプロジェクトの更新でエラーが発生することをテスト"""
        # [AI GENERATED] モックを作成
        project_repo = Mock(spec=ProjectRepository)
        task_repo = Mock(spec=TaskRepository)
        service = ProjectService(project_repo, task_repo)

        # [AI GENERATED] 存在しないプロジェクトID
        project_id = uuid.uuid4()
        update_data = ProjectUpdate(title="更新データ")

        # [AI GENERATED] プロジェクトが見つからない設定
        project_repo.get_by_id.return_value = None

        # [AI GENERATED] 例外が発生することを確認
        with pytest.raises(ProjectServiceCheckError):
            service.update_project(project_id, update_data)

    def test_update_project_failure(self) -> None:
        """プロジェクト更新が失敗することをテスト"""
        # [AI GENERATED] モックを作成
        project_repo = Mock(spec=ProjectRepository)
        task_repo = Mock(spec=TaskRepository)
        service = ProjectService(project_repo, task_repo)

        # [AI GENERATED] 更新対象のプロジェクト
        project_id = uuid.uuid4()
        existing_project = Project(
            id=project_id,
            title="更新前プロジェクト",
            description="更新前の説明",
            status=ProjectStatus.ACTIVE,
        )

        update_data = ProjectUpdate(title="更新データ")

        # [AI GENERATED] モックの戻り値を設定
        project_repo.get_by_id.return_value = existing_project
        project_repo.update.return_value = None  # 更新失敗

        # [AI GENERATED] 例外が発生することを確認
        with pytest.raises(ProjectServiceUpdateError):
            service.update_project(project_id, update_data)


class TestProjectServiceDelete:
    """delete_projectメソッドのテストクラス"""

    def test_delete_project_success_no_related_tasks(self) -> None:
        """関連タスクがないプロジェクトの削除が成功することをテスト"""
        # [AI GENERATED] モックを作成
        project_repo = Mock(spec=ProjectRepository)
        task_repo = Mock(spec=TaskRepository)
        service = ProjectService(project_repo, task_repo)

        # [AI GENERATED] 削除対象のプロジェクト
        project_id = uuid.uuid4()
        existing_project = Project(
            id=project_id,
            title="削除対象プロジェクト",
            description="削除テスト用",
            status=ProjectStatus.ACTIVE,
        )

        # [AI GENERATED] モックの戻り値を設定
        project_repo.get_by_id.return_value = existing_project
        task_repo.get_by_project_id.return_value = []  # 関連タスクなし
        project_repo.delete.return_value = True

        # [AI GENERATED] プロジェクトを削除
        result = service.delete_project(project_id)

        # [AI GENERATED] 削除が成功したことを確認
        assert result is True

        # [AI GENERATED] モックの呼び出しを確認
        project_repo.get_by_id.assert_called_once_with(project_id)
        task_repo.get_by_project_id.assert_called_once_with(project_id)
        project_repo.delete.assert_called_once_with(project_id)

    def test_delete_project_with_related_tasks_without_force(self) -> None:
        """関連タスクがあるプロジェクトの削除でエラーが発生することをテスト"""
        # [AI GENERATED] モックを作成
        project_repo = Mock(spec=ProjectRepository)
        task_repo = Mock(spec=TaskRepository)
        service = ProjectService(project_repo, task_repo)

        # [AI GENERATED] 削除対象のプロジェクト
        project_id = uuid.uuid4()
        existing_project = Project(
            id=project_id,
            title="関連タスクありプロジェクト",
            description="削除テスト用",
            status=ProjectStatus.ACTIVE,
        )

        # [AI GENERATED] 関連タスクを作成
        related_tasks = [
            Task(
                id=uuid.uuid4(),
                title="関連タスク1",
                description="",
                status=TaskStatus.INBOX,
                project_id=project_id,
            )
        ]

        # [AI GENERATED] モックの戻り値を設定
        project_repo.get_by_id.return_value = existing_project
        task_repo.get_by_project_id.return_value = related_tasks

        # [AI GENERATED] 例外が発生することを確認
        with pytest.raises(ProjectServiceDeleteError):
            service.delete_project(project_id, force=False)

        # [AI GENERATED] 削除が呼ばれていないことを確認
        project_repo.delete.assert_not_called()

    def test_delete_project_with_related_tasks_with_force(self) -> None:
        """関連タスクがあるプロジェクトの強制削除が成功することをテスト"""
        # [AI GENERATED] モックを作成
        project_repo = Mock(spec=ProjectRepository)
        task_repo = Mock(spec=TaskRepository)
        service = ProjectService(project_repo, task_repo)

        # [AI GENERATED] 削除対象のプロジェクト
        project_id = uuid.uuid4()
        existing_project = Project(
            id=project_id,
            title="強制削除プロジェクト",
            description="削除テスト用",
            status=ProjectStatus.ACTIVE,
        )

        # [AI GENERATED] 関連タスクを作成
        task_id = uuid.uuid4()
        related_tasks = [
            Task(
                id=task_id,
                title="関連タスク1",
                description="",
                status=TaskStatus.INBOX,
                project_id=project_id,
            )
        ]

        # [AI GENERATED] モックの戻り値を設定
        project_repo.get_by_id.return_value = existing_project
        task_repo.get_by_project_id.return_value = related_tasks
        task_repo.update.return_value = Task(
            id=task_id,
            title="関連タスク1",
            description="",
            status=TaskStatus.INBOX,
            project_id=None,  # プロジェクト関連を削除
        )
        project_repo.delete.return_value = True

        # [AI GENERATED] プロジェクトを強制削除
        result = service.delete_project(project_id, force=True)

        # [AI GENERATED] 削除が成功したことを確認
        assert result is True

        # [AI GENERATED] 関連タスクの更新が呼ばれたことを確認
        task_repo.update.assert_called_once()
        project_repo.delete.assert_called_once_with(project_id)

    def test_delete_project_not_found(self) -> None:
        """存在しないプロジェクトの削除でエラーが発生することをテスト"""
        # [AI GENERATED] モックを作成
        project_repo = Mock(spec=ProjectRepository)
        task_repo = Mock(spec=TaskRepository)
        service = ProjectService(project_repo, task_repo)

        # [AI GENERATED] 存在しないプロジェクトID
        project_id = uuid.uuid4()

        # [AI GENERATED] プロジェクトが見つからない設定
        project_repo.get_by_id.return_value = None

        # [AI GENERATED] 例外が発生することを確認
        with pytest.raises(ProjectServiceCheckError):
            service.delete_project(project_id)

    def test_delete_project_failure(self) -> None:
        """プロジェクト削除が失敗することをテスト"""
        # [AI GENERATED] モックを作成
        project_repo = Mock(spec=ProjectRepository)
        task_repo = Mock(spec=TaskRepository)
        service = ProjectService(project_repo, task_repo)

        # [AI GENERATED] 削除対象のプロジェクト
        project_id = uuid.uuid4()
        existing_project = Project(
            id=project_id,
            title="削除失敗プロジェクト",
            description="削除テスト用",
            status=ProjectStatus.ACTIVE,
        )

        # [AI GENERATED] モックの戻り値を設定
        project_repo.get_by_id.return_value = existing_project
        task_repo.get_by_project_id.return_value = []
        project_repo.delete.return_value = False  # 削除失敗

        # [AI GENERATED] 例外が発生することを確認
        with pytest.raises(ProjectServiceDeleteError):
            service.delete_project(project_id)

        # [AI GENERATED] 例外が発生することを確認
        with pytest.raises(ProjectServiceDeleteError):
            service.delete_project(project_id)
