"""タグサービスの実装

このモジュールは、タグに関するビジネスロジックを提供します。
リポジトリ層を使用してデータアクセスを行い、複雑なタグ操作を実装します。
"""

import uuid

from loguru import logger

from logic.repositories.tag import TagRepository
from logic.repositories.task_tag import TaskTagRepository
from logic.services.base import MyBaseError, ServiceBase
from models.tag import TagCreate, TagRead, TagUpdate


# Custom exceptions for tag service errors
class TagServiceCreateError(MyBaseError):
    """タグ作成時のカスタム例外クラス

    Args:
        arg (str): エラーメッセージ
    """

    def __str__(self) -> str:
        return f"タグ作成エラー: {self.arg}"


class TagServiceCheckError(MyBaseError):
    """タグ存在確認時のカスタム例外クラス

    Args:
        arg (str): エラーメッセージ
    """

    def __str__(self) -> str:
        return f"タグ存在確認エラー: {self.arg}"


class TagServiceUpdateError(MyBaseError):
    """タグ更新時のカスタム例外クラス

    Args:
        arg (str): エラーメッセージ
    """

    def __str__(self) -> str:
        return f"タグ更新エラー: {self.arg}"


class TagServiceDeleteError(MyBaseError):
    """タグ削除時のカスタム例外クラス

    Args:
        arg (str): エラーメッセージ
    """

    def __str__(self) -> str:
        return f"タグ削除エラー: {self.arg}"


class TagServiceGetError(MyBaseError):
    """タグ取得時のカスタム例外クラス

    Args:
        arg (str): エラーメッセージ
    """

    def __str__(self) -> str:
        return f"タグ取得エラー: {self.arg}"


type TagServiceError = (
    TagServiceGetError | TagServiceCreateError | TagServiceCheckError | TagServiceUpdateError | TagServiceDeleteError
)


class TagService(ServiceBase[TagServiceError]):
    """タグサービス

    タグに関するビジネスロジックを提供するサービスクラス。
    複数のリポジトリを組み合わせて、複雑なタグ操作を実装します。
    """

    def __init__(self) -> None:
        """TagServiceを初期化する"""
        self.tag_repo = TagRepository()
        self.task_tag_repo = TaskTagRepository()

    # タグの存在を確認するメソッド
    def _check_tag_exists(self, tag_id: uuid.UUID) -> TagRead:
        """タグの存在を確認する

        Args:
            tag_id: タグのID

        Returns:
            TagRead: 存在するタグ

        Raises:
            TagServiceCheckError: タグが存在しない場合
            ValidationError: タグデータの検証に失敗した場合
        """
        tag = self.tag_repo.get_by_id(tag_id)
        if not tag:
            self._log_error_and_raise(f"タグID {tag_id} が見つかりません", TagServiceCheckError)
        return TagRead.model_validate(tag)

    def create_tag(self, tag_data: TagCreate) -> TagRead:
        """新しいタグを作成する

        Args:
            tag_data: 作成するタグのデータ

        Returns:
            TagRead: 作成されたタグ

        Raises:
            TagServiceCreateError: 同一名のタグが既に存在する場合、またはタグ作成に失敗した場合
            ValidationError: タグデータの検証に失敗した場合
        """
        # [AI GENERATED] 同一名のタグが既に存在するかチェック
        existing_tag = self.tag_repo.get_by_name(tag_data.name)
        if existing_tag:
            self._log_error_and_raise(f"タグ名 '{tag_data.name}' は既に存在します", TagServiceCreateError)

        tag = self.tag_repo.create(tag_data)
        if not tag:
            self._log_error_and_raise("タグの作成に失敗しました", TagServiceCreateError)

        logger.info(f"タグ '{tag.name}' を作成しました (ID: {tag.id})")
        return TagRead.model_validate(tag)

    def update_tag(self, tag_id: uuid.UUID, tag_data: TagUpdate) -> TagRead:
        """タグを更新する

        Args:
            tag_id: 更新するタグのID
            tag_data: 更新するタグのデータ

        Returns:
            TagRead: 更新されたタグ

        Raises:
            TagServiceCheckError: タグが存在しない場合
            TagServiceUpdateError: 同一名のタグが既に存在する場合、またはタグ更新に失敗した場合
            ValidationError: タグデータの検証に失敗した場合
        """
        # タグの存在を確認
        self._check_tag_exists(tag_id)

        # [AI GENERATED] 新しいタグ名が指定されている場合、重複チェック
        if tag_data.name is not None:
            existing_tag = self.tag_repo.get_by_name(tag_data.name)
            if existing_tag and existing_tag.id != tag_id:
                self._log_error_and_raise(f"タグ名 '{tag_data.name}' は既に存在します", TagServiceUpdateError)

        updated_tag = self.tag_repo.update(tag_id, tag_data)
        if not updated_tag:
            self._log_error_and_raise(f"タグの更新に失敗しました (ID: {tag_id})", TagServiceUpdateError)

        logger.info(f"タグ '{updated_tag.name}' を更新しました (ID: {tag_id})")
        return TagRead.model_validate(updated_tag)

    def delete_tag(self, tag_id: uuid.UUID, *, force: bool = False) -> bool:
        """タグを削除する

        Args:
            tag_id: 削除するタグのID
            force: 関連タスクがある場合も強制削除するかどうか(default: False)

        Returns:
            bool: 削除が成功した場合True

        Raises:
            TagServiceCheckError: タグが存在しない場合
            TagServiceDeleteError: タスクが関連している場合、または削除に失敗した場合
        """
        # [AI GENERATED] タグの存在を確認
        existing_tag = self._check_tag_exists(tag_id)

        # [AI GENERATED] 関連するタスクタグがあるかチェック
        related_task_tags = self.task_tag_repo.get_by_tag_id(tag_id)
        if related_task_tags and not force:
            self._log_error_and_raise(
                f"タグ '{existing_tag.name}' には {len(related_task_tags)} 個のタスクが関連しています。"
                "force=Trueで強制削除できます",
                TagServiceDeleteError,
            )

        # [AI GENERATED] 強制削除の場合、関連するタスクタグを削除
        if force and related_task_tags:
            for task_tag in related_task_tags:
                self.task_tag_repo.delete_by_task_and_tag(task_tag.task_id, task_tag.tag_id)
            logger.info(f"{len(related_task_tags)} 個のタスクタグ関連を削除しました")

        success = self.tag_repo.delete(tag_id)
        if not success:
            self._log_error_and_raise(f"タグの削除に失敗しました (ID: {tag_id})", TagServiceDeleteError)

        logger.info(f"タグ '{existing_tag.name}' を削除しました (ID: {tag_id})")
        return success

    def get_tag_by_id(self, tag_id: uuid.UUID) -> TagRead | None:
        """IDでタグを取得する

        Args:
            tag_id: タグのID

        Returns:
            TagRead | None: 見つかったタグ、存在しない場合はNone

        Raises:
            TagServiceGetError: タグ取得に失敗した場合
            ValidationError: タグデータの検証に失敗した場合
        """
        try:
            tag = self.tag_repo.get_by_id(tag_id)
            if not tag:
                return None
            return TagRead.model_validate(tag)
        except Exception:
            self._log_error_and_raise(f"タグの取得に失敗しました (ID: {tag_id})", TagServiceGetError)

    def get_tag_by_name(self, name: str) -> TagRead | None:
        """タグ名でタグを取得する

        Args:
            name: タグ名

        Returns:
            TagRead | None: 見つかったタグ、存在しない場合はNone

        Raises:
            TagServiceGetError: タグ取得に失敗した場合
            ValidationError: タグデータの検証に失敗した場合
        """
        try:
            tag = self.tag_repo.get_by_name(name)
            if not tag:
                return None
            return TagRead.model_validate(tag)
        except Exception:
            self._log_error_and_raise(f"タグの取得に失敗しました (名前: {name})", TagServiceGetError)

    def get_all_tags(self) -> list[TagRead]:
        """全てのタグを取得する

        Returns:
            list[TagRead]: 全てのタグのリスト

        Raises:
            TagServiceGetError: タグ一覧の取得に失敗した場合
            ValidationError: タグデータの検証に失敗した場合
        """
        try:
            tags = self.tag_repo.get_all()
            return [TagRead.model_validate(tag) for tag in tags]
        except Exception:
            self._log_error_and_raise("タグ一覧の取得に失敗しました", TagServiceGetError)

    def search_tags(self, query: str) -> list[TagRead]:
        """タグを名前で検索する

        Args:
            query: 検索クエリ

        Returns:
            list[TagRead]: 検索条件に一致するタグのリスト

        Raises:
            TagServiceGetError: タグの検索に失敗した場合
            ValidationError: タグデータの検証に失敗した場合
        """
        try:
            tags = self.tag_repo.search_by_name(query)
            return [TagRead.model_validate(tag) for tag in tags]
        except Exception:
            self._log_error_and_raise(f"タグの検索に失敗しました (クエリ: {query})", TagServiceGetError)

    def check_tag_exists_by_name(self, name: str) -> bool:
        """タグ名でタグの存在をチェックする

        Args:
            name: タグ名

        Returns:
            bool: タグが存在する場合True

        Raises:
            TagServiceGetError: タグ存在チェックに失敗した場合
        """
        try:
            return self.tag_repo.exists_by_name(name)
        except Exception:
            self._log_error_and_raise(f"タグ存在チェックに失敗しました (名前: {name})", TagServiceGetError)

    def get_or_create_tag(self, name: str) -> TagRead:
        """タグ名でタグを取得、存在しない場合は作成する

        Args:
            name: タグ名

        Returns:
            TagRead: 取得または作成されたタグ

        Raises:
            TagServiceCreateError: タグの作成に失敗した場合
            TagServiceGetError: タグの取得に失敗した場合
            ValidationError: タグデータの検証に失敗した場合
        """
        # [AI GENERATED] 既存のタグを検索
        existing_tag = self.get_tag_by_name(name)
        if existing_tag:
            logger.debug(f"既存のタグ '{name}' を取得しました (ID: {existing_tag.id})")
            return existing_tag

        # [AI GENERATED] 新規作成
        tag_data = TagCreate(name=name)
        return self.create_tag(tag_data)
