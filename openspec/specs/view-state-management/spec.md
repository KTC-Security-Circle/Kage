# view-state-management Specification

## Purpose
TBD - created by archiving change organize-view-layer. Update Purpose after archive.
## Requirements
### Requirement: Dataclass State Objects

各 View は表示状態を `@dataclass` で定義した State オブジェクト（例: `MemosViewState`）として保持しなければならない (MUST)。辞書や散在するフィールドで状態を管理してはならない (MUST NOT)。

#### Scenario: Tasks View State

- GIVEN タスク画面
- WHEN 状態を定義
- THEN `@dataclass class TasksViewState:` が存在しフィールドに items/loading/error_message を含む

### Requirement: Immutable Update Pattern

State の更新は `dataclasses.replace(state, field=value)` などにより新しいインスタンスを生成して行わなければならない (MUST)。フィールドを直接ミュータブル操作（`append` 等）した後に再描画のみで済ませるパターンは避けなければならない (MUST NOT)。大量要素の性能最適化が必要な場合のみ一時的なミュータブル操作後に単一回の再割当 + `self.update()` を行う (MAY)。

#### Scenario: Add Task Item

- GIVEN 既存 state.items
- WHEN タスクを追加
- THEN `state = dataclasses.replace(state, items=[*state.items, new_item])` のように不変更新する

#### Scenario: Batch Update Performance

- GIVEN 1000 件のタスクを一括更新
- WHEN パフォーマンスを考慮
- THEN リスト生成を一度で行い `dataclasses.replace` を使い単回更新 + `self.update()` を呼ぶ

### Requirement: Loading/Error Flags

非同期処理開始時に `state.loading=True`、完了時に False を設定しなければならない (MUST)。例外発生時 `state.error_message` にユーザ向けメッセージを格納する (SHOULD)。

#### Scenario: Service Failure

- GIVEN 外部呼び出しで例外
- WHEN 例外捕捉
- THEN `state.error_message` に文言、`loading` は False へ戻る

### Requirement: Reset On Route Change

主要 View はルート遷移時（`did_mount` 再実行等）に再利用不要な表示状態を初期化しなければならない (MUST)。必要なキャッシュは Application Service 側で保持し View 側で重複キャッシュを持ってはならない (MUST NOT)。

#### Scenario: Navigate Away And Back

- GIVEN タスク画面から他画面へ遷移後戻る
- WHEN `did_mount` が呼ばれる
- THEN 状態が再同期される

### Requirement: Derived Data Methods

表示用の派生データ（フィルタ済み一覧など）は `get_*` ヘルパメソッドとして View 内に定義しなければならない (MUST)。派生結果を state に永続フィールドとして追加してはならない (MUST NOT)。

#### Scenario: Filtered Tasks

- GIVEN state.items に複数タスク
- WHEN 完了タスクのみが必要
- THEN `get_completed_tasks()` がフィルタ結果を返し state に不要な重複フィールドを追加しない

