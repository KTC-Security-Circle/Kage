# task-search Specification

## Purpose
TBD - created by archiving change introduce-application-search. Update Purpose after archive.
## Requirements
### Requirement: タスク検索 API（Application 層）

- Application 層は `search(query: str, with_details: bool=False)` を公開しなければならない (MUST)。
- 検索はタイトル/説明の部分一致（大文字小文字無視）を対象としなければならない (MUST)。
- 結果は `TaskRead` の配列を返し、ヒットなしは空配列としなければならない (MUST)。
- `with_details=True` の場合、タグ/関連メモ/プロジェクト等の関連情報を含めて返さなければならない (MUST)。
- title/description の両検索結果に同一 ID が含まれる場合、重複は除去しなければならない (MUST)。
- ページング/ソートは将来拡張とし、今回の最小実装では含めない (SHOULD)。

#### Scenario: タイトルで部分一致

- **WHEN** query="fix" を指定して検索
- **THEN** タイトルに "fix" を含むタスクが返る

#### Scenario: 説明で部分一致

- **WHEN** query="investigate" を指定して検索
- **THEN** 説明に "investigate" を含むタスクが返る

#### Scenario: 重複除去

- **WHEN** タイトルと説明の両方で同じタスクがヒット
- **THEN** 結果には同一タスクが 1 件のみ含まれる

#### Scenario: ヒットなしは空配列

- **WHEN** query がどのタスクにも一致しない
- **THEN** 空配列を返す

#### Scenario: with_details で関連を含む

- **WHEN** with_details=True で検索
- **THEN** タグ/関連メモ/プロジェクトが読み込まれた `TaskRead` が返る

### Requirement: タグ・ステータスによるフィルタ（タスク）

- `search` はオプション引数として `status: TaskStatus | None` と `tags: list[UUID] | None` を受け付けなければならない (MUST)。
- `status` が指定された場合、該当ステータスのタスクに限定しなければならない (MUST)。
- `tags` が指定された場合、指定タグのいずれかを持つタスクに限定しなければならない (MUST)。
- `query` が None/空であっても、フィルタのみでの検索を許容しなければならない (MUST)。

#### Scenario: ステータスで絞り込み

- **WHEN** status=PROGRESS を指定
- **THEN** 進行中タスクのみが返る

#### Scenario: タグで絞り込み

- **WHEN** tags=[tagA] を指定
- **THEN** tagA を持つタスクのみが返る

#### Scenario: クエリ無しでフィルタのみ

- **WHEN** query=None, status=TODAYS を指定
- **THEN** 今日のタスクのみが返る

