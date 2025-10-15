"""タグサービスの実装

このモジュールは、タグに関するビジネスロジックを提供します。
リポジトリ層を使用してデータアクセスを行い、複雑なタグ操作を実装します。
"""

import uuid

from loguru import logger

from logic.repositories import RepositoryFactory, TagRepository
from logic.services.base import MyBaseError, ServiceBase, convert_read_model, handle_service_errors
from models import Tag, TagCreate, TagRead, TagUpdate

SERVICE_NAME = "タグサービス"


class TagServiceError(MyBaseError):
    """タグサービス層で発生する汎用的なエラー"""

    def __init__(self, message: str, operation: str = "不明な操作") -> None:  # [AI GENERATED]
        super().__init__(f"タグの{operation}処理でエラーが発生しました: {message}")
        self.operation = operation


class TagService(ServiceBase):
    """タグサービス

    タグに関するビジネスロジックを提供するサービスクラス。
    複数のリポジトリを組み合わせて、複雑なタグ操作を実装します。
    """

    def __init__(self, tag_repo: TagRepository) -> None:
        """タグサービスの初期化

        Args:
            tag_repo: タグリポジトリ
        """
        self.tag_repo = tag_repo

    @classmethod
    def build_service(cls, repo_factory: RepositoryFactory) -> "TagService":
        """TagServiceのインスタンスを生成するファクトリメソッド

        Returns:
            TagService: タグサービスのインスタンス
        """
        return cls(tag_repo=repo_factory.create(TagRepository))

    @handle_service_errors(SERVICE_NAME, "作成", TagServiceError)
    @convert_read_model(TagRead)
    def create(self, create_data: TagCreate) -> Tag:
        """新しいタグを作成する

        Args:
            create_data: 作成するタグのデータ

        Returns:
            TagRead: 作成されたタグ

        Raises:
            NotFoundError: エンティティが存在しない場合
            TagServiceError: タグ作成に失敗した場合
        """
        tag = self.tag_repo.create(create_data)
        logger.info(f"タグを作成しました: {tag.id}")

        return tag

    @handle_service_errors(SERVICE_NAME, "更新", TagServiceError)
    @convert_read_model(TagRead)
    def update(self, tag_id: uuid.UUID, update_data: TagUpdate) -> Tag:
        """タグを更新する

        Args:
            tag_id: 更新するタグのID
            update_data: 更新データ

        Returns:
            TagRead: 更新されたタグ

        Raises:
            NotFoundError: タグが存在しない場合
            TagServiceError: タグ更新に失敗した場合
        """
        tag = self.tag_repo.update(tag_id, update_data)
        logger.info(f"タグを更新しました: {tag.id}")

        return tag

    @handle_service_errors(SERVICE_NAME, "削除", TagServiceError)
    def delete(self, tag_id: uuid.UUID, *, force: bool = False) -> bool:
        """タグを削除する

        Args:
            tag_id: 削除するタグのID
            force: 関連タスクが存在しても強制的に削除するかどうか

        Returns:
            bool: 削除が成功したかどうか

        Raises:
            TagServiceError: タグの削除に失敗した場合
        """
        existing_tag = self.tag_repo.get_by_id(tag_id)

        if not force:
            self.tag_repo.remove_all_memos(tag_id)
            self.tag_repo.remove_all_tasks(tag_id)
            self.tag_repo.delete(tag_id)
            success = True
        else:
            self.delete(tag_id, force=True)
            success = True

        logger.debug(f"タグ '{existing_tag.name}' を削除しました (ID: {tag_id})")
        return success

    @handle_service_errors(SERVICE_NAME, "取得", TagServiceError)
    @convert_read_model(TagRead)
    def get_by_id(self, tag_id: uuid.UUID) -> Tag:
        """IDでタグを取得する

        Args:
            tag_id: タグのID

        Returns:
            TagRead: 見つかったタグ

        Raises:
            NotFoundError: タグが存在しない場合
            TagServiceError: タグの取得に失敗した場合
        """
        tag = self.tag_repo.get_by_id(tag_id)
        logger.debug(f"タグを取得しました: {tag.id}")
        return tag

    @handle_service_errors(SERVICE_NAME, "取得", TagServiceError)
    @convert_read_model(TagRead)
    def get_by_name(self, name: str) -> Tag:
        """タグ名でタグを取得する

        Args:
            name: タグ名

        Returns:
            TagRead: 見つかったタグ

        Raises:
            NotFoundError: タグが存在しない場合
            TagServiceError: タグの取得に失敗した場合
        """
        tag = self.tag_repo.get_by_name(name)
        logger.debug(f"タグを取得しました: {tag.id}")
        return tag

    @handle_service_errors(SERVICE_NAME, "取得", TagServiceError)
    @convert_read_model(TagRead, is_list=True)
    def get_all(self) -> list[Tag]:
        """全てのタグを取得する

        Returns:
            list[TagRead]: 取得したタグのリスト

        Raises:
            NotFoundError: エンティティが存在しない場合
            TagServiceError: タグの取得に失敗した場合
        """
        tags = self.tag_repo.get_all()
        logger.debug(f"{len(tags)} 件のタグを取得しました。")
        return tags

    @handle_service_errors(SERVICE_NAME, "検索", TagServiceError)
    @convert_read_model(TagRead, is_list=True)
    def search_by_name(self, query: str) -> list[Tag]:
        """タグを名前で検索する

        Args:
            query: 検索クエリ

        Returns:
            list[TagRead]: 検索結果のタグのリスト

        Raises:
            TagServiceError: タグの検索に失敗した場合
        """
        tags = self.tag_repo.search_by_name(query)
        logger.debug(f"検索クエリ '{query}' に一致するタグを {len(tags)} 件取得しました。")
        return tags

    @handle_service_errors(SERVICE_NAME, "取得または作成", TagServiceError)
    def get_or_create_tag(self, name: str) -> TagRead:
        """タグ名でタグを取得し、存在しない場合は新規作成する

        Args:
            name: タグ名

        Returns:
            TagRead: 取得または作成されたタグ

        Raises:
            TagServiceError: タグの取得または作成に失敗した場合
        """
        try:
            tag = self.get_by_name(name)
            logger.debug(f"既存のタグを取得しました: {tag.id}")
        except Exception:
            create_data = TagCreate(name=name)
            tag = self.create(create_data)
            logger.debug(f"新しいタグを作成しました: {tag.id}")

        return tag
