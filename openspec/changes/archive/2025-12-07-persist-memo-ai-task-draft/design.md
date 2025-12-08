## Context

- 現状の MemoAI フローは MemoAiJobQueue が LLM 応答を受け取った後、`ai_analysis_log` に JSON を保存するのみで Task ドメインには何も作成しない。
- ユーザーは承認前タスクの所在を把握できず、アプリ再読込時に Draft 情報が失われる。
- 今後 Tool Calling へ移行する計画があるため、Task ドメインを経由したワークフローを先行して整備したい。

## Goals / Non-Goals

- Goals: 生成直後のタスクを Draft として永続化し、承認/削除は Task ドメイン経由で完結できる状態を整える。
- Non-Goals: Task ビュー全体の刷新、Tool Calling 実装、メモ以外の AI 生成パイプライン。

## Decisions

1. **Draft 永続化タイミング**: MemoAiJobQueue がジョブ成功した瞬間に TaskApplicationService.create を呼び出して TaskStatus.DRAFT で登録する。理由: UI の待受状態と永続化タイミングを 1 箇所に集約するため。
2. **Route→TaskStatus マッピング**: progress→PROGRESS, waiting→WAITING, calendar→TODO/TODAYS(期日あり), next_action→TODO。複数ステップ(project_title)は TODO + project 紐付けのみ。理由: 既存 TaskStatus と最小限の整合を保つため。
3. **ai_analysis_log フォーマット**: Draft タスク ID を参照できる `draft_task_ids` と `route` 情報のみ保存し、本文は Task テーブルに依存する。理由: 正式データのソースを Task テーブルへ一本化する。
4. **UI 表示**: AiSuggestedTask は TaskRead のスナップショットを保持し、ステータス変更後も Task API から再読込する。理由: Draft/承認済みを同一 UI で扱うため。

## Risks / Trade-offs

- Task を大量作成後にユーザーが一括削除すると DB 負荷が上がる → Task Delete をバッチ化できるよう API 設計を工夫。
- Draft のまま放置されたタスクが増える → 後続でクリーンアップやフィルタリング UI が必要になる。

## Migration Plan

1. Draft 永続化コードを追加し、既存 UI が参照する `ai_analysis_log` も新形式を許容する実装を入れる。
2. 既存ログのみのメモには後方互換として従来パスで表示する。
3. 検証後に旧形式ロジックを段階的に削除予定（別タスク）。

## Open Questions

- `project_title` から既存 Project を自動作成するか？ → 現時点ではメモへ紐づくだけとし、Project 自動生成は見送り。
- Draft の表示場所（Task ビュー）をどうするか？ → 今回はメモ詳細 UI に限定し、Task ビュー拡張は別提案で扱う。
