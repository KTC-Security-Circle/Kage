# view-components-guidelines Specification

## Purpose
TBD - created by archiving change organize-view-layer. Update Purpose after archive.
## Requirements
### Requirement: Component Class Base

複雑な UI 要素は `ft.UserControl` を継承したクラスとして定義しなければならない (MUST)。単純なラッパは関数コンポーネント（factory）を許容する (MAY)。

#### Scenario: TaskBoard Component

- GIVEN タスクボード UI を新規実装
- WHEN 構造が複数のサブ要素とイベントを持つ
- THEN `class TaskBoard(ft.UserControl)` として実装される

### Requirement: Props vs State Separation

外部から渡されるデータ/コールバックはコンストラクタ引数 (props) とし、内部可変値は `self._state`（dataclass）に保持しなければならない (MUST)。

#### Scenario: ProjectList Props

- GIVEN プロジェクト一覧コンポーネント
- WHEN 外部サービスからデータを渡す
- THEN コンストラクタで受け取り、内部で変更しない

### Requirement: Stateless Preference

コンポーネントは可能な限り stateless でなければならない (MUST)。ビジネス上の状態（一覧や選択など）は親 View の dataclass state で管理しなければならない (MUST)。UI の一時的な状態（開閉、入力中文字列など）のみローカル `self._state` の使用を許容する (MAY)。

#### Scenario: Simple Tag Pill

- GIVEN タグ表示のみのコンポーネント
- WHEN クリック以外に状態を持たない
- THEN コンポーネントは stateless とする

### Requirement: Side-Effect Policy

副作用（サービス呼び出し、ファイル I/O）はコンポーネント内部では行ってはならない (MUST NOT)。イベントハンドラで親 View のメソッドをコールし、親が Service と対話する (MUST)。

#### Scenario: Create Task Button

- GIVEN タスク作成ボタン
- WHEN クリックされる
- THEN ボタンは親の `on_create_task()` を呼び、直接 DB 操作しない

### Requirement: Event Handler Injection

コンポーネントはユーザインタラクションに対する副作用的処理（ナビゲーション、Application Service 呼び出し）を内部で直接実行してはならない (MUST NOT)。これらの処理は親 View が提供するハンドラ（Callable/Protocol）を props として受け取り、そのハンドラを呼び出す形で実行しなければならない (MUST)。ナビゲーション（`page.go`）呼び出しは常に注入ハンドラ経由で行わなければならない (MUST)。

#### Scenario: Handler Injection For Navigation

- GIVEN メモ詳細へ遷移するリンクコンポーネント
- WHEN クリックイベントが発生
- THEN 直接 `page.go` を呼ばずに注入された `on_open_memo(memo_id)` ハンドラを呼び出す

### Requirement: Reusability Naming

再利用意図のあるコンポーネントは機能を明確化する名称（例: `FilteredMemoList`）を持たなければならない (MUST)。特定画面に依存する名称（例: `HomeLeftPane`）は使用してはならない (MUST NOT)。

#### Scenario: Memo List Component

- GIVEN メモ一覧を複数画面で使いたい
- WHEN コンポーネント命名を検討
- THEN `MemoList` など汎用性のある名称を選ぶ

### Requirement: Testing Accessibility

コンポーネントはテスト容易性のため、主要操作要素に `data_test_id` 相当の識別子（Flet では `ref` または構造上の安定した index）を提供しなければならない (MUST)。

#### Scenario: Dialog Submit Button

- GIVEN フォーム送信ボタン
- WHEN E2E テストから参照したい
- THEN `Ref[ft.ElevatedButton]` を保持しテストが取得可能

### Requirement: Stable Keys For Repeated Elements

繰り返し表示（リスト/グリッド）のアイテムコンポーネントは安定した識別子 `key` を設定しなければならない (MUST)。動的 index や表示順依存のみで識別してはならない (MUST NOT)。

#### Scenario: Memo List Item Keys

- GIVEN メモ一覧を表示
- WHEN 各メモ行コンポーネントを生成
- THEN 行は `key=memo.id` を持ち、テストと差分更新が安定する

### Requirement: Functional vs Class Component Selection

イベントや内部状態を持たない純粋表示目的の単純 UI は関数コンポーネント (MAY)。イベントハンドラ注入・内部状態管理・再描画制御が必要な場合は `ft.UserControl` を継承するクラスコンポーネントを使用しなければならない (MUST)。

#### Scenario: Static Separator Component

- GIVEN 単純な区切り線表示
- WHEN 実装方針を決定
- THEN 関数 `def separator(): ...` として十分でクラス化しない

