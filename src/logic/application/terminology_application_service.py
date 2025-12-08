"""用語管理のApplication Service

View層からSession管理を分離し、ビジネスロジックを調整する層
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any, override

from loguru import logger

from errors import ApplicationError, NotFoundError, ValidationError
from logic.application.base import BaseApplicationService
from logic.services.terminology_service import TerminologyService
from logic.unit_of_work import SqlModelUnitOfWork
from models import TermCreate, TermRead, TermStatus, TermUpdate

if TYPE_CHECKING:
    import uuid


class TerminologyApplicationError(ApplicationError):
    """用語管理のApplication Serviceで発生するエラー"""


class TermKeyValidationError(ValidationError, TerminologyApplicationError):
    """用語キーのバリデーションエラー"""


class TermNotFoundError(NotFoundError, TerminologyApplicationError):
    """用語が見つからないエラー"""


class TerminologyApplicationService(BaseApplicationService[type[SqlModelUnitOfWork]]):
    """用語管理のApplication Service

    View層からSession管理を分離し、ビジネスロジックを調整する層。
    用語の作成、更新、削除、検索、インポート/エクスポート機能を提供します。
    """

    def __init__(self, unit_of_work_factory: type[SqlModelUnitOfWork] = SqlModelUnitOfWork) -> None:
        """TerminologyApplicationServiceの初期化

        Args:
            unit_of_work_factory: Unit of Workファクトリー
        """
        super().__init__(unit_of_work_factory)

    @classmethod
    @override
    def get_instance(cls, *args: Any, **kwargs: Any) -> TerminologyApplicationService: ...

    # CRUD操作

    def create(
        self,
        key: str,
        title: str,
        description: str | None = None,
        *,
        status: TermStatus = TermStatus.DRAFT,
        source_url: str | None = None,
    ) -> TermRead:
        """用語を作成する

        Args:
            key: 用語の一意キー
            title: 用語のタイトル
            description: 用語の説明
            status: 用語のステータス
            source_url: 参照元URL

        Returns:
            TermRead: 作成された用語

        Raises:
            TermKeyValidationError: キーまたはタイトルが空の場合
        """
        if not key.strip():
            msg = "用語キーを入力してください"
            raise TermKeyValidationError(msg)

        if not title.strip():
            msg = "用語タイトルを入力してください"
            raise TermKeyValidationError(msg)

        create_model = TermCreate(
            key=key.strip(),
            title=title.strip(),
            description=description.strip() if description else None,
            status=status,
            source_url=source_url.strip() if source_url else None,
        )

        with self._unit_of_work_factory() as uow:
            term_service = uow.service_factory.get_service(TerminologyService)
            created = term_service.create(create_model)
            uow.commit()
            result = term_service.get_by_id(created.id)

        if result is None:
            msg = f"用語の作成に失敗しました: {key}"
            raise TerminologyApplicationError(msg)

        logger.info(f"用語作成完了 - key={result.key}, ID={result.id}")
        return result

    def update(self, term_id: uuid.UUID, update_data: TermUpdate) -> TermRead:
        """用語を更新する

        Args:
            term_id: 更新対象用語のID
            update_data: 用語更新データ

        Returns:
            TermRead: 更新後の用語

        Raises:
            TermNotFoundError: 用語が存在しない場合
        """
        with self._unit_of_work_factory() as uow:
            term_service = uow.service_factory.get_service(TerminologyService)
            term_service.update(term_id, update_data)
            uow.commit()
            result = term_service.get_by_id(term_id)

        if result is None:
            msg = f"用語が見つかりません: {term_id}"
            raise TermNotFoundError(msg)

        logger.info(f"用語更新完了 - ID={result.id}")
        return result

    def delete(self, term_id: uuid.UUID) -> bool:
        """用語を削除する

        Args:
            term_id: 削除する用語のID

        Returns:
            bool: 削除成功フラグ
        """
        with self._unit_of_work_factory() as uow:
            term_service = uow.service_factory.get_service(TerminologyService)
            success = term_service.delete(term_id)
            logger.info(f"用語削除完了: ID={term_id}, 結果={success}")
            return success

    # 取得系

    def get_by_id(self, term_id: uuid.UUID) -> TermRead | None:
        """IDで用語を取得する

        Args:
            term_id: 用語のID

        Returns:
            TermRead | None: 見つかった用語（存在しない場合はNone）
        """
        with self._unit_of_work_factory() as uow:
            term_service = uow.service_factory.get_service(TerminologyService)
            return term_service.get_by_id(term_id)

    def get_by_key(self, key: str) -> TermRead | None:
        """キーで用語を取得する

        Args:
            key: 用語の一意キー

        Returns:
            TermRead | None: 見つかった用語（存在しない場合はNone）
        """
        with self._unit_of_work_factory() as uow:
            term_service = uow.service_factory.get_service(TerminologyService)
            return term_service.get_by_key(key)

    def get_all(self) -> list[TermRead]:
        """全ての用語を取得する

        Returns:
            list[TermRead]: 全用語のリスト
        """
        with self._unit_of_work_factory() as uow:
            term_service = uow.service_factory.get_service(TerminologyService)
            return term_service.get_all()

    def search(
        self,
        query: str | None = None,
        *,
        tags: list[uuid.UUID] | None = None,
        status: TermStatus | None = None,
        include_synonyms: bool = True,
    ) -> list[TermRead]:
        """用語検索

        Serviceのsearchに委譲し、同義語を含めるか等のオプションを指定できる。

        Args:
            query: 検索クエリ（None可）
            tags: タグIDのリスト
            status: ステータスフィルタ
            include_synonyms: 同義語も検索対象に含めるか

        Returns:
            list[TermRead]: 検索結果
        """
        with self._unit_of_work_factory() as uow:
            term_service = uow.service_factory.get_service(TerminologyService)
            return term_service.search(query=query, tags=tags, status=status, include_synonyms=include_synonyms)

    # インポート/エクスポート

    def import_from_csv(self, file_path: Path | str) -> dict[str, Any]:
        """CSVファイルから用語をインポートする

        Args:
            file_path: CSVファイルのパス

        Returns:
            dict: インポート結果（success_count, failed_count, errorsを含む）
        """
        path = Path(file_path)
        if not path.exists():
            msg = f"ファイルが見つかりません: {file_path}"
            raise TerminologyApplicationError(msg)

        with self._unit_of_work_factory() as uow:
            term_service = uow.service_factory.get_service(TerminologyService)
            result = term_service.import_from_csv(path)
            logger.info(f"CSV インポート完了: 成功={result.success_count}, 失敗={result.failed_count}")
            return {
                "success_count": result.success_count,
                "failed_count": result.failed_count,
                "errors": result.errors,
            }

    def import_from_json(self, file_path: Path | str) -> dict[str, Any]:
        """JSONファイルから用語をインポートする

        Args:
            file_path: JSONファイルのパス

        Returns:
            dict: インポート結果（success_count, failed_count, errorsを含む）
        """
        path = Path(file_path)
        if not path.exists():
            msg = f"ファイルが見つかりません: {file_path}"
            raise TerminologyApplicationError(msg)

        with self._unit_of_work_factory() as uow:
            term_service = uow.service_factory.get_service(TerminologyService)
            result = term_service.import_from_json(path)
            logger.info(f"JSON インポート完了: 成功={result.success_count}, 失敗={result.failed_count}")
            return {
                "success_count": result.success_count,
                "failed_count": result.failed_count,
                "errors": result.errors,
            }

    def export_to_csv(self, file_path: Path | str) -> int:
        """用語をCSVファイルにエクスポートする

        Args:
            file_path: エクスポート先のCSVファイルパス

        Returns:
            int: エクスポートした用語の件数
        """
        path = Path(file_path)

        with self._unit_of_work_factory() as uow:
            term_service = uow.service_factory.get_service(TerminologyService)
            count = term_service.export_to_csv(path)
            logger.info(f"CSV エクスポート完了: {count}件 -> {file_path}")
            return count

    def export_to_json(self, file_path: Path | str) -> int:
        """用語をJSONファイルにエクスポートする

        Args:
            file_path: エクスポート先のJSONファイルパス

        Returns:
            int: エクスポートした用語の件数
        """
        path = Path(file_path)

        with self._unit_of_work_factory() as uow:
            term_service = uow.service_factory.get_service(TerminologyService)
            count = term_service.export_to_json(path)
            logger.info(f"JSON エクスポート完了: {count}件 -> {file_path}")
            return count

    # タグ操作

    def sync_tags(self, term_id: uuid.UUID, tag_ids: list[uuid.UUID]) -> TermRead:
        """用語のタグを同期する

        既存のタグと指定されたタグを比較し、差分を反映します。
        - 指定されていない既存タグは削除
        - 新しく指定されたタグは追加

        Args:
            term_id: 用語のID
            tag_ids: 同期後のタグIDリスト

        Returns:
            TermRead: 更新された用語

        Raises:
            TermNotFoundError: 用語が見つからない場合
        """
        with self._unit_of_work_factory() as uow:
            term_service = uow.service_factory.get_service(TerminologyService)

            # 現在のタグIDを取得
            term = term_service.get_by_id(term_id)
            current_tag_ids = {tag.id for tag in term.tags}
            desired_tag_ids = set(tag_ids)

            # 削除するタグと追加するタグを計算
            tags_to_remove = current_tag_ids - desired_tag_ids
            tags_to_add = desired_tag_ids - current_tag_ids

            # タグを削除
            for tag_id in tags_to_remove:
                term = term_service.remove_tag(term_id, tag_id)

            # タグを追加
            for tag_id in tags_to_add:
                term = term_service.add_tag(term_id, tag_id)

        logger.info(f"タグ同期完了: 用語ID={term_id}, 追加={len(tags_to_add)}, 削除={len(tags_to_remove)}")
        return term
