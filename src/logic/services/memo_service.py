"""メモサービスの実装

このモジュールは、メモに関するビジネスロジックを提供します。
リポジトリ層を使用してデータアクセスを行い、複雑なメモ操作を実装します。
"""

import uuid

from loguru import logger

from logic.repositories import MemoRepository, RepositoryFactory
from logic.services.base import MyBaseError, ServiceBase, convert_read_model, handle_service_errors
from models import Memo, MemoCreate, MemoRead, MemoStatus, MemoUpdate

SERVICE_NAME = "メモサービス"


# Custom exceptions for memo service errors
class MemoServiceError(MyBaseError):
    """メモサービス層で発生する汎用的なエラー"""

    def __init__(self, message: str, operation: str = "不明な操作") -> None:
        super().__init__(f"メモの{operation}処理でエラーが発生しました: {message}")
        self.operation = operation


class MemoService(ServiceBase):
    """メモサービス

    メモに関するビジネスロジックを提供するサービスクラス。
    複数のリポジトリを組み合わせて、複雑なメモ操作を実装します。
    """

    def __init__(
        self,
        memo_repo: MemoRepository,
    ) -> None:
        """MemoServiceを初期化する

        Args:
            memo_repo: メモリポジトリ
        """
        self.memo_repo = memo_repo

    @classmethod
    def build_service(cls, repo_factory: RepositoryFactory) -> "MemoService":
        """MemoServiceのインスタンスを生成するファクトリメソッド

        Returns:
            MemoService: メモサービスのインスタンス
        """
        return cls(memo_repo=repo_factory.create(MemoRepository))

    @handle_service_errors(SERVICE_NAME, "作成", MemoServiceError)
    @convert_read_model(MemoRead)
    def create(self, create_data: MemoCreate) -> Memo:
        """メモを作成する

        Args:
            create_data: メモ作成データ

        Returns:
            MemoRead: 作成されたメモ

        Raises:
            NotFoundError: エンティティが存在しない場合
            MemoServiceError: メモ作成に失敗した場合
        """
        memo = self.memo_repo.create(create_data)
        logger.debug(f"メモを作成しました: {memo.id}")

        return memo

    @handle_service_errors(SERVICE_NAME, "更新", MemoServiceError)
    @convert_read_model(MemoRead)
    def update(self, memo_id: uuid.UUID, update_data: MemoUpdate) -> Memo:
        """メモを更新する

        Args:
            memo_id: 更新するメモのID
            update_data: メモ更新データ

        Returns:
            MemoRead: 更新されたメモ

        Raises:
            NotFoundError: メモが存在しない場合
            MemoServiceError: メモの更新に失敗した場合
        """
        memo = self.memo_repo.update(memo_id, update_data)
        logger.debug(f"メモを更新しました: {memo.id}")

        return memo

    @handle_service_errors(SERVICE_NAME, "削除", MemoServiceError)
    def delete(self, memo_id: uuid.UUID) -> bool:
        """メモを削除する

        Args:
            memo_id: 削除するメモのID

        Returns:
            bool: 削除が成功したかどうか

        Raises:
            MemoServiceError: メモの削除に失敗した場合
        """
        success = self.memo_repo.delete(memo_id)
        if success:
            logger.debug(f"メモを削除しました: {memo_id}")
        else:
            logger.warning(f"メモの削除に失敗しました: {memo_id}")

        return success

    @handle_service_errors(SERVICE_NAME, "タグ追加", MemoServiceError)
    @convert_read_model(MemoRead)
    def add_tag(self, memo_id: uuid.UUID, tag_id: uuid.UUID) -> Memo:
        """メモにタグを追加する

        Args:
            memo_id: メモID
            tag_id: タグID

        Returns:
            MemoRead: 更新されたメモ

        Raises:
            NotFoundError: メモまたはタグが存在しない場合
            MemoServiceError: メモの更新に失敗した場合
        """
        memo = self.memo_repo.add_tag(memo_id, tag_id)
        logger.debug(f"メモ({memo_id})にタグ({tag_id})を追加しました。")

        return memo

    @handle_service_errors(SERVICE_NAME, "タグ削除", MemoServiceError)
    @convert_read_model(MemoRead)
    def add_task(self, memo_id: uuid.UUID, task_id: uuid.UUID) -> Memo:
        """メモにタスクを追加する

        Args:
            memo_id: メモID
            task_id: タスクID

        Returns:
            MemoRead: 更新されたメモ

        Raises:
            NotFoundError: メモまたはタスクが存在しない場合
            MemoServiceError: メモの更新に失敗した場合
        """
        memo = self.memo_repo.add_task(memo_id, task_id)
        logger.debug(f"メモ({memo_id})にタスク({task_id})を追加しました。")

        return memo

    @handle_service_errors(SERVICE_NAME, "取得", MemoServiceError)
    @convert_read_model(MemoRead)
    def get_by_id(self, memo_id: uuid.UUID, *, with_details: bool = False) -> Memo:
        """IDでメモを取得する

        Args:
            memo_id: 取得するメモのID
            with_details: 関連エンティティを含めるかどうか

        Returns:
            MemoRead: 取得されたメモ

        Raises:
            NotFoundError: エンティティが存在しない場合
            MemoServiceError: メモの取得に失敗した場合
        """
        memo = self.memo_repo.get_by_id(memo_id, with_details=with_details)
        logger.debug(f"メモを取得しました: {memo.id}")

        return memo

    @handle_service_errors(SERVICE_NAME, "取得", MemoServiceError)
    @convert_read_model(MemoRead, is_list=True)
    def get_all(self, *, with_details: bool = False) -> list[Memo]:
        """全てのメモを取得する

        Args:
            with_details: 関連エンティティを含めるかどうか

        Returns:
            list[MemoRead]: 取得されたメモのリスト

        Raises:
            NotFoundError: エンティティが存在しない場合
            MemoServiceError: メモの取得に失敗した場合
        """
        memos = self.memo_repo.get_all(with_details=with_details)
        logger.debug(f"全てのメモを取得しました: {len(memos)} 件")

        return memos

    @handle_service_errors(SERVICE_NAME, "ステータス取得", MemoServiceError)
    @convert_read_model(MemoRead, is_list=True)
    def list_by_status(self, status: MemoStatus, *, with_details: bool = False) -> list[Memo]:
        """ステータスでメモ一覧を取得する

        Args:
            status: メモステータス
            with_details: 関連エンティティを含めるかどうか

        Returns:
            list[MemoRead]: 指定されたステータスのメモ一覧

        Raises:
            NotFoundError: エンティティが存在しない場合
            MemoServiceError: メモの取得に失敗した場合
        """
        memos = self.memo_repo.list_by_status(status, with_details=with_details)
        logger.debug(f"ステータス '{status}' のメモを {len(memos)} 件取得しました。")

        return memos

    @handle_service_errors(SERVICE_NAME, "検索", MemoServiceError)
    @convert_read_model(MemoRead, is_list=True)
    def search_memos(self, query: str, *, with_details: bool = False) -> list[Memo]:
        """クエリでメモを検索する

        Args:
            query: 検索クエリ
            with_details: 関連エンティティを含めるかどうか

        Returns:
            list[MemoRead]: 検索結果のメモ一覧

        Raises:
            NotFoundError: エンティティが存在しない場合
            MemoServiceError: メモの取得に失敗した場合
        """
        memos = self.memo_repo.search_by_title(query, with_details=with_details)
        memos += self.memo_repo.search_by_content(query, with_details=with_details)
        # 重複を排除
        memos = list({memo.id: memo for memo in memos}.values())
        logger.debug(f"クエリ '{query}' に一致するメモを {len(memos)} 件取得しました。")

        return memos
