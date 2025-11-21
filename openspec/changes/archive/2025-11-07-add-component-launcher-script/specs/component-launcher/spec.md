# Change: add-component-launcher-script / Component Launcher

## ADDED Requirements

### Requirement: Component Launcher Invocation

システムは開発者が CLI 経由で単一 Flet コンポーネントを起動できる手段を提供しなければならない (MUST)。

#### Scenario: Invoke by module path

- **WHEN** 開発者が `--target src.views.task.view:TaskView` を指定してランチャーを実行
- **THEN** 指定されたクラスを import し page に追加して表示する

#### Scenario: Invoke by file path

- **WHEN** 開発者が `--target src/views/task/view.py:TaskView` を指定してランチャーを実行
- **THEN** ファイルパスを動的 import し指定クラスを取得して表示する

### Requirement: Dynamic Import Resolution

ランチャーはファイルパス形式とドット区切りモジュールパス形式の両方を受け入れ正確に解決しなければならない (MUST)。

#### Scenario: File path with extension

- **WHEN** `--target path/to/component.py:MyControl` 指定
- **THEN** `importlib.util.spec_from_file_location` を用いてモジュールロードしクラス取得に成功する

#### Scenario: Module path without extension

- **WHEN** `--target package.module:MyControl` 指定
- **THEN** `importlib.import_module` が成功しクラス取得に成功する

### Requirement: Reuse Base App Configuration

ランチャーは既存アプリと同じログ設定・フォント設定・基本コンフィグを初期化しなければならない (MUST)。

#### Scenario: Logging initialized

- **WHEN** ランチャー起動
- **THEN** `logging_conf` の設定が適用されログフォーマットが通常起動時と一致する

#### Scenario: Fonts applied

- **WHEN** ランチャー起動
- **THEN** `page.fonts` に本番アプリと同一フォントマッピングが設定される

### Requirement: Component Interface Contract

対象クラスは `ft.Control` (または `ft.UserControl`) のサブクラスであるか、`create_control(page)` ファクトリ関数を提供しなければならない (MUST)。

#### Scenario: Control subclass accepted

- **WHEN** 指定クラスが `ft.UserControl` を継承
- **THEN** インスタンス生成後に `page.add(instance)` で表示される

#### Scenario: Factory function accepted

- **WHEN** モジュールが `create_control(page)` を定義
- **THEN** その戻り値が Control として追加される

### Requirement: Error Handling & Exit Codes

ランチャーはインポート/解決/インターフェイス不一致/初期化失敗を分類し非ゼロ終了コードと明確なメッセージを返さなければならない (MUST)。

#### Scenario: Class not found

- **WHEN** 指定されたクラス名が存在しない
- **THEN** 標準エラーに原因を表示し終了コードが非ゼロ (例: 2) になる

#### Scenario: Invalid interface

- **WHEN** 取得対象が Control でもファクトリでもない
- **THEN** インターフェイス不一致エラーを表示し終了コードが非ゼロになる

### Requirement: Optional Layout Wrapping

開発者は既存レイアウト(`views/layout.py`) でコンポーネントをラップするかどうかを CLI フラグで選択できなければならない (SHALL)。

#### Scenario: Wrap enabled

- **WHEN** `--wrap-layout` フラグを付与
- **THEN** コンポーネントはレイアウトコンテナ内部に組み込まれて表示される

### Requirement: Props Injection

ランチャーは JSON 文字列で与えられた初期プロパティをコンポーネントコンストラクタまたはファクトリへ受け渡さなければならない (SHALL)。

#### Scenario: Valid JSON props

- **WHEN** `--props '{"title": "Demo"}'` 指定
- **THEN** コンポーネント生成時に引数として渡され表示に反映される

#### Scenario: Invalid JSON props

- **WHEN** 壊れた JSON を指定
- **THEN** パース失敗エラーを表示し終了コードが非ゼロになる
