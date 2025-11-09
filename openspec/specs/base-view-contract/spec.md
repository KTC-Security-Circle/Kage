# base-view-contract Specification

## Purpose
TBD - created by archiving change organize-view-layer. Update Purpose after archive.
## Requirements
### Requirement: BaseView Standard Interface

全てのページ View クラスは共通の BaseView 契約に従わなければならない (MUST)。少なくとも以下を満たす:

- `page`: flet.Page への参照を保持する
- `state`: dataclass で `loading: bool` と `error_message: str | None` を含む
- `notify_error(message: str, details: str | None = None) -> None`: ユーザ通知とログ出力を行う
- `with_loading(fn_or_coro)`: 同期/非同期処理をラップし、loading の開始/終了を一貫化する
- Lifecycle hooks: `did_mount()` と `will_unmount()` を提供し、購読/タイマー等の開始と終了を担う

#### Scenario: BaseView Contract Satisfied

- GIVEN 新規 `MemosView`
- WHEN View を実装
- THEN 上記プロパティ/メソッド/ライフサイクルが存在し、`state.loading` と `state.error_message` を標準化する

### Requirement: Update Responsibility

View/コンポーネント内部の UI 更新は `self.update()` を用いなければならない (MUST)。ルーティングによる画面再構築とナビゲーション更新は Router 層が `page.update()` を呼び責務を負わなければならない (MUST)。

#### Scenario: Internal vs Router Update

- GIVEN View 内で state を更新
- WHEN 表示再描画が必要
- THEN View は `self.update()` を呼ぶ。一方でルート遷移時は Router が `page.update()` を呼ぶ

### Requirement: Logging and User Messaging Policy

例外発生時は `loguru` で `exception` レベルのログを記録しなければならない (MUST)。ユーザに表示するエラーメッセージはサニタイズされ、内部情報（スタックトレース、機密）を露出してはならない (MUST NOT)。`notify_error()` はログとユーザ通知の両方を行う単一経路でなければならない (MUST)。

#### Scenario: Domain vs Unknown Error

- GIVEN 既知のドメイン例外と未知の例外
- WHEN `notify_error()` が呼ばれる
- THEN ドメイン例外は簡潔な文言、未知例外は一般的な失敗文言を表示しつつ、詳細はログにのみ残る

### Requirement: Cleanup On Unmount

`will_unmount()` ではイベント購読、タイマー、非同期タスクのキャンセル等のクリーンアップを必ず実施しなければならない (MUST)。

#### Scenario: Cancel Running Task

- GIVEN 長時間実行のタスクを開始済み
- WHEN ユーザが別画面に遷移し View が破棄される
- THEN `will_unmount()` がキャンセルを行い、リソースリークを防止する

