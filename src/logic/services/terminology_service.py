"""用語管理サービスの実装

このモジュールは、用語管理に関するビジネスロジックを提供します。
リポジトリ層を使用してデータアクセスを行い、複雑な用語操作を実装します。
"""

import csv
import json
import uuid
from dataclasses import dataclass
from pathlib import Path

from loguru import logger

from logic.repositories import RepositoryFactory, TagRepository
from logic.repositories.term import TermRepository
from logic.services.base import MyBaseError, ServiceBase, convert_read_model, handle_service_errors
from models import Term, TermCreate, TermRead, TermStatus, TermUpdate

SERVICE_NAME = "用語管理サービス"


class TerminologyServiceError(MyBaseError):
    """用語管理サービス層で発生する汎用的なエラー"""

    def __init__(self, message: str, operation: str = "不明な操作") -> None:
        super().__init__(f"用語の{operation}処理でエラーが発生しました: {message}")
        self.operation = operation


@dataclass
class ImportResult:
    """インポート結果

    Attributes:
        success_count: 成功した件数
        failed_count: 失敗した件数
        errors: エラーメッセージのリスト
    """

    success_count: int
    failed_count: int
    errors: list[str]


@dataclass
class TermForPrompt:
    """エージェント用の用語データ

    Attributes:
        key: 用語のキー
        title: 用語のタイトル
        description: 用語の説明
        synonyms: 同義語のリスト
    """

    key: str
    title: str
    description: str | None
    synonyms: list[str]

    def to_prompt_text(self) -> str:
        """プロンプト用のテキストを生成する

        Returns:
            str: プロンプト用のテキスト
        """
        text = f"- {self.key}: {self.title}"
        if self.description:
            text += f" - {self.description}"
        if self.synonyms:
            text += f" (同義語: {', '.join(self.synonyms)})"
        return text


class TerminologyService(ServiceBase):
    """用語管理サービス

    用語管理に関するビジネスロジックを提供するサービスクラス。
    複数のリポジトリを組み合わせて、複雑な用語操作を実装します。
    """

    def __init__(self, term_repo: TermRepository, tag_repo: TagRepository) -> None:
        """用語管理サービスの初期化

        Args:
            term_repo: 用語リポジトリ
            tag_repo: タグリポジトリ
        """
        self.term_repo = term_repo
        self.tag_repo = tag_repo

    @classmethod
    def build_service(cls, repo_factory: RepositoryFactory) -> "TerminologyService":
        """TerminologyServiceのインスタンスを生成するファクトリメソッド

        Args:
            repo_factory: リポジトリファクトリ

        Returns:
            TerminologyService: 用語管理サービスのインスタンス
        """
        return cls(term_repo=repo_factory.create(TermRepository), tag_repo=repo_factory.create(TagRepository))

    # ==============================================================================
    # CRUD operations
    # ==============================================================================

    @handle_service_errors(SERVICE_NAME, "作成", TerminologyServiceError)
    @convert_read_model(TermRead)
    def create(self, create_data: TermCreate) -> Term:
        """新しい用語を作成する

        Args:
            create_data: 作成する用語のデータ

        Returns:
            TermRead: 作成された用語

        Raises:
            AlreadyExistsError: 同じkeyの用語が既に存在する場合
            TerminologyServiceError: 用語作成に失敗した場合
        """
        term = self.term_repo.create(create_data)
        logger.info(f"用語を作成しました: {term.key} ({term.id})")

        return term

    @handle_service_errors(SERVICE_NAME, "更新", TerminologyServiceError)
    @convert_read_model(TermRead)
    def update(self, term_id: uuid.UUID, update_data: TermUpdate) -> Term:
        """用語を更新する

        Args:
            term_id: 更新する用語のID
            update_data: 更新データ

        Returns:
            TermRead: 更新された用語

        Raises:
            NotFoundError: 用語が存在しない場合
            TerminologyServiceError: 用語更新に失敗した場合
        """
        term = self.term_repo.update(term_id, update_data)
        logger.info(f"用語を更新しました: {term.key} ({term.id})")

        return term

    @handle_service_errors(SERVICE_NAME, "削除", TerminologyServiceError)
    def delete(self, term_id: uuid.UUID, *, force: bool = False) -> bool:
        """用語を削除する

        Args:
            term_id: 削除する用語のID
            force: 関連データが存在しても強制的に削除するかどうか

        Returns:
            bool: 削除が成功したかどうか

        Raises:
            TerminologyServiceError: 用語の削除に失敗した場合
        """
        existing_term = self.term_repo.get_by_id(term_id)

        if not force:
            # タグを削除
            self.term_repo.remove_all_tags(term_id)

        # 削除実行（同義語はカスケード削除される）
        success = self.term_repo.delete(term_id)

        logger.info(f"用語 '{existing_term.key}' を削除しました (ID: {term_id})")
        return success

    # ==============================================================================
    # Get operations
    # ==============================================================================

    @handle_service_errors(SERVICE_NAME, "取得", TerminologyServiceError)
    @convert_read_model(TermRead)
    def get_by_id(self, term_id: uuid.UUID) -> Term:
        """IDで用語を取得する

        Args:
            term_id: 用語のID

        Returns:
            TermRead: 見つかった用語

        Raises:
            NotFoundError: 用語が存在しない場合
            TerminologyServiceError: 用語の取得に失敗した場合
        """
        term = self.term_repo.get_by_id(term_id, with_details=True)
        logger.debug(f"用語を取得しました: {term.key} ({term.id})")
        return term

    @handle_service_errors(SERVICE_NAME, "取得", TerminologyServiceError)
    @convert_read_model(TermRead)
    def get_by_key(self, key: str) -> Term:
        """キーで用語を取得する

        Args:
            key: 用語のキー

        Returns:
            TermRead: 見つかった用語

        Raises:
            NotFoundError: 用語が存在しない場合
            TerminologyServiceError: 用語の取得に失敗した場合
        """
        term = self.term_repo.get_by_key(key, with_details=True)
        logger.debug(f"用語を取得しました: {term.key} ({term.id})")
        return term

    @handle_service_errors(SERVICE_NAME, "取得", TerminologyServiceError)
    @convert_read_model(TermRead, is_list=True)
    def get_all(self) -> list[Term]:
        """全ての用語を取得する

        Returns:
            list[TermRead]: 取得した用語のリスト

        Raises:
            TerminologyServiceError: 用語の取得に失敗した場合
        """
        terms = self.term_repo.get_all(with_details=True)
        logger.debug(f"{len(terms)} 件の用語を取得しました。")
        return terms

    # ==============================================================================
    # Search operations
    # ==============================================================================

    @handle_service_errors(SERVICE_NAME, "検索", TerminologyServiceError)
    @convert_read_model(TermRead, is_list=True)
    def search(
        self,
        query: str | None = None,
        *,
        tags: list[uuid.UUID] | None = None,
        status: TermStatus | None = None,
        include_synonyms: bool = True,
    ) -> list[Term]:
        """用語を検索する

        Args:
            query: 検索クエリ（キー、タイトル、説明を検索）
            tags: フィルタリングするタグのIDリスト
            status: フィルタリングするステータス
            include_synonyms: 同義語も検索対象に含めるか

        Returns:
            list[TermRead]: 検索結果の用語のリスト

        Raises:
            TerminologyServiceError: 用語の検索に失敗した場合
        """
        terms = self.term_repo.search(
            query=query, tags=tags, status=status, include_synonyms=include_synonyms, with_details=True
        )
        logger.debug(f"検索クエリに一致する用語を {len(terms)} 件取得しました。")
        return terms

    # ==============================================================================
    # Tag operations
    # ==============================================================================

    @handle_service_errors(SERVICE_NAME, "タグ追加", TerminologyServiceError)
    @convert_read_model(TermRead)
    def add_tag(self, term_id: uuid.UUID, tag_id: uuid.UUID) -> Term:
        """用語にタグを追加する

        Args:
            term_id: 用語のID
            tag_id: 追加するタグのID

        Returns:
            TermRead: 更新された用語

        Raises:
            NotFoundError: エンティティが存在しない場合
            TerminologyServiceError: タグ追加に失敗した場合
        """
        term = self.term_repo.add_tag(term_id, tag_id)
        logger.info(f"用語({term_id})にタグ({tag_id})を追加しました。")
        return term

    @handle_service_errors(SERVICE_NAME, "タグ削除", TerminologyServiceError)
    @convert_read_model(TermRead)
    def remove_tag(self, term_id: uuid.UUID, tag_id: uuid.UUID) -> Term:
        """用語からタグを削除する

        Args:
            term_id: 用語のID
            tag_id: 削除するタグのID

        Returns:
            TermRead: 更新された用語

        Raises:
            NotFoundError: エンティティが存在しない場合
            TerminologyServiceError: タグ削除に失敗した場合
        """
        term = self.term_repo.remove_tag(term_id, tag_id)
        logger.info(f"用語({term_id})からタグ({tag_id})を削除しました。")
        return term

    @handle_service_errors(SERVICE_NAME, "タグ同期", TerminologyServiceError)
    @convert_read_model(TermRead)
    def sync_tags(self, term_id: uuid.UUID, tag_ids: set[uuid.UUID]) -> Term:
        """用語のタグを一括同期する

        既存のループ操作を1回のDB操作に最適化し、N+1問題を回避します。

        Args:
            term_id: 用語のID
            tag_ids: 設定するタグIDのセット

        Returns:
            TermRead: 更新された用語

        Raises:
            NotFoundError: 用語またはタグが存在しない場合
            TerminologyServiceError: タグ同期に失敗した場合
        """
        term = self.term_repo.sync_tags(term_id, tag_ids)
        logger.info(f"用語({term_id})のタグを同期しました: {len(tag_ids)}個")
        return term

    # ==============================================================================
    # Synonym operations
    # ==============================================================================

    @handle_service_errors(SERVICE_NAME, "同義語追加", TerminologyServiceError)
    @convert_read_model(TermRead)
    def add_synonym(self, term_id: uuid.UUID, synonym_text: str) -> Term:
        """用語に同義語を追加する

        Args:
            term_id: 用語のID
            synonym_text: 同義語のテキスト

        Returns:
            TermRead: 更新された用語

        Raises:
            NotFoundError: エンティティが存在しない場合
            TerminologyServiceError: 同義語追加に失敗した場合
        """
        term = self.term_repo.add_synonym(term_id, synonym_text)
        logger.info(f"用語({term_id})に同義語({synonym_text})を追加しました。")
        return term

    @handle_service_errors(SERVICE_NAME, "同義語削除", TerminologyServiceError)
    @convert_read_model(TermRead)
    def remove_synonym(self, term_id: uuid.UUID, synonym_id: uuid.UUID) -> Term:
        """用語から同義語を削除する

        Args:
            term_id: 用語のID
            synonym_id: 削除する同義語のID

        Returns:
            TermRead: 更新された用語

        Raises:
            NotFoundError: エンティティが存在しない場合
            TerminologyServiceError: 同義語削除に失敗した場合
        """
        term = self.term_repo.remove_synonym(term_id, synonym_id)
        logger.info(f"用語({term_id})から同義語({synonym_id})を削除しました。")
        return term

    # ==============================================================================
    # Import/Export operations
    # ==============================================================================

    def _import_term_from_csv_row(self, row: dict[str, str]) -> None:
        """CSV行から用語をインポートする（ヘルパーメソッド）

        Args:
            row: CSV行の辞書

        Raises:
            Exception: インポートに失敗した場合
        """
        # 用語作成
        term_data = TermCreate(
            key=row["key"],
            title=row["title"],
            description=row.get("description") or None,
            status=TermStatus(row.get("status", "draft")),
            source_url=row.get("source_url") or None,
        )
        term = self.term_repo.create(term_data)
        if not term.id:
            return

        # 同義語追加
        if synonyms_str := row.get("synonyms"):
            for synonym in synonyms_str.split(";"):
                if synonym.strip():
                    self.term_repo.add_synonym(term.id, synonym.strip())

        # タグ追加
        if tags_str := row.get("tags"):
            self._add_tags_from_names(term.id, tags_str.split(";"))

    def _add_tags_from_names(self, term_id: uuid.UUID, tag_names: list[str]) -> None:
        """タグ名リストから用語にタグを追加する（ヘルパーメソッド）

        Args:
            term_id: 用語のID
            tag_names: タグ名のリスト
        """
        for tag_name in tag_names:
            if not tag_name.strip():
                continue
            # タグを検索または作成
            try:
                tag = self.tag_repo.get_by_name(tag_name.strip())
            except Exception:
                from models import TagCreate

                tag = self.tag_repo.create(TagCreate(name=tag_name.strip()))
            if tag.id:
                self.term_repo.add_tag(term_id, tag.id)

    @handle_service_errors(SERVICE_NAME, "インポート", TerminologyServiceError)
    def import_from_csv(self, file_path: Path) -> ImportResult:
        """CSVファイルから用語をインポートする

        CSV形式: key,title,description,status,source_url,synonyms(;区切り),tags(;区切り)

        Args:
            file_path: CSVファイルのパス

        Returns:
            ImportResult: インポート結果

        Raises:
            TerminologyServiceError: インポートに失敗した場合
        """
        success_count = 0
        failed_count = 0
        errors: list[str] = []

        with file_path.open(encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row_num, row in enumerate(reader, start=2):  # ヘッダー行を1行目とする
                try:
                    self._import_term_from_csv_row(row)
                    success_count += 1
                except Exception as e:
                    failed_count += 1
                    errors.append(f"行 {row_num}: {e!s}")
                    logger.warning(f"行 {row_num} のインポートに失敗しました: {e}")

        logger.info(f"CSVインポート完了: 成功 {success_count} 件, 失敗 {failed_count} 件")
        return ImportResult(success_count=success_count, failed_count=failed_count, errors=errors)

    @handle_service_errors(SERVICE_NAME, "インポート", TerminologyServiceError)
    def import_from_json(self, file_path: Path) -> ImportResult:
        """JSONファイルから用語をインポートする

        JSON形式:
        [
            {
                "key": "...",
                "title": "...",
                "description": "...",
                "status": "draft|approved|deprecated",
                "source_url": "...",
                "synonyms": ["...", "..."],
                "tags": ["...", "..."]
            },
            ...
        ]

        Args:
            file_path: JSONファイルのパス

        Returns:
            ImportResult: インポート結果

        Raises:
            TerminologyServiceError: インポートに失敗した場合
        """
        success_count = 0
        failed_count = 0
        errors: list[str] = []

        with file_path.open(encoding="utf-8") as f:
            data = json.load(f)

        for idx, item in enumerate(data, start=1):
            try:
                # 用語作成
                term_data = TermCreate(
                    key=item["key"],
                    title=item["title"],
                    description=item.get("description"),
                    status=TermStatus(item.get("status", "draft")),
                    source_url=item.get("source_url"),
                )
                term = self.term_repo.create(term_data)

                # 同義語追加
                if term.id:
                    for synonym in item.get("synonyms", []):
                        self.term_repo.add_synonym(term.id, synonym)

                    # タグ追加
                    for tag_name in item.get("tags", []):
                        # タグを検索または作成
                        try:
                            tag = self.tag_repo.get_by_name(tag_name)
                        except Exception:
                            from models import TagCreate

                            tag = self.tag_repo.create(TagCreate(name=tag_name))
                        if tag.id:
                            self.term_repo.add_tag(term.id, tag.id)

                success_count += 1
            except Exception as e:
                failed_count += 1
                errors.append(f"項目 {idx}: {e!s}")
                logger.warning(f"項目 {idx} のインポートに失敗しました: {e}")

        logger.info(f"JSONインポート完了: 成功 {success_count} 件, 失敗 {failed_count} 件")
        return ImportResult(success_count=success_count, failed_count=failed_count, errors=errors)

    @handle_service_errors(SERVICE_NAME, "エクスポート", TerminologyServiceError)
    def export_to_csv(self, file_path: Path, *, status_filter: TermStatus | None = None) -> int:
        """用語をCSVファイルにエクスポートする

        Args:
            file_path: 出力先CSVファイルのパス
            status_filter: エクスポートする用語のステータスフィルタ

        Returns:
            int: エクスポートした用語の件数

        Raises:
            TerminologyServiceError: エクスポートに失敗した場合
        """
        terms = self.term_repo.search(status=status_filter, with_details=True)

        with file_path.open("w", encoding="utf-8", newline="") as f:
            fieldnames = ["key", "title", "description", "status", "source_url", "synonyms", "tags"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for term in terms:
                writer.writerow(
                    {
                        "key": term.key,
                        "title": term.title,
                        "description": term.description or "",
                        "status": term.status.value,
                        "source_url": term.source_url or "",
                        "synonyms": ";".join(s.text for s in term.synonyms),
                        "tags": ";".join(t.name for t in term.tags),
                    }
                )

        logger.info(f"{len(terms)} 件の用語をCSVエクスポートしました: {file_path}")
        return len(terms)

    @handle_service_errors(SERVICE_NAME, "エクスポート", TerminologyServiceError)
    def export_to_json(self, file_path: Path, *, status_filter: TermStatus | None = None) -> int:
        """用語をJSONファイルにエクスポートする

        Args:
            file_path: 出力先JSONファイルのパス
            status_filter: エクスポートする用語のステータスフィルタ

        Returns:
            int: エクスポートした用語の件数

        Raises:
            TerminologyServiceError: エクスポートに失敗した場合
        """
        terms = self.term_repo.search(status=status_filter, with_details=True)

        data = [
            {
                "key": term.key,
                "title": term.title,
                "description": term.description,
                "status": term.status.value,
                "source_url": term.source_url,
                "synonyms": [s.text for s in term.synonyms],
                "tags": [t.name for t in term.tags],
            }
            for term in terms
        ]

        with file_path.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        logger.info(f"{len(terms)} 件の用語をJSONエクスポートしました: {file_path}")
        return len(terms)

    # ==============================================================================
    # Agent API
    # ==============================================================================

    @handle_service_errors(SERVICE_NAME, "エージェント用取得", TerminologyServiceError)
    def for_agents_top_k(
        self,
        query: str | None = None,
        *,
        tags: list[uuid.UUID] | None = None,
        exclude_tags: list[uuid.UUID] | None = None,
        k: int = 8,
    ) -> list[TermForPrompt]:
        """エージェント用にtop-k件の用語を取得する

        Args:
            query: 検索クエリ（Noneの場合は承認済み用語を優先）
            tags: 含めるタグのIDリスト
            exclude_tags: 除外するタグのIDリスト
            k: 取得する最大件数

        Returns:
            list[TermForPrompt]: エージェント用の用語データリスト

        Raises:
            TerminologyServiceError: 取得に失敗した場合
        """
        # 承認済み用語を優先的に取得
        terms = self.term_repo.search(query=query, tags=tags, status=TermStatus.APPROVED, with_details=True)

        # 除外タグでフィルタリング
        if exclude_tags:
            terms = [term for term in terms if not any(tag.id in exclude_tags for tag in term.tags)]

        # 件数が不足している場合は草案も含める
        if len(terms) < k:
            draft_terms = self.term_repo.search(query=query, tags=tags, status=TermStatus.DRAFT, with_details=True)
            if exclude_tags:
                draft_terms = [term for term in draft_terms if not any(tag.id in exclude_tags for tag in term.tags)]
            terms.extend(draft_terms)

        # top-k件を取得
        terms = terms[:k]

        # TermForPromptに変換
        result = [
            TermForPrompt(
                key=term.key,
                title=term.title,
                description=term.description,
                synonyms=[s.text for s in term.synonyms],
            )
            for term in terms
        ]

        logger.debug(f"エージェント用に {len(result)} 件の用語を取得しました。")
        return result
