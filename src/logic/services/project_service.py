"""プロジェクトサービスの実装

このモジュールは、プロジェクトに関するビジネスロジックを提供します。
リポジトリ層を使用してデータアクセスを行い、複雑なプロジェクト操作を実装します。
"""

import uuid

from loguru import logger

from logic.repositories.project import ProjectRepository
from logic.repositories.task import TaskRepository
from logic.services.base import MyBaseError, ServiceBase
from models import ProjectCreate, ProjectRead, ProjectStatus, ProjectUpdate, TaskRead


# Custom exceptions for project service errors
class ProjectServiceCreateError(MyBaseError):
    """プロジェクト作成時のカスタム例外クラス

    Args:
        arg (str): エラーメッセージ
    """

    def __str__(self) -> str:
        return f"プロジェクト作成エラー: {self.arg}"


class ProjectServiceCheckError(MyBaseError):
    """プロジェクト存在確認時のカスタム例外クラス

    Args:
        arg (str): エラーメッセージ
    """

    def __str__(self) -> str:
        return f"プロジェクト存在確認エラー: {self.arg}"


class ProjectServiceUpdateError(MyBaseError):
    """プロジェクト更新時のカスタム例外クラス

    Args:
        arg (str): エラーメッセージ
    """

    def __str__(self) -> str:
        return f"プロジェクト更新エラー: {self.arg}"


class ProjectServiceDeleteError(MyBaseError):
    """プロジェクト削除時のカスタム例外クラス

    Args:
        arg (str): エラーメッセージ
    """

    def __str__(self) -> str:
        return f"プロジェクト削除エラー: {self.arg}"


class ProjectServiceGetError(MyBaseError):
    """プロジェクト取得時のカスタム例外クラス

    Args:
        arg (str): エラーメッセージ
    """

    def __str__(self) -> str:
        return f"プロジェクト取得エラー: {self.arg}"


type ProjectServiceError = (
    ProjectServiceGetError
    | ProjectServiceCreateError
    | ProjectServiceCheckError
    | ProjectServiceUpdateError
    | ProjectServiceDeleteError
)


class ProjectService(ServiceBase[ProjectServiceError]):
    """プロジェクトサービス

    プロジェクトに関するビジネスロジックを提供するサービスクラス。
    複数のリポジトリを組み合わせて、複雑なプロジェクト操作を実装します。
    """

    def __init__(self, project_repo: ProjectRepository, task_repo: TaskRepository) -> None:
        """ProjectServiceを初期化する

        Args:
            project_repo: プロジェクトリポジトリ
            task_repo: タスクリポジトリ
        """
        self.project_repo = project_repo
        self.task_repo = task_repo

    # プロジェクトの存在を確認を確認するメソッド
    def _check_project_exists(self, project_id: uuid.UUID) -> ProjectRead:
        """プロジェクトの存在を確認する

        Args:
            project_id: プロジェクトのID

        Returns:
            ProjectRead: 存在するプロジェクト

        Raises:
            ProjectServiceCheckError: プロジェクトが存在しない場合
            ValidationError: プロジェクトデータの検証に失敗した場合
        """
        project = self.project_repo.get_by_id(project_id)
        if not project:
            self._log_error_and_raise(f"プロジェクトID {project_id} が見つかりません", ProjectServiceCheckError)
        return ProjectRead.model_validate(project)

    def create_project(self, project_data: ProjectCreate) -> ProjectRead:
        """新しいプロジェクトを作成する

        Args:
            project_data: 作成するプロジェクトのデータ

        Returns:
            ProjectRead: 作成されたプロジェクト

        Raises:
            ProjectServiceCreateError: プロジェクト作成に失敗した場合
            ValidationError: プロジェクトデータの検証に失敗した場合
        """
        project = self.project_repo.create(project_data)
        if not project:
            self._log_error_and_raise("プロジェクトの作成に失敗しました", ProjectServiceCreateError)

        logger.info(f"プロジェクト '{project.title}' を作成しました (ID: {project.id})")
        return ProjectRead.model_validate(project)

    def update_project(self, project_id: uuid.UUID, project_data: ProjectUpdate) -> ProjectRead:
        """プロジェクトを更新する

        Args:
            project_id: 更新するプロジェクトのID
            project_data: 更新するプロジェクトのデータ

        Returns:
            ProjectRead: 更新されたプロジェクト

        Raises:
            ProjectServiceCheckError: プロジェクトが存在しない場合
            ProjectServiceUpdateError: プロジェクト更新に失敗した場合
            ValidationError: プロジェクトデータの検証に失敗した場合
        """
        # プロジェクトの存在を確認
        self._check_project_exists(project_id)

        updated_project = self.project_repo.update(project_id, project_data)
        if not updated_project:
            self._log_error_and_raise(f"プロジェクトの更新に失敗しました (ID: {project_id})", ProjectServiceUpdateError)

        logger.info(f"プロジェクト '{updated_project.title}' を更新しました (ID: {project_id})")
        return ProjectRead.model_validate(updated_project)

    def delete_project(self, project_id: uuid.UUID, *, force: bool = False) -> bool:
        """プロジェクトを削除する

        Args:
            project_id: 削除するプロジェクトのID
            force: 関連タスクがある場合も強制削除するかどうか(default: False)

        Returns:
            bool: 削除が成功した場合True

        Raises:
            ProjectServiceCheckError: プロジェクトが存在しない場合
            ProjectServiceDeleteError: タスクが関連している場合、または削除に失敗した場合
        """
        # プロジェクトの存在を確認
        existing_project = self._check_project_exists(project_id)

        # 関連するタスクがあるかチェック
        related_tasks = self.task_repo.get_by_project_id(project_id)
        if related_tasks and not force:
            self._log_error_and_raise(
                f"プロジェクト '{existing_project.title}' には {len(related_tasks)} 個のタスクが関連しています。force=Trueで強制削除できます",  # noqa: E501
                ProjectServiceDeleteError,
            )

        # 強制削除の場合、関連タスクのproject_idをNoneに更新
        if force and related_tasks:
            from models.task import TaskUpdate

            for task in related_tasks:
                if task.id is not None:  # IDがNoneでないことを確認
                    task_update = TaskUpdate(project_id=None)
                    self.task_repo.update(task.id, task_update)
            logger.info(f"{len(related_tasks)} 個のタスクからプロジェクト関連を削除しました")

        success = self.project_repo.delete(project_id)
        if not success:
            self._log_error_and_raise(f"プロジェクトの削除に失敗しました (ID: {project_id})", ProjectServiceDeleteError)

        logger.info(f"プロジェクト '{existing_project.title}' を削除しました (ID: {project_id})")
        return success

    def get_project_by_id(self, project_id: uuid.UUID) -> ProjectRead | None:
        """IDでプロジェクトを取得する

        Args:
            project_id: プロジェクトのID

        Returns:
            ProjectRead | None: 見つかったプロジェクト、存在しない場合はNone

        Raises:
            ProjectServiceGetError: プロジェクト取得に失敗した場合
            ValidationError: プロジェクトデータの検証に失敗した場合
        """
        try:
            project = self.project_repo.get_by_id(project_id)
            if not project:
                self._log_error_and_raise(f"プロジェクトID {project_id} が見つかりません", ProjectServiceGetError)
            return ProjectRead.model_validate(project)
        except Exception:
            self._log_error_and_raise(f"プロジェクトの取得に失敗しました (ID: {project_id})", ProjectServiceGetError)

    def get_all_projects(self) -> list[ProjectRead]:
        """全てのプロジェクトを取得する

        Returns:
            list[ProjectRead]: 全てのプロジェクトのリスト

        Raises:
            ProjectServiceGetError: プロジェクト一覧の取得に失敗した場合
            ValidationError: プロジェクトデータの検証に失敗した場合
        """
        try:
            projects = self.project_repo.get_all()
            return [ProjectRead.model_validate(project) for project in projects]
        except Exception:
            self._log_error_and_raise("プロジェクト一覧の取得に失敗しました", ProjectServiceGetError)

    def get_projects_by_status(self, status: ProjectStatus) -> list[ProjectRead]:
        """指定されたステータスのプロジェクトを取得する

        Args:
            status: プロジェクトステータス

        Returns:
            list[ProjectRead]: 指定されたステータスのプロジェクトのリスト

        Raises:
            ProjectServiceGetError: ステータス別プロジェクトの取得に失敗した場合
            ValidationError: プロジェクトデータの検証に失敗した場合
        """
        try:
            projects = self.project_repo.get_by_status(status)
            return [ProjectRead.model_validate(project) for project in projects]
        except Exception:
            self._log_error_and_raise(f"ステータス '{status}' のプロジェクト取得に失敗しました", ProjectServiceGetError)

    def get_active_projects(self) -> list[ProjectRead]:
        """アクティブなプロジェクトを取得する

        Returns:
            list[ProjectRead]: アクティブなプロジェクトのリスト

        Raises:
            ProjectServiceGetError: アクティブプロジェクトの取得に失敗した場合
            ValidationError: プロジェクトデータの検証に失敗した場合
        """
        try:
            projects = self.project_repo.get_active_projects()
            return [ProjectRead.model_validate(project) for project in projects]
        except Exception:
            self._log_error_and_raise("アクティブプロジェクトの取得に失敗しました", ProjectServiceGetError)

    def get_completed_projects(self) -> list[ProjectRead]:
        """完了済みプロジェクトを取得する

        Returns:
            list[ProjectRead]: 完了済みプロジェクトのリスト

        Raises:
            ProjectServiceGetError: 完了済みプロジェクトの取得に失敗した場合
            ValidationError: プロジェクトデータの検証に失敗した場合
        """
        try:
            projects = self.project_repo.get_completed_projects()
            return [ProjectRead.model_validate(project) for project in projects]
        except Exception:
            self._log_error_and_raise("完了済みプロジェクトの取得に失敗しました", ProjectServiceGetError)

    def search_projects(self, query: str) -> list[ProjectRead]:
        """プロジェクトをタイトルで検索する

        Args:
            query: 検索クエリ

        Returns:
            list[ProjectRead]: 検索条件に一致するプロジェクトのリスト

        Raises:
            ProjectServiceGetError: プロジェクトの検索に失敗した場合
            ValidationError: プロジェクトデータの検証に失敗した場合
        """
        try:
            projects = self.project_repo.search_by_title(query)
            return [ProjectRead.model_validate(project) for project in projects]
        except Exception:
            self._log_error_and_raise("プロジェクトの検索に失敗しました", ProjectServiceGetError)

    def get_project_tasks(self, project_id: uuid.UUID) -> list[TaskRead]:
        """プロジェクトに関連するタスクを取得する

        Args:
            project_id: プロジェクトID

        Returns:
            list[TaskRead]: プロジェクトに関連するタスクのリスト

        Raises:
            ProjectServiceCheckError: プロジェクトが存在しない場合
            ProjectServiceGetError: タスク取得に失敗した場合
        """
        # プロジェクトの存在を確認
        self._check_project_exists(project_id)

        try:
            tasks = self.task_repo.get_by_project_id(project_id)
            return [TaskRead.model_validate(task) for task in tasks]
        except Exception:
            self._log_error_and_raise("タスク取得に失敗しました", ProjectServiceGetError)

    def complete_project(self, project_id: uuid.UUID) -> ProjectRead:
        """プロジェクトを完了する

        Args:
            project_id: プロジェクトID

        Returns:
            ProjectRead: 更新されたプロジェクト

        Raises:
            ProjectServiceCheckError: プロジェクトが存在しない場合
            ProjectServiceUpdateError: プロジェクト更新に失敗した場合
            ValidationError: プロジェクトデータの検証に失敗した場合
        """
        project_data = ProjectUpdate(status=ProjectStatus.COMPLETED)
        return self.update_project(project_id, project_data)

    def activate_project(self, project_id: uuid.UUID) -> ProjectRead:
        """プロジェクトをアクティブにする

        Args:
            project_id: プロジェクトID

        Returns:
            ProjectRead: 更新されたプロジェクト

        Raises:
            ProjectServiceCheckError: プロジェクトが存在しない場合
            ProjectServiceUpdateError: プロジェクト更新に失敗した場合
            ValidationError: プロジェクトデータの検証に失敗した場合
        """
        project_data = ProjectUpdate(status=ProjectStatus.ACTIVE)
        return self.update_project(project_id, project_data)

    def put_project_on_hold(self, project_id: uuid.UUID) -> ProjectRead:
        """プロジェクトを保留にする

        Args:
            project_id: プロジェクトID

        Returns:
            ProjectRead: 更新されたプロジェクト

        Raises:
            ProjectServiceCheckError: プロジェクトが存在しない場合
            ProjectServiceUpdateError: プロジェクト更新に失敗した場合
            ValidationError: プロジェクトデータの検証に失敗した場合
        """
        project_data = ProjectUpdate(status=ProjectStatus.ON_HOLD)
        return self.update_project(project_id, project_data)

    def cancel_project(self, project_id: uuid.UUID) -> ProjectRead:
        """プロジェクトをキャンセルする

        Args:
            project_id: プロジェクトID

        Returns:
            ProjectRead: 更新されたプロジェクト

        Raises:
            ProjectServiceCheckError: プロジェクトが存在しない場合
            ProjectServiceUpdateError: プロジェクト更新に失敗した場合
            ValidationError: プロジェクトデータの検証に失敗した場合
        """
        project_data = ProjectUpdate(status=ProjectStatus.CANCELLED)
        return self.update_project(project_id, project_data)
