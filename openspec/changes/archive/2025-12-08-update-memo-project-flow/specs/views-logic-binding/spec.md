## MODIFIED Requirements
### Requirement: Memo AI Task Binding
MemosView は AI 生成タスクを View 内で組み立てず、必ず Application Service を介して取得した Draft Task を表示しなければならない (MUST)。ジョブ完了後は `MemoApplicationService.refresh_memo` を通じて最新 Memo + Task を再取得し、UI で保持する `AiSuggestedTask` に `task_id` を設定する (MUST)。承認・削除・再生成は `MemoApplicationService` に追加される専用 API（TaskUpdate/Delete を内部で実行）を呼び出し、View から直接 TaskRepository を触ってはならない (MUST NOT)。`requires_project=True` の応答を受け取った場合は `ai_analysis_log.project_info` を State に復元し、プロジェクト作成の結果（成功/失敗）をカード上に表示した上で ProjectsView への遷移ハンドラを提供しなければならない (MUST)。

#### Scenario: Approve Draft Task From View

- **GIVEN** MemosView が Draft Task 一覧を表示している
- **WHEN** 承認ボタンを押す
- **THEN** View は Controller 経由で `MemoApplicationService.approve_ai_tasks(memo_id, task_ids)` を呼び、結果を受け取って UI を更新する

#### Scenario: Delete Draft Task From View

- **GIVEN** 1 件の Draft Task を削除したい
- **WHEN** View で削除操作を発火させる
- **THEN** Controller は `MemoApplicationService.delete_ai_task(memo_id, task_id)` を呼び、成功後に再読込して UI から削除する

#### Scenario: Show Project CTA On Memo Detail
- **GIVEN** Memo の AI 分析ログに project_info(id/title/description) が含まれる
- **WHEN** MemosView が詳細カードを描画する
- **THEN** Presenter は「AI がプロジェクトを作成しました」バナーと ProjectsView へ遷移する `on_open_project(project_id)` ハンドラを表示する

#### Scenario: Handle Project Creation Error
- **GIVEN** project_info に `error` が含まれる
- **WHEN** ユーザーが AI パネルを確認する
- **THEN** View はエラーバナーを表示し、再生成ボタンを提供して同じ Application Service API を用いてリトライできる
