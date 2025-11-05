# Spec: memo-search

## ADDED Requirements

### Requirement: メモ検索 API（Application 層）

- Application 層は `search(query: str, with_details: bool=False)` を公開しなければならない (MUST)。
- 検索はタイトル/内容の部分一致（大文字小文字無視）を対象としなければならない (MUST)。
- 結果は `MemoRead` の配列を返し、ヒットなしは空配列としなければならない (MUST)。
- `with_details=True` の場合、タグ/関連タスク等の関連情報を含めて返さなければならない (MUST)。
- ページング/ソートは将来拡張とし、今回の最小実装では含めない (SHOULD)。

#### Scenario: タイトルで前方/中間一致

- **WHEN** query="proj" を指定して検索
- **THEN** タイトルに "proj" を含むメモが返る（大文字小文字無視）

#### Scenario: 内容で部分一致

- **WHEN** query="design doc" を指定して検索
- **THEN** 内容に "design doc" を含むメモが返る

#### Scenario: ヒットなしは空配列

- **WHEN** query がどのメモにも一致しない
- **THEN** 空配列を返す

#### Scenario: with_details で関連を含む

- **WHEN** with_details=True で検索
- **THEN** タグや関連タスクが読み込まれた `MemoRead` が返る

### Requirement: タグ・ステータスによるフィルタ（メモ）

- `search` はオプション引数として `status: MemoStatus | None` と `tags: list[UUID] | None` を受け付けなければならない (MUST)。
- `status` が指定された場合、該当ステータスのメモに限定しなければならない (MUST)。
- `tags` が指定された場合、指定タグのいずれかを持つメモに限定しなければならない (MUST)。
- `query` が None/空であっても、フィルタのみでの検索を許容しなければならない (MUST)。

#### Scenario: ステータスで絞り込み

- **WHEN** status=ACTIVE を指定
- **THEN** ACTIVE のメモのみが返る

#### Scenario: タグで絞り込み

- **WHEN** tags=[tagX] を指定
- **THEN** tagX を持つメモのみが返る

#### Scenario: クエリ無しでフィルタのみ

- **WHEN** query=None, status=INBOX を指定
- **THEN** INBOX のメモのみが返る
