# Projects Query Transition

## Purpose

既存の InMemoryQuery 直接依存を段階的に廃し、ProjectApplicationService 経由の取得 API へ移行するための遷移要件を定義する。UI は不変。

## ADDED Requirements

### Requirement: Query Abstraction via Port

Controller は InMemory 実装へ直接依存せず、`ProjectApplicationPort`（Protocol）を介してデータ取得を行わなければならない (MUST)。

#### Scenario: Controller Uses Port

- GIVEN Controller 初期化
- WHEN 一覧取得を行う
- THEN 依存は Port 型であり、InMemory 具体型への isinstance チェックや直接参照は存在しない

### Requirement: InMemoryQuery Demotion

`InMemoryProjectQuery` はテスト/プロトタイピング用途としてのみ利用されなければならない (SHOULD)。本番コードで使用してはならない (MUST NOT)。

#### Scenario: Production Startup

- GIVEN 本番起動パス
- WHEN Controller がサービス/依存を解決
- THEN InMemory 実装は利用されず、ApplicationService 実装が Port を満たしている

### Requirement: Detail Linear Scan Temporary Allowance

`get_project_by_id` が未実装の場合、一時的に list + 線形探索で詳細取得を行ってもよい (MAY) が、専用 API が追加された段階で移行しなければならない (MUST)。

#### Scenario: Missing get_by_id API

- GIVEN サービスに ID 直取得メソッドが存在しない
- WHEN 詳細パネル更新
- THEN list_projects の結果を線形探索し取得するが、専用 API 追加後はコードが置換される

### Requirement: Test Replace Strategy

単体テストは Port モックを注入し、InMemory 実装を直接使用しなくても動作しなければならない (MUST)。

#### Scenario: Inject Mock Service

- GIVEN Port を満たすモックを用意
- WHEN Controller を生成し一覧取得を呼び出す
- THEN テストは成功し、InMemory 実装を必要としない

## Notes

- Cross-Refs: `projects-view-logic-binding` (サービス境界), `views-logic-binding` (一般原則)
