"""リポジトリモジュール

このモジュールは、データベースアクセスのためのリポジトリクラスを提供します。
各モデルに対応するリポジトリクラスが定義されており、CRUD操作と追加の検索機能を提供します。

リポジトリクラスは BaseRepository を継承しており、共通のデータ操作ロジックを共有します。
また、RepositoryFactory クラスを使用して、データベースセッションを注入し、リポジトリインスタンスを生成します。
"""

from typing import TypeVar

from sqlmodel import Session

from logic.repositories.base import BaseRepository
from logic.repositories.memo import MemoRepository
from logic.repositories.project import ProjectRepository
from logic.repositories.tag import TagRepository
from logic.repositories.task import TaskRepository
from logic.repositories.term import TermRepository

_RepositoryT = TypeVar("_RepositoryT", bound=BaseRepository)


class RepositoryFactoryError(Exception):
    """リポジトリファクトリ関連の例外"""

    def __init__(self, message: str) -> None:
        """RepositoryFactoryError を初期化する

        Args:
            message (str): エラーメッセージ
        """
        super().__init__(message)


class RepositoryFactory:
    """リポジトリファクトリ

    データベースセッションを使用してリポジトリインスタンスを生成するファクトリクラス。
    """

    def __init__(self, session: Session) -> None:
        """RepositoryFactoryを初期化する

        Args:
            session: データベースセッション
        """
        self.session: Session = session

    def create(self, repo_class: type[_RepositoryT]) -> _RepositoryT:
        """任意のリポジトリを生成する

        Args:
            repo_class (type[_RepositoryT]): 生成するリポジトリのクラス

        Returns:
            _RepositoryT: 生成されたリポジトリインスタンス

        Raises:
            RepositoryFactoryError: リポジトリクラスが不正、または初期化に失敗した場合
        """
        try:
            repository = repo_class(self.session)
        except TypeError as exc:
            error_message = (
                "RepositoryFactoryでリポジトリの初期化に失敗しました。"
                " セッション以外の依存関係を必要とする可能性があります。"
            )
            raise RepositoryFactoryError(error_message) from exc
        if not isinstance(repository, BaseRepository):
            error_message = (
                f"RepositoryFactoryが生成したオブジェクトがBaseRepositoryを継承していません: {type(repository)!r}"
            )
            raise RepositoryFactoryError(error_message)

        return repository


__all__ = [
    "BaseRepository",
    "MemoRepository",
    "ProjectRepository",
    "TagRepository",
    "TaskRepository",
    "TermRepository",
    "RepositoryFactory",
    "RepositoryFactoryError",
]
