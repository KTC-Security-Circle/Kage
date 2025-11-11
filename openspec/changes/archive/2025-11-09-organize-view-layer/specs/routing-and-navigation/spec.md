# Specification: routing-and-navigation (OUT OF SCOPE)

<!-- OPENSPEC:START -->

この仕様は当初 organize-view-layer 変更に含まれていたが、ユーザー指示により当該変更のスコープから除外された。以下の要件は本変更では実装も検証も行わない。後続の専用変更（例: routing-refactor など）で再提示・再検証される予定。

## ADDED Requirements

### Requirement: Routing Deferred Notice

本変更ではルーティング関連要件（ルート解決、中央マッピング、パラメータパース、戻るナビゲーション、AppBar 方針）は扱わない (MUST)。後続の専用変更で再定義されるまで、これらは implement しないことを明示しなければならない (MUST)。

#### Scenario: Reviewer Confirms Defer

- GIVEN organize-view-layer 変更のレビュー
- WHEN スコープを確認
- THEN ルーティング要件が明確に deferred/out-of-scope と記載されている

## REMOVED Requirements

(なし)

## MODIFIED Requirements

(なし)

See also: views-structure, base-view-contract, views-logic-binding (routing は後続変更)

<!-- OPENSPEC:END -->
