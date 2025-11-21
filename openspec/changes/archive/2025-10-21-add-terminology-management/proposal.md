# Proposal: 社内用語管理システムの追加 (Terminology Management)

<!-- OPENSPEC:START -->

## Why

Kage に社内固有の用語・略語・同義語・定義・参照情報を一元管理し、
ユーザーの検索/参照体験と、LLM へのコンテキスト提供（RAG／プロンプト補強）に活用したい。
現在はこの情報が分散し、重複・表記揺れ・検索性の低下が発生している。

## Summary

まずは SQLite を唯一のソース・オブ・トゥルースとして用語データを保存・CRUD 可能にし、
軽量な全文検索（FTS）での検索を提供する。将来、LLM 向けの関連語検索品質を高めるため、
オプションの埋め込みインデックス（ローカル Vector Index）を追加可能にする二段構えとする。
これにより最小実装で価値を提供しつつ、必要時にベクトル検索へ拡張できる。

## Goals

- 用語の CRUD、タグ/同義語/出典/説明/ステータス（草案/確定）管理
- インポート/エクスポート（CSV/JSON）
- 検索（キーワード/タグ/同義語/部分一致、将来的にベクトル類似も）
- LLM 連携のための取得 API（top-k 抽出、フィルタ、プロンプト整形）

## Non-goals

- 初期段階での外部マネージド Vector DB 導入（Qdrant/Weaviate/Supabase Vector 等）は対象外
- マルチユーザー強認証/承認ワークフロー（必要になった時点で別提案）

## Scope

- 新規: models/repositories/services（Terminology）
- 既存: 設定/DI/UnitOfWork へ用語リソースを統合、既存のタグテーブル (`tags`) を再利用
- エージェント: 取得 API を経由して用語をプロンプトへ注入
- 除外: 今回は UI 実装はスコープ外（別提案/PR）

## What Changes

- データモデル: Term, Synonym, TermTag（中間; 参照先は既存の `tags` テーブル）、Source（出典; 必要なら）、TermRevision（任意）
- Repository/Service: CRUD、検索、バルク I/O
- 設定: 用語管理の有効化、埋め込みインデックス（オプション）設定

## Design Direction（選定）

- 初期は SQLite + FTS (または LIKE/正規化検索) を採用。
- ベクトル検索は抽象インターフェースを準備し、後追いでローカル実装（例: FAISS/Chroma）をプラグインとして追加可能に。
- SQLite を唯一の正とし、ベクトルは誘導インデックス（再構築可能）として扱う。
- タグは既存の `tags` テーブルを再利用し、新規テーブルは作成しない（用語との関連のみ中間テーブルで表現）。

## Trade-offs: SQLite vs Vector DB（結論）

- SQLite の利点: 依存最小/配布容易/トランザクション一貫性/移行容易。UI 開発のスピードに寄与。
- Vector DB の利点: 類似検索の品質向上、大規模語彙にスケール。ただし導入/運用コストが増す。
- 結論: まず SQLite で実装し、品質/規模要求が高まった段階でローカル Vector Index を追加（プラグイン化）。

## Risks & Mitigations

- 検索品質: 初期はキーワード検索のため、あいまい一致/同義語展開を実装し品質を補完。
- 将来のスケール: Vector 層を抽象化し、段階導入可能にすることでリスク低減。

## Success Criteria

- 用語 CRUD と検索が UI/CLI/Service 経由で完了する
- インポート/エクスポートで 100 件程度のデータを往復できる
- エージェントは API から top-k 用語を取得し、プロンプトに注入できる

## References

- openspec/specs 既存の構成
- src/logic の Repository/Service/UnitOfWork パターン

<!-- OPENSPEC:END -->
