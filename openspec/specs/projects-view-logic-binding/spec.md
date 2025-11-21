# projects-view-logic-binding Specification

## Purpose
TBD - created by archiving change migrate-projects-to-logic-layer. Update Purpose after archive.
## Requirements
### Requirement: Project Application Service Boundary

Projects の View/Controller は ProjectApplicationService を介してのみドメイン操作・読み取りを行わなければならない (MUST)。Repository 直接呼び出し、Query オブジェクトへの直接依存、SQL 直書きは行ってはならない (MUST NOT)。

#### Scenario: Load Project List via Service Port

- GIVEN 画面初期表示
- WHEN プロジェクト一覧をロードする
- THEN `ProjectApplicationPort.list_projects(keyword, status)` を呼び、その結果のみで UI を更新する

### Requirement: Dependency Provisioning

Controller は ProjectApplicationService 解決において DI 注入を優先し、未注入時は `ProjectApplicationService.get_instance()` を用いて取得しなければならない (MUST)。

#### Scenario: Service Acquisition Fallback

- GIVEN Controller 生成時にサービスが未注入
- WHEN 一覧取得を行う
- THEN `get_instance()` で取得して処理を続行し、UI は正常に更新される

### Requirement: Error Notification Contract

サービス呼び出しで例外が発生した場合、Controller は例外を捕捉し `notify_error()`/`SnackBar` 等でユーザーへ通知し、`loguru` で詳細ログを記録しなければならない (MUST)。

#### Scenario: Known Domain Error

- GIVEN 入力不備等で既知のドメイン例外が発生
- WHEN 一覧/詳細取得を実行
- THEN ユーザーへ説明的なメッセージを表示し、詳細はログへ記録される

### Requirement: Asynchronous Operations & Loading Flag

重い処理は UI スレッドをブロックしない手段（AsyncExecutor 相当）で実行しなければならない (MUST)。実行中は `state.loading=True`、完了時に False へ戻す (MUST)。

#### Scenario: Long Fetch

- GIVEN 件数の多い一覧取得
- WHEN 取得を開始
- THEN `loading` が True→False へ往復し、完了までローディング表示が維持される

### Requirement: Presenter/Handler Injection (UI unchanged)

コンポーネントは View/Controller から注入されたハンドラ（Callable/Protocol）のみを呼び出さなければならない (MUST)。コンポーネントがサービスやルータを直接呼び出してはならない (MUST NOT)。既存の `ProjectCardVM`/`ProjectDetailVM` のフィールドとハンドラ契約は変更してはならない (MUST)。

#### Scenario: Card Click Opens Detail

- GIVEN プロジェクトカードがクリックされた
- WHEN コンポーネントが `on_select(project_id)` を呼ぶ
- THEN Controller が詳細を取得して Presenter で VM を構築し、UI を更新する（コンポーネントの API 変更はない）

### Requirement: Detail Fetch Optimization

詳細パネル用に ID 直取得 API（`get_project_by_id`）が提供されている場合、それを利用しなければならない (MUST)。未提供の場合は一旦一覧 + 探索でもよい (MAY) が、API 提供後は ID 直取得へ移行しなければならない (MUST)。

#### Scenario: Get Detail By ID

- GIVEN `get_project_by_id` がサービスに存在
- WHEN 選択中 ID の詳細を取得
- THEN 一覧の線形探索ではなく、ID 直取得で最小コストで取得する

