# routing-and-navigation Specification

## Purpose
TBD - created by archiving change organize-view-layer. Update Purpose after archive.
## Requirements
### Requirement: Routing Deferred Notice

本変更ではルーティング関連要件（ルート解決、中央マッピング、パラメータパース、戻るナビゲーション、AppBar 方針）は扱わない (MUST)。後続の専用変更で再定義されるまで、これらは implement しないことを明示しなければならない (MUST)。

#### Scenario: Reviewer Confirms Defer

- GIVEN organize-view-layer 変更のレビュー
- WHEN スコープを確認
- THEN ルーティング要件が明確に deferred/out-of-scope と記載されている

