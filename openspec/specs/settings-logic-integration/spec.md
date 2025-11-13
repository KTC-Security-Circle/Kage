# settings-logic-integration Specification

## Purpose
TBD - created by archiving change connect-settings-view-logic. Update Purpose after archive.
## Requirements
### Requirement: SettingsView Logic Binding via Controller

SettingsView は Controller 経由でのみアプリケーション層（self.apps.settings）から取得した `SettingsService` の `load_settings_snapshot()` / `save_settings_snapshot()` / 個別更新APIを利用しなければならない (MUST)。View や components が Service を直接参照してはならない (MUST NOT)。

#### Scenario: Initial Load Through Controller

- GIVEN SettingsView が `/settings` へ遷移
- WHEN `did_mount()` が呼ばれる
- THEN Controller が Query を通じて snapshot を取得し state を replace する (直接 Service 呼び出し無し)

#### Scenario: Save Via Controller

- GIVEN ユーザーが変更後に保存ボタンを押下
- WHEN 保存処理が実行
- THEN Controller が self.apps.settings.save_settings_snapshot を呼び、成功後 state.modified が False に更新される

### Requirement: Immutable State Updates

Controller は state を直接ミューテートせず dataclasses.replace 相当の不変更新パターンで差分反映しなければならない (MUST)。

#### Scenario: Theme Toggle Immutable Update

- GIVEN 現在 theme='light'
- WHEN ユーザーが dark を選択
- THEN Controller は新しい SettingsViewState を生成し theme='dark' へ置換し modified=True

### Requirement: Error Categorization

`ValidationError` はユーザ向け詳細メッセージを state.error_message に設定し、未知例外は汎用メッセージを設定しログへスタックトレースを出力しなければならない (MUST)。

#### Scenario: Invalid Theme Value

- GIVEN テーマ選択に 'blue' が渡される
- WHEN Controller.update_theme が呼ばれる
- THEN ValidationError を捕捉し "テーマは'light'または'dark'です" のようなメッセージを表示

### Requirement: Service Injection for Testing

Controller は SettingsService をコンストラクタ注入可能とし、未指定の場合はデフォルト `SettingsService.build_service()` を用いる (MUST)。

#### Scenario: Provide Mock Service

- GIVEN テストでモックサービスを用意
- WHEN Controller を生成
- THEN モックが利用され実ファイルへの保存が行われない

### Requirement: Presenter Isolation

Presenter は純粋関数で snapshot dict を UI 用構造 (options, normalized tuples) に変換し、副作用 (I/O, ログ) を含んではならない (MUST)。

#### Scenario: Provider Options Generation

- GIVEN provider Enum 値一覧
- WHEN Presenter.present(snapshot) を呼ぶ
- THEN provider_options に (value,label) のリストが生成されログ出力やファイル操作は行われない

