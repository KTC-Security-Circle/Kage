# term-search Specification

## Purpose
TBD - created by archiving change introduce-application-search. Update Purpose after archive.
## Requirements
### Requirement: 用語検索 API（Application 層）

- Application 層は `search(query: str | None, tags: list[UUID] | None, status: TermStatus | None, include_synonyms: bool=True) -> list[TermRead]` を公開しなければならない (MUST)。
- 検索はキー/タイトル/説明を対象とし、`include_synonyms=True` の場合は同義語も対象としなければならない (MUST)。
- タグ/ステータスによるフィルタリングをサポートしなければならない (MUST)。
- 結果は `TermRead` の配列を返し、ヒットなしは空配列としなければならない (MUST)。
- ページング/ソートは将来拡張とし、今回の最小実装では含めない (SHOULD)。

#### Scenario: 同義語でヒット

- **WHEN** query が登録済み同義語に一致し、include_synonyms=True
- **THEN** 対応する用語が返る

#### Scenario: タグでフィルタ

- **WHEN** tags=[security] を指定
- **THEN** security タグを持つ用語のみ返る

#### Scenario: ステータスでフィルタ

- **WHEN** status=approved を指定
- **THEN** 承認済み用語のみ返る

