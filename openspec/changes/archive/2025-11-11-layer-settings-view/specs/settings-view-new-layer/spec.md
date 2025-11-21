# settings-view-new-layer Specification

## Purpose

`SettingsView` を他 View (memos) と同一の多層アーキテクチャへ適合させ、状態管理と責務分離、テスト容易性を向上させる。

## ADDED Requirements

### Requirement: SettingsView Layered Files

`src/views/settings/` は `state.py`, `query.py`, `presenter.py`, `controller.py`, `view.py`, `components/` を含まなければならない (MUST)。既存 `components/` 配下は再利用され、ビジネスロジックを含んではならない (MUST NOT)。

#### Scenario: Settings Directory Structure

- GIVEN 設定画面をレイヤー化する
- WHEN ディレクトリを確認する
- THEN 上記ファイル群が存在し、`view.py` 以外に UI コントロール生成コードが散在しない

### Requirement: SettingsViewState Dataclass

`state.py` で `SettingsViewState` dataclass を定義し、少なくとも `loading: bool`, `error_message: str | None` と appearance/database/window 等のカテゴリ設定フィールドを含まなければならない (MUST)。辞書ベースの匿名構造を使用してはならない (MUST NOT)。

#### Scenario: State Fields Present

- GIVEN `state.py`
- WHEN クラス定義を見る
- THEN Dataclass で上記フィールドが宣言されている

### Requirement: Immutable State Updates

Controller / View は state 更新時に `dataclasses.replace` など不変パターンを用いなければならない (MUST)。可変操作後に update のみ行う方式は避ける (MUST NOT)。

#### Scenario: Toggle Dark Mode

- GIVEN `SettingsController.toggle_dark_mode()`
- WHEN state 更新
- THEN `state = replace(state, appearance=...)` のような不変更新が行われる

### Requirement: Query Layer Abstraction

`query.py` は設定値取得関数 (例: `load_current_settings()`) を公開し、I/O や Application Service 呼び出し以外の UI 加工を行ってはならない (MUST NOT)。

#### Scenario: Load Settings Raw

- GIVEN Query 実装
- WHEN 関数を確認
- THEN 返却は domain/raw 型で UI ラベル加工を含まない

### Requirement: Presenter Transformation

`presenter.py` は Query からの raw データを UI 表示用 (選択肢リスト、ラベル、Enum 名変換) に変換する純粋関数を提供しなければならない (MUST)。副作用を持ってはならない (MUST NOT)。

#### Scenario: Present Theme Options

- GIVEN テーマ候補列挙
- WHEN presenter 関数を呼ぶ
- THEN UI 選択肢 (値+表示ラベル) のリストを返し副作用がない

### Requirement: Controller Orchestration

`controller.py` の `SettingsController` はユーザインタラクション (保存/リセット/トグル) を受け取り、Query/Presenter を組み合わせて state を更新する責務を持たなければならない (MUST)。コンポーネントが Query/Presenter を直接呼び出してはならない (MUST NOT)。

#### Scenario: Save Settings Flow

- GIVEN 保存ボタン押下
- WHEN handler 呼び出し
- THEN Controller が validation → service 呼び出し → state 更新を連鎖させる

### Requirement: View Handler Injection

`view.py` はコンポーネントへ controller のメソッド (Callable) を注入しなければならない (MUST)。コンポーネントが `page.go` や service を直接呼ぶことは禁止 (MUST NOT)。

#### Scenario: Appearance Section Handlers

- GIVEN `AppearanceSection` コンポーネント
- WHEN 生成
- THEN `on_toggle_theme` などのハンドラが注入され内部で controller メソッドを呼ぶ

### Requirement: BaseView Contract Compliance

`SettingsView` は BaseView 契約 (`state.loading`, `state.error_message`, `notify_error`, `with_loading`, `did_mount`, `will_unmount`) を実装しなければならない (MUST)。

#### Scenario: Lifecycle On Mount

- GIVEN ルート遷移で Settings 表示
- WHEN `did_mount` 実行
- THEN `with_loading` 内で初期設定ロードが行われる

### Requirement: Error Handling Policy

Controller の処理で例外が発生した場合、未知例外は包括的メッセージを表示し詳細をログ出力、既知ドメイン例外はドメインメッセージを表示しなければならない (MUST)。

#### Scenario: Invalid Database Path

- GIVEN 無効な DB パス
- WHEN 保存処理
- THEN ユーザに検証エラー文言が表示されログに詳細が記録される

### Requirement: Testability Hooks

Controller / Presenter 関数は純粋またはモック可能依存注入により単体テスト可能でなければならない (MUST)。View 構築はモック Controller を受け入れるコンストラクタ/ファクトリを提供すべき (SHOULD)。

#### Scenario: Inject Mock Controller

- GIVEN テスト
- WHEN View をモック Controller で生成
- THEN 実サービスを呼ばずにハンドラ動作を検証できる

### Requirement: Predefined Form Components

設定編集の再利用可能な UI コンポーネントを `src/views/settings/components/fields/` に用意しなければならない (MUST)。

最低限含むこと:

- `BooleanField`: トグル/スイッチ (value: bool, on_change: Callable[[bool], None])
- `ChoiceField`: ドロップダウン (options: list[tuple[value,label]], selected: str|int|Enum, on_select: Callable[[str|int], None])
- `TextField`: 文字列入力 (value: str, on_change: Callable[[str], None])
- `PathField`: パス入力 (path: str, on_select: Callable[[str], None])
- `NumberPairField`: 2 値入力 (values: tuple[int,int], on_change: Callable[[tuple[int,int]], None])

#### Scenario: Components Are Passive

- GIVEN 上記コンポーネント
- WHEN props を与えてレンダ/操作
- THEN Service 取得や `page.go` を行わず、注入コールバックの呼び出しのみ行う

### Requirement: Models Alignment (models.py)

現状の設定内容 (編集対象) は `src/settings/models.py` に定義されている `AppSettings` に準拠しなければならない (MUST)。`EnvSettings` は本画面の直接編集対象外とし、別変更で扱う (SHOULD)。

#### Scenario: Fields Mapping

- GIVEN AppSettings のフィールド群
- WHEN UI を構築
- THEN `user.theme` は ChoiceField、`user.user_name` は TextField、`database.url` は PathField、`window.size/position` は NumberPairField、`agents.provider` は ChoiceField で編集可能になる
