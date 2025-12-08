## Why

MemoToTaskAgent が生成するタスクは UI メモリ上と `ai_analysis_log` のみに存在し、画面遷移やアプリ再起動後に所在が追跡できない。Draft としてでも `tasks` テーブルへ永続化されていないため、承認・削除時に Task ドメインのワークフローを踏めず、TaskStatus や route 情報の一貫性が保てない問題がある。

## What Changes

- MemoAI ジョブ完了時に TaskApplicationService を介してタスクを `TaskStatus.DRAFT` で作成し、Memo と Task の関連を保持する。
- 承認・再生成・削除など UI 操作は既存 Task レコードを Update/Delete するフローへ移行し、route から TaskStatus を決定するマッピングとバリデーションを定義する。
- View/State 層は Draft タスクの `task_id`・route・memo 関連情報を保持し、`ai_analysis_log` は既存 Task 参照用メタデータのみ記録する。
- これらのフローを `memo-to-task-agent`、`views-logic-binding`（必要なら `view-state-management`）仕様へ反映し、Draft 永続化と Update/Delete ワークフローを要件化する。

## Impact

- 影響スペック: memo-to-task-agent, views-logic-binding, view-state-management（表示状態と Draft 表示の要求）
- 影響コード: logic/application/memo_application_service.py, logic/application/memo_ai_job_queue.py, logic/application/task_application_service.py（呼び出し増加）, views/memos/\*（state/controller/view）、tests 配下
