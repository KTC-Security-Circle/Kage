## 1. 仕様更新

- [x] 1.1 memo-to-task-agent 仕様に Draft 永続化と Task Update/Delete フローを追加
- [x] 1.2 views-logic-binding / view-state-management 仕様へ Draft 表示・操作要件を追加

## 2. 実装計画

- [x] 2.1 MemoAiJobQueue 完了処理で TaskApplicationService を通じ TaskStatus.DRAFT で作成し、MemoService と関連付ける
- [x] 2.2 MemoApplicationService/MemosController/MemosViewState を Draft 永続化前提に更新（task_id 保存, ai_analysis_log フォーマット変更）
- [x] 2.3 承認/削除ハンドラーを TaskUpdate/Delete を使う実装に変更し、route→TaskStatus マップを導入
- [x] 2.4 新フローをカバーするユニットテスト・UI 状態テストを追加

## 3. 検証

- [x] 3.1 `uv run poe test`（対象モジュール）を実行し、新規テスト含めて成功することを確認
- [x] 3.2 `uv run poe fix` を実行し、フォーマッタ・リンタを通す
