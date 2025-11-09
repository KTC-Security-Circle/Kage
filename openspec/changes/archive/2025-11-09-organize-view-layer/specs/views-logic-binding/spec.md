# Specification: views-logic-binding

<!-- OPENSPEC:START -->

## ADDED Requirements

### Requirement: Application Service Boundary

View は Application Service（例: `MemoApplicationService`）を経由してのみドメイン操作を行わなければならない (MUST)。Repository 直接呼び出しや SQL 実行を View で行ってはならない (MUST NOT)。

#### Scenario: Invoke Memo Service From View

- GIVEN メモ作成ボタンが押下された
- WHEN View が入力値を検証して処理を委譲する
- THEN `MemoApplicationService.create(title, content)` を呼び出し、結果を UI に反映する

### Requirement: Dependency Provisioning

View は Service 取得において、`SettingsApplicationService.get_instance()` など既存の Application Service のファクトリ/シングルトン規約に従わなければならない (MUST)。DI コンテナが存在しない場合は `get_instance()` にフォールバックする (SHOULD)。

#### Scenario: Service Acquisition Without Container

- GIVEN DI コンテナが未導入
- WHEN View が設定値を参照したい
- THEN `SettingsApplicationService.get_instance()` を用いて取得する

#### Scenario: Missing Service Dependency

- GIVEN View がコンストラクタ注入を受けておらず、かつ `get_instance()` も未提供/解決不可
- WHEN View が Service 呼び出しを試みる
- THEN View はクラッシュせず `notify_error()` によりユーザへ通知し、`loguru` に詳細例外ログを記録する（既知/未知の区別ポリシーに従う）

### Requirement: Error Notification Contract

Service 呼び出しで例外が発生した場合、View はエラーを捕捉し、`SnackBar`/`AlertDialog` を用いてユーザに通知しなければならない (MUST)。同時に `loguru` で例外ログを記録すること (SHOULD)。

#### Scenario: Validation Error In Service

- GIVEN `ContentValidationError` が発生する入力
- WHEN View から Service を呼ぶ
- THEN View は例外を捕捉してユーザ通知し、ログに詳細を残す

### Requirement: Asynchronous Operations

重い処理（AI 呼び出し、I/O）は UI スレッドをブロックしない手段で実行しなければならない (MUST)。具体 API 依存を避けるため `AsyncExecutor.run(callable)` のようなアダプタを経由して非同期実行を行わなければならない (MUST)。View は `loading` 状態を管理しローディング表示を行う (SHOULD)。

#### Scenario: Clarify Memo Async

- GIVEN Clarify ボタン押下
- WHEN エージェント実行をトリガー
- THEN `AsyncExecutor.run` で非同期実行し、完了まで `loading` 表示を行う

### Requirement: Error Category and Messaging Policy

サービス呼び出し失敗は「既知のドメイン例外」と「未知の例外」に分類して扱わなければならない (MUST)。既知例外は説明的メッセージを `SnackBar` 等で表示し、未知例外は汎用エラーメッセージを表示する (SHOULD)。詳細は常に `loguru` 例外ログに記録する (MUST)。

#### Scenario: Known vs Unknown Error Handling

- GIVEN 入力不備で `ContentValidationError` が起きるケース
- WHEN View が Service を呼び出す
- THEN SnackBar にドメインメッセージ、未知例外では汎用メッセージ + 例外ログ

### Requirement: Service Injection for Testing

View はコンストラクタ引数により Application Service を注入可能でなければならない (MUST)。未注入時は `get_instance()` を使用してデフォルト解決してもよい (SHOULD)。

#### Scenario: Provide Mock Service

- GIVEN テストでモック Service を利用したい
- WHEN View を生成
- THEN コンストラクタ引数でモックを渡し `get_instance()` は呼ばれない

### Requirement: Presenter/Handler Injection

View は UI 依存のオーケストレーション（ナビゲーション、ダイアログ制御、Application Service 呼び出しの連携）を保持し、コンポーネントへはハンドラ（Callable/Protocol）として注入しなければならない (MUST)。コンポーネントが Service を直接取得/呼び出すこと、および `page.go` を直接呼ぶことは許可されない (MUST NOT)。

#### Scenario: Inject Handlers Into Components

- GIVEN `MemosView` が `MemoList` コンポーネントを使用
- WHEN `MemoList` の行クリックで詳細遷移が必要
- THEN `MemosView` は `on_open_memo` ハンドラを注入し、`MemoList` はそれを呼び出して遷移を発生させる

## REMOVED Requirements

(なし)

## MODIFIED Requirements

(なし)

See also: base-view-contract (notify_error/with_loading), view-components-guidelines (handler injection), view-state-management (loading flag)

<!-- OPENSPEC:END -->
