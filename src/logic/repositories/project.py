"""プロジェクトリポジトリの実装"""

from loguru import logger
from sqlmodel import Session, select

from logic.repositories.base import BaseRepository
from models import Project, ProjectCreate, ProjectStatus, ProjectUpdate


class ProjectRepository(BaseRepository[Project, ProjectCreate, ProjectUpdate]):
    """プロジェクトリポジトリ

    プロジェクトの CRUD 操作を提供するリポジトリクラス。
    BaseRepository を継承して基本操作を提供し、プロジェクト固有の操作を追加実装。
    """

    def __init__(self, session: Session) -> None:
        """ProjectRepository を初期化する

        Args:
            session: データベースセッション
        """
        super().__init__(Project, session)

    def get_all(self) -> list[Project]:
        """全てのプロジェクト一覧を取得する

        Returns:
            list[Project]: 全てのプロジェクト一覧
        """
        try:
            statement = select(Project)
            results = self.session.exec(statement).all()
        except Exception as e:
            logger.exception(f"プロジェクト取得に失敗しました: {e}")
            raise
        return list(results)

    def get_by_status(self, status: ProjectStatus) -> list[Project]:
        """指定されたステータスのプロジェクト一覧を取得する

        Args:
            status: プロジェクトステータス

        Returns:
            list[Project]: 指定された条件に一致するプロジェクト一覧
        """
        try:
            statement = select(Project).where(Project.status == status)
            results = self.session.exec(statement).all()
        except Exception as e:
            logger.exception(f"ステータス別プロジェクト取得に失敗しました: {e}")
            raise
        return list(results)

    def search_by_title(self, title_query: str) -> list[Project]:
        """タイトルでプロジェクトを検索する

        Args:
            title_query: 検索クエリ（部分一致）

        Returns:
            list[Project]: 検索条件に一致するプロジェクト一覧
        """
        try:
            # Python側でフィルタリングを実行
            statement = select(Project)
            all_projects = self.session.exec(statement).all()

            # タイトルに検索クエリが含まれるプロジェクトをフィルタリング
            filtered_projects = [project for project in all_projects if title_query.lower() in project.title.lower()]

        except Exception as e:
            logger.exception(f"タイトル検索に失敗しました: {e}")
            raise
        return filtered_projects

    def get_active_projects(self) -> list[Project]:
        """アクティブなプロジェクト一覧を取得する

        Returns:
            list[Project]: アクティブなプロジェクト一覧
        """
        return self.get_by_status(ProjectStatus.ACTIVE)

    def get_completed_projects(self) -> list[Project]:
        """完了済みプロジェクト一覧を取得する

        Returns:
            list[Project]: 完了済みプロジェクト一覧
        """
        return self.get_by_status(ProjectStatus.COMPLETED)
