"""Kage プロジェクトの一貫した例外階層。

本モジュールは、層（Domain/Repository/Service/Application）間での例外の
発生・変換・伝播を統一するための基底クラス群を提供します。

設計原則（要点）:
- Domain 層のルール違反は DomainError（主に ValidationError/NotFoundError）。
- Repository 層の技術的失敗は RepositoryError に集約。
- Service 層では RepositoryError を ServiceError に変換して上位へ伝播。
- Application/CLI/UI 境界で KageError を適切にユーザー表示・ロギングへマッピング。

将来拡張として、外部 API/LLM 呼び出し失敗を表す ExternalServiceError を用意し、
既存の RepositoryError と互換に扱います（RepositoryError の派生）。
"""

from __future__ import annotations

__all__ = [
    "KageError",
    "ServiceError",
    "RepositoryError",
    "ExternalServiceError",
    "ApplicationError",
    "FactoryError",
    "DomainError",
    "NotFoundError",
    "ValidationError",
]


class KageError(Exception):
    """Kage の例外階層の最上位。

    すべてのアプリ内例外はこのクラスを継承します。境界層（Application/CLI/UI）
    では本クラス（あるいは派生）を捕捉して、ユーザー向け応答やロギングに
    マッピングしてください。
    """


class ServiceError(KageError):
    """サービス層の基底例外。

    - Repository 層からの技術的失敗（RepositoryError 等）をサービス層で
      抽象化した上位の失敗として表す際に使用します。
    - DomainError（Validation/NotFound など）は原則として変換せずに上位へ
      伝播してください（ユーザー起因の可能性が高いため）。
    """


class RepositoryError(KageError):
    """リポジトリ層（DB/IO/HTTP 等）での技術的失敗の基底例外。

    低レベルなライブラリ例外は "raise RepositoryError(...) from e" の形で
    例外チェインを保持したまま変換して raise してください。
    """


class ExternalServiceError(RepositoryError):
    """外部 API/LLM 等の外部サービス連携失敗を表す例外。

    RepositoryError の派生として定義することで、サービス層では
    RepositoryError と同様に ServiceError へ変換可能です。
    例:
        try:
            client.call()
        except SomeSDKError as e:
            raise ExternalServiceError("外部サービス呼び出しに失敗") from e
    """


class ApplicationError(KageError):
    """アプリケーション層（ユースケース/インタラクタ）での例外の基底。"""


class FactoryError(KageError):
    """ファクトリー/生成処理に関する例外。"""


class DomainError(KageError):
    """ドメイン層（ビジネスルール）での例外の基底。"""


class NotFoundError(DomainError):
    """エンティティが見つからない場合の例外。

    期待されるケース（例えば ID 指定で存在しない）では、そのまま上位へ伝播し、
    UI/CLI で情報的に扱います。
    """


class ValidationError(DomainError):
    """入力/状態がドメインルールに反していることを示す例外。"""
