# agent-integration Specification

## Purpose
TBD - created by archiving change add-terminology-management. Update Purpose after archive.
## Requirements
### Requirement: top-k 用語取得 API

- クエリ文字列および任意のタグフィルタで上位 k 件の用語を返す API を提供しなければならない (MUST)。
- 応答は key/title/description/synonyms/tags を含めるべきである (SHOULD)。

#### Scenario: タグで限定した top-k
- GIVEN security タグ付き 20 件
- WHEN query="認証", k=5, tags=["security"]
- THEN セキュリティ関連の 5 件が返る

### Requirement: プロンプト整形

- 取得した用語をテンプレートに整形して返すヘルパーを提供しなければならない (MUST)。
- テンプレートはカスタマイズ可能であるべきである (SHOULD)。

#### Scenario: 既定テンプレートでの整形
- GIVEN 用語 3 件
- WHEN format_for_prompt(terms)
- THEN 箇条書きで key と要約が整形される

<!-- OPENSPEC:END -->

