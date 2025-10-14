"""プロジェクトサービスの実装

このモジュールは、プロジェクトに関するビジネスロジックを提供します。
リポジトリ層を使用してデータアクセスを行い、複雑なプロジェクト操作を実装します。
"""

import uuid

from loguru import logger

from logic.repositories import ProjectRepository, RepositoryFactory
from logic.services.base import MyBaseError, ServiceBase, convert_read_model, handle_service_errors
from models import Project, ProjectCreate, ProjectRead, ProjectStatus, ProjectUpdate

SERVICE_NAME = "プロジェクトサービス"


class ProjectServiceError(MyBaseError):
    """プロジェクトサービス層で発生する汎用的なエラー"""

    def __init__(self, message: str, operation: str = "不明な操作") -> None:
        super().__init__(f"プロジェクトの{operation}処理でエラーが発生しました: {message}")
        self.operation = operation


class ProjectService(ServiceBase):
    """プロジェクトサービス

    プロジェクトに関するビジネスロジックを提供するサービスクラス。
    複数のリポジトリを組み合わせて、複雑なプロジェクト操作を実装します。
    """

    def __init__(self, project_repo: ProjectRepository) -> None:
        """ProjectServiceを初期化する

        Args:
            project_repo: プロジェクトリポジトリ
        """
        self.project_repo = project_repo

    @classmethod
    def build_service(cls, repo_factory: RepositoryFactory) -> "ProjectService":
        """ProjectServiceのインスタンスを生成するファクトリメソッド

        Returns:
            ProjectService: プロジェクトサービスのインスタンス
        """
        return cls(project_repo=repo_factory.create(ProjectRepository))

    @handle_service_errors(SERVICE_NAME, "作成", ProjectServiceError)
    @convert_read_model(ProjectRead)
    def create(self, project_data: ProjectCreate) -> Project:
        """新しいプロジェクトを作成する

        Args:
            project_data: 作成するプロジェクトのデータ

        Returns:
            ProjectRead: 作成されたプロジェクト

        Raises:
            NotFoundError: エンティティが存在しない場合
            ProjectServiceError: プロジェクト作成に失敗した場合
        """
        project = self.project_repo.create(project_data)
        logger.debug(f"プロジェクト '{project.title}' を作成しました (ID: {project.id})")

        return project

    @handle_service_errors(SERVICE_NAME, "更新", ProjectServiceError)
    @convert_read_model(ProjectRead)
    def update(self, project_id: uuid.UUID, project_data: ProjectUpdate) -> Project:
        """プロジェクトを更新する

        Args:
            project_id: 更新するプロジェクトのID
            project_data: 更新するプロジェクトのデータ

        Returns:
            ProjectRead: 更新されたプロジェクト

        Raises:
            NotFoundError: プロジェクトが存在しない場合
            ProjectServiceError: プロジェクト更新に失敗した場合
        """
        updated_project = self.project_repo.update(project_id, project_data)
        logger.debug(f"プロジェクト '{updated_project.title}' を更新しました (ID: {project_id})")

        return updated_project

    @handle_service_errors(SERVICE_NAME, "削除", ProjectServiceError)
    def delete(self, project_id: uuid.UUID, *, force: bool = False) -> bool:
        """プロジェクトを削除する

        Args:
            project_id: 削除するプロジェクトのID
            force: 関連タスクがある場合も強制削除するかどうか(default: False)

        Returns:
            bool: 削除が成功した場合True

        Raises:
            NotFoundError: プロジェクトが存在しない場合
            ProjectServiceError: タスクが関連している場合、または削除に失敗した場合
        """
        # プロジェクトの存在を確認し、関連タスクを取得
        existing_project = self.project_repo.get_by_id(project_id)

        if not force:
            # 強制削除でない場合は関連タスクを外してから削除
            self.project_repo.remove_all_tasks(project_id)
            self.project_repo.delete(project_id)
            success = True
        else:
            self.project_repo.delete(project_id)
            success = True

        logger.info(f"プロジェクト '{existing_project.title}' を削除しました (ID: {project_id})")
        return success

    @handle_service_errors(SERVICE_NAME, "タスク削除", ProjectServiceError)
    @convert_read_model(ProjectRead)
    def remove_task(self, project_id: uuid.UUID, task_id: str) -> Project:
        """プロジェクトからタスクを削除する

        Args:
            project_id: プロジェクトのID
            task_id: 削除するタスクのID

        Returns:
            ProjectRead: 更新されたプロジェクト

        Raises:
            NotFoundError: エンティティが存在しない場合
        """
        project = self.project_repo.get_by_id(project_id, with_details=True)

        for task in project.tasks:
            if task.id == task_id:
                updated_project = self.project_repo.remove_task(project_id, task_id)
                logger.debug(f"プロジェクト({project_id})からタスク({task_id})を削除しました。")
                break
        else:
            msg = f"プロジェクト({project_id})にタスク({task_id})は存在しません。"
            logger.warning(msg)
            raise ValueError(msg)

        return updated_project

    @handle_service_errors(SERVICE_NAME, "取得", ProjectServiceError)
    @convert_read_model(ProjectRead)
    def get_by_id(self, project_id: uuid.UUID) -> Project:
        """IDでプロジェクトを取得する

        Args:
            project_id: プロジェクトのID

        Returns:
            ProjectRead: 見つかったプロジェクト、存在しない場合はNone

        Raises:
            NotFoundError: プロジェクトが存在しない場合
            ProjectServiceError: プロジェクトの取得に失敗した場合
        """
        project = self.project_repo.get_by_id(project_id)
        logger.debug(f"プロジェクトを取得しました: {project.id}")
        return project

    @handle_service_errors(SERVICE_NAME, "取得", ProjectServiceError)
    @convert_read_model(ProjectRead, is_list=True)
    def get_all(self) -> list[Project]:
        """全てのプロジェクトを取得する

        Returns:
            list[ProjectRead]: 全てのプロジェクトのリスト

        Raises:
            NotFoundError: エンティティが存在しない場合
            ProjectServiceError: 全プロジェクトの取得に失敗した場合
        """
        projects = self.project_repo.get_all()
        logger.debug(f"全てのプロジェクトを取得しました: {len(projects)} 件")
        return projects

    @handle_service_errors(SERVICE_NAME, "取得", ProjectServiceError)
    @convert_read_model(ProjectRead, is_list=True)
    def list_by_status(self, status: ProjectStatus) -> list[Project]:
        """指定されたステータスのプロジェクトを取得する

        Args:
            status: プロジェクトステータス

        Returns:
            list[ProjectRead]: 指定されたステータスのプロジェクトのリスト

        Raises:
            NotFoundError: エンティティが存在しない場合
            ProjectServiceError: プロジェクトの取得に失敗した場合
        """
        projects = self.project_repo.list_by_status(status)
        logger.debug(f"ステータス '{status}' のプロジェクトを {len(projects)} 件取得しました。")
        return projects
