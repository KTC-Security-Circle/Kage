# Spec: logic テストカバレッジ向上

<!-- OPENSPEC:START -->

## ADDED Requirements

### Requirement: Service 層の例外・分岐網羅

- Service 層の分岐/例外 (成功/NotFound/境界値/空集合/with_details 分岐) はテストで網羅されなければならない (MUST)。
- 行カバレッジは pytest-cov により 85% 以上を達成しなければならない (MUST)。

#### Scenario: TaskService.delete の force=false 経路

- GIVEN 既存タスクが存在する
- WHEN delete(task_id, force=False) を実行
- THEN remove_all_tags と delete が呼ばれ、True を返す

#### Scenario: TaskService.remove_tag のタグ未存在

- GIVEN タスクに対象タグが無い
- WHEN remove_tag を呼び出す
- THEN NotFoundError が送出される

#### Scenario: TaskService.list_by_status の空集合

- GIVEN 指定ステータスに一致するタスクが存在しない
- WHEN list_by_status を呼び出す
- THEN Repository の NotFoundError を透過し、NotFoundError を送出する

### Requirement: Repository 層の例外・クエリ網羅

- Repository 層の例外系 (存在しない ID、DB 例外のモック) とクエリ分岐はテストで網羅されなければならない (MUST)。
- 行カバレッジは pytest-cov により 85% 以上を達成しなければならない (MUST)。

#### Scenario: TaskRepository.get_by_id の未存在

- GIVEN 不正な ID
- WHEN get_by_id を呼び出す
- THEN NotFoundError を送出

#### Scenario: TaskRepository.list_by_status の詳細読み込み分岐

- GIVEN with_details=True での呼び出し
- WHEN list_by_status を実行
- THEN 関連情報を含む結果が返る

### Requirement: UnitOfWork/Factory のエッジケース

- 例外時のロールバックおよびリソース解放はテストで検証されなければならない (MUST)。

#### Scenario: UnitOfWork 内例外でロールバック

- GIVEN トランザクション開始
- WHEN 処理中に例外が発生
- THEN ロールバックが実行される

### Requirement: カバレッジ閾値の段階設定

- `poe test-cov` 実行時に logic 配下の行カバレッジ最小値は段階的に強制されなければならない (MUST)。
- 初期閾値は 80% とし、段階的に 85% に引き上げなければならない (MUST)。

#### Scenario: カバレッジ 85% 未満で CI 失敗

- GIVEN CI 上で poe test-cov を実行
- WHEN logic 配下のカバレッジが 85% 未満
- THEN ジョブは非ゼロ終了コードで失敗する

### Requirement: カバレッジレポート更新

- tests/logic/COVERAGE_REPORT.md は最新の計測値と差分、優先課題を反映するよう更新されなければならない (MUST)。

#### Scenario: レポートに最新の層別値が反映

- GIVEN 新規テストが反映
- WHEN レポート更新
- THEN 各層の数値が最新化される

<!-- OPENSPEC:END -->
