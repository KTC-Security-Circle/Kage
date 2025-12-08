## Why
MemoToTaskAgent の Clarify フローで project に分類された場合でも Draft タスクしか生成されず、プロジェクト作成や UI 上の導線が欠落している。memo.content から派生するプロジェクト情報を永続化し、承認フローに統合する必要がある。

## What Changes
- エージェント出力に project 情報と requires_project フラグを追加し、MemoAiJobQueue が ProjectApplicationService を利用して新規プロジェクトを自動作成する
- job snapshot / ai_analysis_log / UI ステートへ project_info を伝播し、メモ詳細の AI 提案カードでプロジェクト導線を表示する
- ユーザー承認フロー（タスク承認・再生成）をプロジェクト作成と同じタイミングで扱うように仕様を更新する

## Impact
- Affected specs: memo-to-task-agent, views-logic-binding
- Affected code: agents.task_agents.memo_to_task.*, logic/application/memo_application_service.py, memo_ai_job_queue.py, views/memos/*, tests
