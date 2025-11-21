# terminology-core Specification

## Purpose
TBD - created by archiving change add-terminology-management. Update Purpose after archive.
## Requirements
### Requirement: 用語の CRUD とユニーク制約

- Term は `key` をユニークとし、`title` と `description` を保持しなければならない (MUST)。
- Term の作成/更新/削除/取得 API を提供しなければならない (MUST)。

#### Scenario: 既存 key の作成は失敗
- GIVEN 既に `key="sso"` の Term が存在
- WHEN 同じ key で Term を作成
- THEN AlreadyExists エラーとなる

#### Scenario: 削除で存在しない場合は NotFound
- GIVEN 存在しない ID
- WHEN delete を実行
- THEN NotFound エラーとなる

### Requirement: タグと同義語の管理（既存タグ再利用）

- Term は複数の Tag と Synonym を持てなければならない (MUST)。
- Tag は既存の `tags` テーブルのレコードを参照し、Term との関連は中間テーブルで表現しなければならない (MUST)。

#### Scenario: 同義語の追加と重複拒否
- GIVEN Term に synonym="Single Sign-On" を追加済み
- WHEN 同一 synonym を再度追加
- THEN ValidationError となる

### Requirement: 検索（キーワード/タグ/同義語）

- キーワード/タグ/同義語を考慮した検索 API を提供しなければならない (MUST)。
- 検索は部分一致（前方/中間）をサポートしなければならない (MUST)。

#### Scenario: 同義語でヒット
- GIVEN key="sso", synonym="Single Sign-On" が登録
- WHEN query="single sign" で検索
- THEN sso の Term が返る

#### Scenario: タグでフィルタ
- GIVEN tag="security" が付与された Term 群
- WHEN tags=["security"] で検索
- THEN security タグの Term のみが返る

### Requirement: インポート/エクスポート

- CSV/JSON によるバルク入出力を提供しなければならない (MUST)。
- 既存 key はスキップ/上書きの戦略を選択できなければならない (SHOULD)。

#### Scenario: CSV インポートで 100 件成功
- GIVEN 100 件の Term を含む CSV
- WHEN import(csv, strategy="skip")
- THEN 100 件が挿入（既存はスキップ）される

<!-- OPENSPEC:END -->

