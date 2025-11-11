# Change: organize-view-layer

<!-- OPENSPEC:START -->

## Summary

Kage の Flet ビュー層に関して、ページごとのディレクトリ構成、ロジック層との結線方針、コンポーネントの作り方、状態管理の境界を標準化する変更です（ルーティングの基本は本変更では扱いません）。既存の `src/views` は最低限の形を前提としており、保守性・単一責任・テスト容易性を高めるための最小だが具体的なルールを追加します。

## Motivation

- 画面実装のばらつきにより、責務境界（View vs Application/Service）が曖昧
- コンポーネント再利用・テストが難しい
- ルーティング/状態/エラーハンドリングの共通方針が不明確

## Scope

- Flet View 層全般（`src/views/**`）
- Application 層（`src/logic/application/**`）への接続規約
- 既存コードとの互換: 破壊的変更は避け、まずは規約の追加とスケルトン整備を対象
- NOTE: ルータ実装（`src/router.py`, `src/router_config.py`）およびテストコード追加は本変更では扱わない（他変更へ委譲）

## Out of Scope

- 個別画面の詳細 UI デザイン（コンポーネントの見た目・文言）
- 複雑なドラッグ＆ドロップや高度なボード仮想化の実装
- ルーティング処理の具体的な実装（router / router_config の編集、ルートパラメータパース）
- テストコードの新規作成（本提案は仕様定義のみを対象）

## Related

- `openspec/views-flet-proposal.md`（Flet UI 再実装の方向性）
- `src/logic/application/memo_application_service.py`（Application Service の現状 API 例）

## Acceptance Criteria

- 新規ビュー/コンポーネントの配置と命名が統一されている
- View は Application Service を直接または Provider 経由で呼び出し、ビジネスロジックを含まない
- コンポーネントは props/state 単位で分割され、テスタブル
- 共通 BaseView 契約（`base-view-contract` spec）が存在し、エラー通知/ローディング/ライフサイクル/cleanup が統一されている（ルーティング挙動自体は他変更で扱う）
- 仕様は spec 形式（ADDED 要件 + シナリオ）で定義され、`tasks.md` の検証手順で確認可能
- router 実装とテストコードは含まれていないことが明確に記されている

<!-- OPENSPEC:END -->
