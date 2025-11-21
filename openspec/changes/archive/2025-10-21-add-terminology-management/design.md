# Design: Terminology Management

<!-- OPENSPEC:START -->

## Architecture Overview

- Domain: Terminology (Term, Synonym, Tag, Source)
- Persistence: SQLite (SQLModel/SQLAlchemy ベースを想定)。将来: Vector Index（FAISS/Chroma など）
- Services: 用語 CRUD、検索、同義語展開、タグフィルタ、バルク I/O
- Integration: UnitOfWork に TerminologyRepository を追加。DI コンテナから Service を取得。
- UI: 今回はスコープ外（将来提案で Flet 画面を追加）。

## Data Model (v1)

- Term(id, key, title, description, status, source_url, created_at, updated_at)
- Synonym(id, term_id, text)
- Tag: 既存 `tags` テーブルを使用（新規テーブル作成はしない）
- TermTag(term_id, tag_id) 中間テーブルで `terms` と `tags` を関連付け

拡張余地: TermRevision（履歴）、Locale（多言語）、Source（出典の型拡張）

## Search Strategy

- v1: LIKE/正規化（大文字小文字・全角半角・記号除去） + 同義語展開
- v2: SQLite FTS 導入の検討（パッケージ互換性を要確認）
- v3: VectorIndex アダプター導入（AbstractVectorIndex + LocalFaissIndex 実装）

## Vector Index Abstraction (future)

```text
VectorIndex
  - build(entries: list[EmbeddingItem]) -> None
  - add(items) / remove(ids) / search(query_embedding, top_k, filters)
  - persist(path) / load(path)
```

Service 側はこれに依存し、未設定時はフォールバックしてキーワード検索。

## API Surface (Service)

- create_term(input) -> Term
- update_term(id, patch) -> Term
- delete_term(id, force=False) -> bool
- get_term(id) -> Term
- list_terms(filter, pagination) -> Page[Term]
- import_terms(file, format) -> ImportResult
- export_terms(filter, format) -> bytes
- search(query, top_k=20, tags=None, include_synonyms=True) -> list[Term]
- for_agents.top_k(query, tags=None, k=8) -> list[TermForPrompt]

## Error Handling

- NotFound, AlreadyExists(key のユニーク), ValidationError（必須欠落/長さ制限）
- ImportError（フォーマット不正）

## Migration

- Alembic: terms, synonyms, tags, term_tags の 4 テーブルを追加。

## UI Outline (Flet)

- 本変更では未対応。将来の UI 提案で具体化。

<!-- OPENSPEC:END -->
