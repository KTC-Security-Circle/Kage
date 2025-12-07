## ADDED Requirements

### Requirement: Memo AI Task Binding

MemosView は AI 生成タスクを View 内で組み立てず、必ず Application Service を介して取得した Draft Task を表示しなければならない (MUST)。ジョブ完了後は `MemoApplicationService.refresh_memo` を通じて最新 Memo + Task を再取得し、UI で保持する `AiSuggestedTask` に `task_id` を設定する (MUST)。承認・削除・再生成は `MemoApplicationService` に追加される専用 API（TaskUpdate/Delete を内部で実行）を呼び出し、View から直接 TaskRepository を触ってはならない (MUST NOT)。

#### Scenario: Approve Draft Task From View

- **GIVEN** MemosView が Draft Task 一覧を表示している
- **WHEN** 承認ボタンを押す
- **THEN** View は Controller 経由で `MemoApplicationService.approve_ai_tasks(memo_id, task_ids)` を呼び、結果を受け取って UI を更新する

#### Scenario: Delete Draft Task From View

- **GIVEN** 1 件の Draft Task を削除したい
- **WHEN** View で削除操作を発火させる
- **THEN** Controller は `MemoApplicationService.delete_ai_task(memo_id, task_id)` を呼び、成功後に再読込して UI から削除する
