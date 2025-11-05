# Design: アプリケーション層検索（横断）

<!-- OPENSPEC:START -->

## Context

- 既存: Repository 層に Memo/Task/Project/Tag/Term の検索 API が一部存在（Task は title のみ、Memo は title/content、Project は title、Tag は name、Term は高度検索）。
- 既存: Service 層に Memo/Tag/Term の検索あり。Task/Project は未整備。
- 課題: Application 層で検索が未公開/未統一のため、View/CLI/Agent 側に実装の重複と例外/セッション管理の漏れが発生。

## Goals / Non-Goals

- Goals: Application API の統一（`search(...)`）、最小の検索（部分一致・大文字小文字無視）、with_details 対応（可能な範囲）。
- Non-Goals: 高度な全文検索・ランキング、ページング/ソート最適化、インデックス設計。

## Decisions

- 共通 API 形：
  - Memo/Task: `search(query: str, with_details: bool=False) -> list[ReadModel]`
  - Project/Tag: `search(query: str) -> list[ReadModel]`（with_details は将来拡張）
  - Term: `search(query: str | None, tags: list[UUID] | None, status: TermStatus | None, include_synonyms: bool=True)` を公開（Service を委譲）
- Task の検索は Repository に `search_by_description` を追加し、Service で title/description の結果を統合（ID で重複除去）。
- 例外方針：ヒットなしは空配列（NotFound を上位で握りつぶすのではなく、Repository/Service は正常系として空リストを返す）。

## Risks / Trade-offs

- LIKE 検索のためパフォーマンスはデータ量依存。必要になればインデックスや検索基盤導入を別提案で検討。
- with_details によるロード増は既存の eager loading を活用して抑制。

## Migration Plan

1. Repository 追加（Task の `search_by_description`）。
2. Service 追加（Task `search_tasks`、Project `search_projects`）。
3. Application 追加（Memo/Task/Project/Tag/Term の検索公開）。
4. テスト追加とドキュメント更新。

## Open Questions

- 複合条件（AND/OR）やソート、ページングの要否とパラメータ設計（将来提案）。

<!-- OPENSPEC:END -->