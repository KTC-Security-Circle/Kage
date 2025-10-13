from __future__ import annotations


class KageError(Exception):
    """カスタム例外クラス"""


class ServiceError(KageError):
    """サービス層の基底例外クラス"""


class RepositoryError(KageError):
    """リポジトリ層の基底例外クラス"""


class ApplicationError(KageError):
    """アプリケーション層の基底例外クラス"""


class FactoryError(KageError):
    """ファクトリーに関連する例外"""


class DomainError(KageError):
    """ドメイン層の基底例外クラス"""


class NotFoundError(DomainError):
    """エンティティが見つからない場合の例外"""


class ValidationError(DomainError):
    """バリデーションエラー"""
