# project-search Specification

## Purpose
TBD - created by archiving change introduce-application-search. Update Purpose after archive.
## Requirements
### Requirement: プロジェクト検索 API（Application 層）

- Application 層は `search(query: str) -> list[ProjectRead]` を公開しなければならない (MUST)。
- 検索はタイトルの部分一致（大文字小文字無視）を対象としなければならない (MUST)。
- 結果は `ProjectRead` の配列を返し、ヒットなしは空配列としなければならない (MUST)。
- ページング/ソートは将来拡張とし、今回の最小実装では含めない (SHOULD)。

#### Scenario: タイトルで部分一致

- **WHEN** query="roadmap" を指定して検索
- **THEN** タイトルに "roadmap" を含むプロジェクトが返る

#### Scenario: ヒットなしは空配列

- **WHEN** query がどのプロジェクトにも一致しない
- **THEN** 空配列を返す

### Requirement: ステータスによるフィルタ（プロジェクト）

- `search` はオプション引数として `status: ProjectStatus | None` を受け付けなければならない (MUST)。
- `status` が指定された場合、該当ステータスのプロジェクトに限定しなければならない (MUST)。
- `query` が None/空であっても、フィルタのみでの検索を許容しなければならない (MUST)。

#### Scenario: ステータスで絞り込み

- **WHEN** status=ACTIVE を指定
- **THEN** ACTIVE のプロジェクトのみが返る

#### Scenario: クエリ無しでフィルタのみ

- **WHEN** query=None, status=COMPLETED を指定
- **THEN** COMPLETED のプロジェクトのみが返る

