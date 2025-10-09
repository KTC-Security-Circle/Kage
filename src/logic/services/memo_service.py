"""メモサービスの実装

このモジュールは、メモに関するビジネスロジックを提供します。
リポジトリ層を使用してデータアクセスを行い、複雑なメモ操作を実装します。
"""

import uuid

from loguru import logger

from logic.repositories.memo import MemoRepository
from logic.repositories.task import TaskRepository
from logic.services.base import MyBaseError, ServiceBase
from models import MemoCreate, MemoRead, MemoUpdate


# Custom exceptions for memo service errors
class MemoServiceCreateError(MyBaseError):
    """メモ作成時のカスタム例外クラス

    Args:
        arg (str): エラーメッセージ
    """

    def __str__(self) -> str:
        return f"メモ作成エラー: {self.arg}"


class MemoServiceCheckError(MyBaseError):
    """メモ存在確認時のカスタム例外クラス

    Args:
        arg (str): エラーメッセージ
    """

    def __str__(self) -> str:
        return f"メモ存在確認エラー: {self.arg}"


class MemoServiceUpdateError(MyBaseError):
    """メモ更新時のカスタム例外クラス

    Args:
        arg (str): エラーメッセージ
    """

    def __str__(self) -> str:
        return f"メモ更新エラー: {self.arg}"


class MemoServiceDeleteError(MyBaseError):
    """メモ削除時のカスタム例外クラス

    Args:
        arg (str): エラーメッセージ
    """

    def __str__(self) -> str:
        return f"メモ削除エラー: {self.arg}"


class MemoServiceGetError(MyBaseError):
    """メモ取得時のカスタム例外クラス

    Args:
        arg (str): エラーメッセージ
    """

    def __str__(self) -> str:
        return f"メモ取得エラー: {self.arg}"


type MemoServiceError = (
    MemoServiceGetError
    | MemoServiceCreateError
    | MemoServiceCheckError
    | MemoServiceUpdateError
    | MemoServiceDeleteError
)


class MemoService(ServiceBase[MemoServiceError]):
    """メモサービス

    メモに関するビジネスロジックを提供するサービスクラス。
    複数のリポジトリを組み合わせて、複雑なメモ操作を実装します。
    """

    def __init__(
        self,
        memo_repo: MemoRepository,
        task_repo: TaskRepository,
    ) -> None:
        """MemoServiceを初期化する

        Args:
            memo_repo: メモリポジトリ
            task_repo: タスクリポジトリ
        """
        self.memo_repo = memo_repo
        self.task_repo = task_repo

    def _check_memo_exists(self, memo_id: uuid.UUID) -> MemoRead:
        """メモの存在を確認する

        Args:
            memo_id: メモのID

        Returns:
            MemoRead: 存在するメモ

        Raises:
            MemoServiceCheckError: メモが存在しない場合
        """
        memo = self.memo_repo.get_by_id(memo_id)
        if not memo:
            self._log_error_and_raise(f"メモID {memo_id} が見つかりません", MemoServiceCheckError)
        return MemoRead.model_validate(memo)

    def _check_task_exists(self, task_id: uuid.UUID) -> None:
        """タスクの存在を確認する

        Args:
            task_id: タスクのID

        Raises:
            MemoServiceCheckError: タスクが存在しない場合
        """
        task = self.task_repo.get_by_id(task_id)
        if not task:
            self._log_error_and_raise(f"タスクID {task_id} が見つかりません", MemoServiceCheckError)

    def create_memo(self, memo_data: MemoCreate) -> MemoRead:
        """新しいメモを作成する

        Args:
            memo_data: 作成するメモのデータ

        Returns:
            MemoRead: 作成されたメモ

        Raises:
            MemoServiceCreateError: タスクIDが存在しない場合、またはメモ作成に失敗した場合
        """
        # [AI GENERATED] タスクIDの存在を確認
        self._check_task_exists(memo_data.task_id)

        try:
            memo = self.memo_repo.create(memo_data)
            if not memo:
                self._log_error_and_raise("メモの作成に失敗しました", MemoServiceCreateError)

            logger.info(f"メモを作成しました (ID: {memo.id}, タスクID: {memo.task_id})")
            return MemoRead.model_validate(memo)
        except Exception as e:
            logger.exception(f"メモ作成中にエラーが発生しました: {e}")
            self._log_error_and_raise("メモの作成に失敗しました", MemoServiceCreateError)

    def update_memo(self, memo_id: uuid.UUID, memo_data: MemoUpdate) -> MemoRead:
        """メモを更新する

        Args:
            memo_id: 更新するメモのID
            memo_data: 更新するメモのデータ

        Returns:
            MemoRead: 更新されたメモ

        Raises:
            MemoServiceCheckError: メモが存在しない場合
            MemoServiceUpdateError: メモ更新に失敗した場合
        """
        # [AI GENERATED] メモの存在を確認
        self._check_memo_exists(memo_id)

        try:
            updated_memo = self.memo_repo.update(memo_id, memo_data)
            if not updated_memo:
                self._log_error_and_raise(f"メモの更新に失敗しました (ID: {memo_id})", MemoServiceUpdateError)

            logger.info(f"メモを更新しました (ID: {memo_id})")
            return MemoRead.model_validate(updated_memo)
        except Exception as e:
            logger.exception(f"メモ更新中にエラーが発生しました: {e}")
            self._log_error_and_raise("メモの更新に失敗しました", MemoServiceUpdateError)

    def delete_memo(self, memo_id: uuid.UUID) -> bool:
        """メモを削除する

        Args:
            memo_id: 削除するメモのID

        Returns:
            bool: 削除が成功した場合True

        Raises:
            MemoServiceCheckError: メモが存在しない場合
            MemoServiceDeleteError: メモ削除に失敗した場合
        """
        # [AI GENERATED] メモの存在を確認
        existing_memo = self._check_memo_exists(memo_id)

        try:
            success = self.memo_repo.delete(memo_id)
            if not success:
                self._log_error_and_raise(f"メモの削除に失敗しました (ID: {memo_id})", MemoServiceDeleteError)
        except Exception as e:
            logger.exception(f"メモ削除中にエラーが発生しました: {e}")
            self._log_error_and_raise("メモの削除に失敗しました", MemoServiceDeleteError)
        else:
            logger.info(f"メモを削除しました (ID: {memo_id}, タスクID: {existing_memo.task_id})")
            return success

    def get_memo_by_id(self, memo_id: uuid.UUID) -> MemoRead | None:
        """IDでメモを取得する

        Args:
            memo_id: メモのID

        Returns:
            MemoRead | None: 見つかったメモ、存在しない場合はNone

        Raises:
            MemoServiceGetError: メモ取得に失敗した場合
        """
        try:
            memo = self.memo_repo.get_by_id(memo_id)
            if not memo:
                logger.warning(f"メモサービス: メモが見つかりませんでした {memo_id}")
                return None

            logger.info(f"メモサービス: メモが見つかりました ID: {memo.id}, content_length: {len(memo.content)}")
            return MemoRead.model_validate(memo)
        except Exception as e:
            logger.exception(f"メモ取得中にエラーが発生しました: {e}")
            self._log_error_and_raise(f"メモの取得に失敗しました (ID: {memo_id})", MemoServiceGetError)

    def get_all_memos(self) -> list[MemoRead]:
        """全てのメモを取得する

        Returns:
            list[MemoRead]: 全てのメモのリスト

        Raises:
            MemoServiceGetError: メモ一覧の取得に失敗した場合
        """
        try:
            memos = self.memo_repo.get_all()
            return [MemoRead.model_validate(memo) for memo in memos]
        except Exception as e:
            logger.exception(f"メモ一覧取得中にエラーが発生しました: {e}")
            self._log_error_and_raise("メモ一覧の取得に失敗しました", MemoServiceGetError)

    def get_memos_by_task_id(self, task_id: uuid.UUID) -> list[MemoRead]:
        """タスクIDでメモを取得する

        Args:
            task_id: タスクのID

        Returns:
            list[MemoRead]: 指定されたタスクのメモのリスト

        Raises:
            MemoServiceCheckError: タスクが存在しない場合
            MemoServiceGetError: メモ取得に失敗した場合
        """
        # [AI GENERATED] タスクの存在を確認
        self._check_task_exists(task_id)

        try:
            memos = self.memo_repo.get_by_task_id(task_id)
            return [MemoRead.model_validate(memo) for memo in memos]
        except Exception as e:
            logger.exception(f"タスク別メモ取得中にエラーが発生しました: {e}")
            self._log_error_and_raise("タスク別メモの取得に失敗しました", MemoServiceGetError)

    def search_memos(self, query: str) -> list[MemoRead]:
        """メモを内容で検索する

        Args:
            query: 検索クエリ

        Returns:
            list[MemoRead]: 検索条件に一致するメモのリスト

        Raises:
            MemoServiceGetError: メモの検索に失敗した場合
        """
        try:
            memos = self.memo_repo.search_by_content(query)
            return [MemoRead.model_validate(memo) for memo in memos]
        except Exception as e:
            logger.exception(f"メモ検索中にエラーが発生しました: {e}")
            self._log_error_and_raise("メモの検索に失敗しました", MemoServiceGetError)
