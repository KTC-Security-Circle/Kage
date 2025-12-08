## ADDED Requirements

### Requirement: Draft Task Persistence

MemoToTaskAgent の結果は `MemoAiJobQueue` を通じて Task ドメインへ即時永続化しなければならない (MUST)。エージェントが返した各 TaskDraft は `TaskApplicationService.create` を用いて `TaskStatus.DRAFT` の Task レコードとして保存し、`memo_id` を必ず紐付けること (MUST)。永続化完了後は `ai_analysis_log` に参照用の `draft_task_ids` と route 情報を記録し、本文やタグなどの真実は Task テーブルを参照しなければならない (MUST)。

#### Scenario: Draft Persistence On Job Success

- **GIVEN** MemoAiJobQueue が MemoToTaskAgent の応答で 2 件の候補を受け取った
- **WHEN** ジョブが SUCCEEDED へ遷移する
- **THEN** 2 件の Task が `TaskStatus.DRAFT` で作成され、各 Task の ID と route が `ai_analysis_log` に保存される

### Requirement: Approval Uses Task Update/Delete

AI 提案タスクの承認・再生成・削除は Task ドメイン API を通じて実行しなければならない (MUST)。承認時は Draft Task の route に応じて TaskStatus を更新する（progress→PROGRESS、waiting→WAITING、calendar→TODAYS もしくは TODO ＋期限、next_action→TODO）(MUST)。破棄する場合は `TaskApplicationService.delete` を使用し、`MemoService` との関連を解除する (MUST)。

#### Scenario: Approve Draft Task

- **GIVEN** route=progress の Draft Task が存在する
- **WHEN** ユーザーが承認ボタンを押す
- **THEN** TaskStatus が PROGRESS へ更新され、Task は既存ビューにも表示される

#### Scenario: Delete Draft Task

- **GIVEN** Memo 詳細で Draft Task を削除したい
- **WHEN** ユーザーが削除操作を行う
- **THEN** TaskApplicationService.delete が呼ばれ、Task と Memo のリンクおよび `ai_analysis_log` 参照が削除される
