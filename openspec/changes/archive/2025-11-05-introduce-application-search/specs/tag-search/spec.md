# Spec: tag-search

## ADDED Requirements

### Requirement: タグ検索 API（Application 層）

- Application 層は `search(query: str) -> list[TagRead]` を公開しなければならない (MUST)。
- 検索はタグ名の部分一致（大文字小文字無視）を対象としなければならない (MUST)。
- 結果は `TagRead` の配列を返し、ヒットなしは空配列としなければならない (MUST)。
- ページング/ソートや with_details は将来拡張とし、今回の最小実装では含めない (SHOULD)。

#### Scenario: 名前で部分一致

- **WHEN** query="sec" を指定して検索
- **THEN** 名前に "sec" を含むタグが返る

#### Scenario: ヒットなしは空配列

- **WHEN** query がどのタグにも一致しない
- **THEN** 空配列を返す
