# 用語管理機能 CRUD実装引継ぎドキュメント

## 概要

用語管理のUIは完成していますが、データベース連携のロジック層が未実装です。
このドキュメントは、ロジック担当者がCRUD機能を実装するためのガイドです。

## 実装状況

### ✅ 完成しているもの

- **UI層（Views）**: 完全実装済み
  - 用語一覧表示（2カラムレイアウト）
  - ステータスタブ（承認済み/草案/非推奨）
  - 検索機能（UI側の実装）
  - 詳細パネル
  - **作成ダイアログ** ← NEW!
    - フォーム入力（キー、タイトル、説明、ステータス、出典URL、同義語）
    - バリデーション（必須チェック、文字数制限、URL形式）
    - エラー表示

- **データモデル**: 完全定義済み
  - `Term`: 用語テーブル（id, key, title, description, status, source_url）
  - `Synonym`: 同義語テーブル（id, text, term_id）
  - `TermCreate`, `TermUpdate`, `TermRead`: DTOモデル
  - `TermStatus` enum: DRAFT, APPROVED, DEPRECATED

- **データベース**: マイグレーション適用済み
  - `terms` テーブル
  - `synonyms` テーブル（CASCADE DELETE）
  - `term_tag` リンクテーブル（多対多）

- **State/Controller/Presenter**: 骨格実装済み
  - 現在はサンプルデータで動作中

### ❌ 未実装（これから実装が必要）

1. **ApplicationService 層**
   - `TermApplicationService`
   - `SynonymApplicationService`（または統合）

2. **Repository 層**
   - `TermRepository`
   - `SynonymRepository`

3. **Controller への統合**
   - `create_term()`, `update_term()`, `delete_term()` メソッド

4. **View からの呼び出し**
   - 非同期実行とエラーハンドリング

## 実装手順

### ステップ1: Repository 層の実装

#### ファイル: `src/logic/repositories/term_repository.py`

```python
"""用語リポジトリ。"""

from uuid import UUID

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from models import Term, TermCreate, TermStatus, TermUpdate


class TermRepository:
    """用語の永続化を担当するリポジトリ。"""

    def __init__(self, session: AsyncSession):
        """Initialize term repository.

        Args:
            session: 非同期データベースセッション
        """
        self._session = session

    async def create(self, data: TermCreate) -> Term:
        """用語を作成する。

        Args:
            data: 作成データ

        Returns:
            作成された用語

        Raises:
            IntegrityError: キーの重複など
        """
        term = Term.model_validate(data)
        self._session.add(term)
        await self._session.commit()
        await self._session.refresh(term)
        return term

    async def find_by_id(self, term_id: UUID) -> Term | None:
        """IDで用語を取得する。

        Args:
            term_id: 用語ID

        Returns:
            用語（存在しない場合はNone）
        """
        result = await self._session.execute(
            select(Term).where(Term.id == term_id)
        )
        return result.scalar_one_or_none()

    async def find_by_key(self, key: str) -> Term | None:
        """キーで用語を取得する（一意性チェック用）。

        Args:
            key: 用語キー

        Returns:
            用語（存在しない場合はNone）
        """
        result = await self._session.execute(
            select(Term).where(Term.key == key)
        )
        return result.scalar_one_or_none()

    async def list_all(self, status: TermStatus | None = None) -> list[Term]:
        """用語一覧を取得する。

        Args:
            status: フィルタするステータス（Noneの場合は全件）

        Returns:
            用語のリスト
        """
        query = select(Term)
        if status:
            query = query.where(Term.status == status)
        result = await self._session.execute(query)
        return list(result.scalars().all())

    async def update(self, term_id: UUID, data: TermUpdate) -> Term | None:
        """用語を更新する。

        Args:
            term_id: 更新対象の用語ID
            data: 更新データ

        Returns:
            更新された用語（存在しない場合はNone）
        """
        term = await self.find_by_id(term_id)
        if not term:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(term, key, value)

        await self._session.commit()
        await self._session.refresh(term)
        return term

    async def delete(self, term_id: UUID) -> bool:
        """用語を削除する。

        Args:
            term_id: 削除対象の用語ID

        Returns:
            削除成功時はTrue
        """
        term = await self.find_by_id(term_id)
        if not term:
            return False

        await self._session.delete(term)
        await self._session.commit()
        return True
```

#### ファイル: `src/logic/repositories/synonym_repository.py`

```python
"""同義語リポジトリ。"""

from uuid import UUID

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from models import Synonym, SynonymCreate


class SynonymRepository:
    """同義語の永続化を担当するリポジトリ。"""

    def __init__(self, session: AsyncSession):
        """Initialize synonym repository.

        Args:
            session: 非同期データベースセッション
        """
        self._session = session

    async def create(self, data: SynonymCreate) -> Synonym:
        """同義語を作成する。

        Args:
            data: 作成データ

        Returns:
            作成された同義語
        """
        synonym = Synonym.model_validate(data)
        self._session.add(synonym)
        await self._session.commit()
        await self._session.refresh(synonym)
        return synonym

    async def list_by_term(self, term_id: UUID) -> list[Synonym]:
        """特定の用語に紐づく同義語を取得する。

        Args:
            term_id: 用語ID

        Returns:
            同義語のリスト
        """
        result = await self._session.execute(
            select(Synonym).where(Synonym.term_id == term_id)
        )
        return list(result.scalars().all())

    async def delete_by_term(self, term_id: UUID) -> int:
        """特定の用語に紐づく同義語を全削除する。

        Args:
            term_id: 用語ID

        Returns:
            削除した件数
        """
        synonyms = await self.list_by_term(term_id)
        count = len(synonyms)
        for synonym in synonyms:
            await self._session.delete(synonym)
        await self._session.commit()
        return count
```

### ステップ2: ApplicationService 層の実装

#### ファイル: `src/logic/application/term_application_service.py`

```python
"""用語管理のApplicationService。"""

from uuid import UUID

from loguru import logger

from models import (
    Synonym,
    SynonymCreate,
    SynonymRead,
    Term,
    TermCreate,
    TermRead,
    TermStatus,
    TermUpdate,
)

from ..repositories.synonym_repository import SynonymRepository
from ..repositories.term_repository import TermRepository


class TermApplicationService:
    """用語管理のビジネスロジックを提供する。

    Repository と協調してCRUD操作とバリデーションを実行します。
    """

    def __init__(
        self,
        term_repo: TermRepository,
        synonym_repo: SynonymRepository,
    ):
        """Initialize term application service.

        Args:
            term_repo: 用語リポジトリ
            synonym_repo: 同義語リポジトリ
        """
        self._term_repo = term_repo
        self._synonym_repo = synonym_repo

    async def create_term(self, data: TermCreate) -> TermRead:
        """用語を作成する。

        Args:
            data: 作成データ

        Returns:
            作成された用語

        Raises:
            ValueError: キーが既に存在する場合
        """
        # キーの一意性チェック
        existing = await self._term_repo.find_by_key(data.key)
        if existing:
            logger.warning(f"Duplicate key attempted: {data.key}")
            raise ValueError(f"キー '{data.key}' は既に使用されています")

        # 用語を作成
        term = await self._term_repo.create(data)
        logger.info(f"Created term: {term.key} (ID: {term.id})")
        return TermRead.model_validate(term)

    async def create_synonyms(
        self,
        term_id: UUID,
        synonyms: list[str],
    ) -> list[SynonymRead]:
        """同義語を一括作成する。

        Args:
            term_id: 用語ID
            synonyms: 同義語のテキストリスト

        Returns:
            作成された同義語のリスト
        """
        created = []
        for text in synonyms:
            synonym_data = SynonymCreate(text=text, term_id=term_id)
            synonym = await self._synonym_repo.create(synonym_data)
            created.append(SynonymRead.model_validate(synonym))

        logger.info(f"Created {len(created)} synonyms for term {term_id}")
        return created

    async def update_term(self, term_id: UUID, data: TermUpdate) -> TermRead:
        """用語を更新する。

        Args:
            term_id: 更新対象の用語ID
            data: 更新データ

        Returns:
            更新された用語

        Raises:
            ValueError: 用語が存在しない場合
        """
        term = await self._term_repo.update(term_id, data)
        if not term:
            logger.warning(f"Term not found for update: {term_id}")
            raise ValueError(f"用語 ID {term_id} が見つかりません")

        logger.info(f"Updated term: {term.key} (ID: {term.id})")
        return TermRead.model_validate(term)

    async def delete_term(self, term_id: UUID) -> bool:
        """用語を削除する（同義語もCASCADE削除）。

        Args:
            term_id: 削除対象の用語ID

        Returns:
            削除成功時はTrue

        Raises:
            ValueError: 用語が存在しない場合
        """
        success = await self._term_repo.delete(term_id)
        if not success:
            logger.warning(f"Term not found for deletion: {term_id}")
            raise ValueError(f"用語 ID {term_id} が見つかりません")

        logger.info(f"Deleted term: {term_id}")
        return success

    async def get_term_by_id(self, term_id: UUID) -> TermRead | None:
        """IDで用語を取得する。

        Args:
            term_id: 用語ID

        Returns:
            用語（存在しない場合はNone）
        """
        term = await self._term_repo.find_by_id(term_id)
        return TermRead.model_validate(term) if term else None

    async def list_terms(
        self,
        status: TermStatus | None = None,
    ) -> list[TermRead]:
        """用語一覧を取得する（オプションでステータスフィルタ）。

        Args:
            status: フィルタするステータス（Noneの場合は全件）

        Returns:
            用語のリスト
        """
        terms = await self._term_repo.list_all(status=status)
        return [TermRead.model_validate(t) for t in terms]

    async def get_synonyms(self, term_id: UUID) -> list[SynonymRead]:
        """用語に紐づく同義語を取得する。

        Args:
            term_id: 用語ID

        Returns:
            同義語のリスト
        """
        synonyms = await self._synonym_repo.list_by_term(term_id)
        return [SynonymRead.model_validate(s) for s in synonyms]

    async def update_synonyms(
        self,
        term_id: UUID,
        new_synonyms: list[str],
    ) -> list[SynonymRead]:
        """用語の同義語を更新する（全削除 + 再作成）。

        Args:
            term_id: 用語ID
            new_synonyms: 新しい同義語のリスト

        Returns:
            作成された同義語のリスト
        """
        # 既存の同義語を削除
        deleted_count = await self._synonym_repo.delete_by_term(term_id)
        logger.debug(f"Deleted {deleted_count} synonyms for term {term_id}")

        # 新しい同義語を作成
        return await self.create_synonyms(term_id, new_synonyms)
```

### ステップ3: Controller への統合

`src/views/terms/controller.py` の TODO セクションに以下のメソッドを実装してください。

```python
async def create_term(self, form_data: dict[str, object]) -> None:
    """新しい用語を作成する。

    Args:
        form_data: ダイアログから受け取ったフォームデータ

    Raises:
        ValueError: バリデーションエラー
    """
    # TermCreate に変換
    term_create = TermCreate(
        key=str(form_data["key"]),
        title=str(form_data["title"]),
        description=str(form_data.get("description")) if form_data.get("description") else None,
        status=TermStatus(str(form_data["status"])),
        source_url=str(form_data.get("source_url")) if form_data.get("source_url") else None,
    )

    # ApplicationService で作成
    created_term = await self.app_service.create_term(term_create)

    # 同義語を作成
    synonyms = form_data.get("synonyms", [])
    if synonyms and isinstance(synonyms, list):
        await self.app_service.create_synonyms(created_term.id, synonyms)

    # State を更新（全件再読み込み）
    await self.load_initial_terms()

    logger.info(f"Created term: {created_term.key} (ID: {created_term.id})")
```

**注意**: 
- `app_service` を Controller の初期化時に注入する必要があります
- `load_initial_terms()` を非同期化する必要があります（現在は同期）

### ステップ4: View からの呼び出し

`src/views/terms/view.py` の `_handle_dialog_create` メソッドを以下のように更新してください。

```python
async def _handle_dialog_create(self, form_data: dict[str, object]) -> None:
    """ダイアログからの用語作成をハンドリングする。

    Args:
        form_data: フォームデータ
    """
    try:
        # Controller で作成実行
        await self.controller.create_term(form_data)

        # ダイアログを閉じる
        self._close_create_dialog()

        # 成功メッセージ
        key = form_data.get("key", "")
        self.show_success_snackbar(f"用語 '{key}' を作成しました")

        # リスト更新
        self._refresh_term_list()
        self._refresh_status_tabs()

    except ValueError as e:
        # バリデーションエラー
        self.show_error_snackbar(self.page, str(e))

    except Exception as e:
        # その他のエラー
        logger.error(f"Failed to create term: {e}")
        self.handle_exception_with_snackbar(
            self.page,
            e,
            "用語の作成に失敗しました",
        )
```

### ステップ5: 依存性注入の設定

`src/logic/container.py` に TermApplicationService を追加してください。

```python
@dataclass
class ApplicationServices:
    """全ApplicationServiceのコンテナ。"""

    # ... 既存のサービス ...

    # 追加
    term_service: TermApplicationService
    synonym_service: SynonymRepository  # 必要に応じて
```

## テスト実装

### ユニットテスト

#### `tests/logic/repositories/test_term_repository.py`

```python
"""TermRepository のテスト。"""

import pytest
from sqlmodel.ext.asyncio.session import AsyncSession

from logic.repositories.term_repository import TermRepository
from models import TermCreate, TermStatus


@pytest.mark.asyncio
async def test_create_term(db_session: AsyncSession):
    """用語の作成をテストする。"""
    repo = TermRepository(db_session)

    data = TermCreate(
        key="TEST",
        title="テスト用語",
        description="これはテストです",
        status=TermStatus.DRAFT,
    )

    term = await repo.create(data)

    assert term.id is not None
    assert term.key == "TEST"
    assert term.title == "テスト用語"


@pytest.mark.asyncio
async def test_find_by_key(db_session: AsyncSession):
    """キーで用語を取得するテスト。"""
    repo = TermRepository(db_session)

    # 作成
    data = TermCreate(key="UNIQUE", title="ユニーク")
    await repo.create(data)

    # 取得
    found = await repo.find_by_key("UNIQUE")

    assert found is not None
    assert found.key == "UNIQUE"


@pytest.mark.asyncio
async def test_duplicate_key_raises_error(db_session: AsyncSession):
    """重複キーがエラーを発生させることをテストする。"""
    repo = TermRepository(db_session)

    data = TermCreate(key="DUP", title="重複テスト")
    await repo.create(data)

    # 同じキーで再作成
    with pytest.raises(Exception):  # IntegrityError
        await repo.create(data)
```

#### `tests/logic/application/test_term_application_service.py`

```python
"""TermApplicationService のテスト。"""

import pytest
from sqlmodel.ext.asyncio.session import AsyncSession

from logic.application.term_application_service import TermApplicationService
from logic.repositories.synonym_repository import SynonymRepository
from logic.repositories.term_repository import TermRepository
from models import TermCreate, TermStatus


@pytest.mark.asyncio
async def test_create_term_with_validation(db_session: AsyncSession):
    """用語作成のバリデーションをテストする。"""
    term_repo = TermRepository(db_session)
    synonym_repo = SynonymRepository(db_session)
    service = TermApplicationService(term_repo, synonym_repo)

    data = TermCreate(
        key="API",
        title="Application Programming Interface",
        status=TermStatus.DRAFT,
    )

    term = await service.create_term(data)

    assert term.id is not None
    assert term.key == "API"


@pytest.mark.asyncio
async def test_duplicate_key_validation(db_session: AsyncSession):
    """重複キーのバリデーションをテストする。"""
    term_repo = TermRepository(db_session)
    synonym_repo = SynonymRepository(db_session)
    service = TermApplicationService(term_repo, synonym_repo)

    data = TermCreate(key="DUP", title="重複")
    await service.create_term(data)

    # 同じキーで再作成 -> ValueError
    with pytest.raises(ValueError, match="既に使用されています"):
        await service.create_term(data)


@pytest.mark.asyncio
async def test_create_with_synonyms(db_session: AsyncSession):
    """同義語付き用語作成をテストする。"""
    term_repo = TermRepository(db_session)
    synonym_repo = SynonymRepository(db_session)
    service = TermApplicationService(term_repo, synonym_repo)

    # 用語作成
    term_data = TermCreate(key="LLM", title="Large Language Model")
    term = await service.create_term(term_data)

    # 同義語作成
    synonyms = await service.create_synonyms(
        term.id,
        ["大規模言語モデル", "言語モデル"],
    )

    assert len(synonyms) == 2
    assert synonyms[0].text == "大規模言語モデル"
```

## チェックリスト

実装完了時に以下を確認してください。

- [ ] TermRepository の実装とテスト
- [ ] SynonymRepository の実装とテスト
- [ ] TermApplicationService の実装とテスト
- [ ] Controller への統合
- [ ] View からの非同期呼び出し
- [ ] 依存性注入の設定（container.py）
- [ ] エラーハンドリング（ValueError, IntegrityError）
- [ ] ログ出力（logger.info/warning/error）
- [ ] マイグレーション確認（alembic upgrade head）
- [ ] 実際の動作確認（Web UI でのCRUD操作）

## 追加資料

### 関連ファイル一覧

```
src/
├── models/__init__.py                     # Term, TermCreate, TermUpdate, TermRead
├── logic/
│   ├── application/
│   │   └── term_application_service.py    # ← 実装必要
│   └── repositories/
│       ├── term_repository.py             # ← 実装必要
│       └── synonym_repository.py          # ← 実装必要
└── views/terms/
    ├── controller.py                       # ← TODOコメント確認
    ├── view.py                            # ← TODOコメント確認
    └── components/
        └── create_term_dialog.py          # ← 完成済み

tests/
├── logic/
│   ├── application/
│   │   └── test_term_application_service.py  # ← 実装必要
│   └── repositories/
│       ├── test_term_repository.py           # ← 実装必要
│       └── test_synonym_repository.py        # ← 実装必要
```

### データベーススキーマ

```sql
-- terms テーブル
CREATE TABLE terms (
    id UUID PRIMARY KEY,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    key VARCHAR(100) UNIQUE NOT NULL,
    title VARCHAR(200) NOT NULL,
    description VARCHAR(2000),
    status VARCHAR(20) NOT NULL,  -- 'draft', 'approved', 'deprecated'
    source_url VARCHAR(500)
);

-- synonyms テーブル
CREATE TABLE synonyms (
    id UUID PRIMARY KEY,
    text VARCHAR(200) NOT NULL,
    term_id UUID NOT NULL REFERENCES terms(id) ON DELETE CASCADE
);

-- term_tag リンクテーブル（多対多）
CREATE TABLE term_tag (
    term_id UUID NOT NULL REFERENCES terms(id) ON DELETE CASCADE,
    tag_id UUID NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
    PRIMARY KEY (term_id, tag_id)
);
```

## 質問・サポート

実装中に不明点があれば、以下を確認してください：

1. `src/views/terms/controller.py` の詳細なTODOコメント
2. `src/views/terms/view.py` の TODOコメント
3. 既存の memos 機能の実装（参考になります）
4. `.github/copilot-instructions.md` のコーディング規約

---

**担当者**: ロジック層担当者
**優先度**: 高
**見積もり**: 2-3日
**ブロッカー**: なし（必要なモデルとマイグレーションは完了済み）
