## MODIFIED Requirements
### Requirement: Clarify Workflow Mapping
メモを Clarify/Organize の決定木に沿って分類し、各 TaskDraft に配置先を示すルート情報を付与できなければならない (MUST)。

- 2 分以内でできる → route=progress（即実行タスクリスト）
- 自分がやるべきでない → route=waiting（連絡待ち/委譲の待機リスト）
- 特定の日にやる → route=calendar（due_date に日付を設定）
- 上記以外の単一ステップ → route=next_action（次のアクションリスト）
- 複数ステップが必要 → project_title と ProjectPlanSuggestion を返し、requires_project=True をセットする。MemoAiJobQueue へ渡される最終出力には `project_plan.project_title` と `project_plan.next_actions` を含め、プロジェクト生成処理で利用できなければならない (MUST)。

#### Scenario: 2 分ルール（即実行）
- **GIVEN** メモ「会議室の予約を今日すぐやる」
- **WHEN** エージェントを実行
- **THEN** 返却の TaskDraft に route=progress が設定される

#### Scenario: 委譲/待機
- **GIVEN** メモ「経理へ請求書の支払いを依頼」
- **WHEN** エージェントを実行
- **THEN** 返却の TaskDraft に route=waiting が設定される

#### Scenario: カレンダー（期日指定）
- **GIVEN** メモ「11/15 に健康診断の予約」
- **WHEN** エージェントを実行
- **THEN** 返却の TaskDraft に route=calendar と due_date（ISO8601）が設定される

#### Scenario: 次のアクション
- **GIVEN** メモ「見積依頼メールを送る」
- **WHEN** エージェントを実行
- **THEN** 返却の TaskDraft に route=next_action が設定される

#### Scenario: 複数ステップ（プロジェクト化）
- **GIVEN** メモ「引越し準備を進める」
- **WHEN** エージェントを実行
- **THEN** 返却に project_title, project_plan(ProjectPlanSuggestion) が含まれ、requires_project=True と少なくとも 1 件の route=next_action タスクが含まれる

### Requirement: Draft Task Persistence
MemoToTaskAgent の結果は `MemoAiJobQueue` を通じて Task ドメインへ即時永続化しなければならない (MUST)。エージェントが返した各 TaskDraft は `TaskApplicationService.create` を用いて `TaskStatus.DRAFT` の Task レコードとして保存し、`memo_id` を必ず紐付けること (MUST)。`requires_project=True` の場合は MemoAiJobQueue が Task 永続化と同じトランザクションの流れで `ProjectApplicationService.create` を呼び出し、Memo 由来の description を持つ Draft プロジェクトを新規作成しなければならない (MUST)。永続化完了後は `ai_analysis_log` に参照用の `draft_task_ids`、route 情報、および `project_info` (id/title/description) を記録し、本文やタグなどの真実は Task/Project テーブルを参照しなければならない (MUST)。

#### Scenario: Draft Persistence On Job Success
- **GIVEN** MemoAiJobQueue が MemoToTaskAgent の応答で 2 件の候補と requires_project=True を受け取った
- **WHEN** ジョブが SUCCEEDED へ遷移する
- **THEN** Draft Project が 1 件作成され、2 件の Task が `TaskStatus.DRAFT` で作成され、各 Task の ID と route・project_id が `ai_analysis_log` に保存される

#### Scenario: Project Creation Failure Fallback
- **GIVEN** ProjectApplicationService が一時的に失敗した
- **WHEN** MemoAiJobQueue がプロジェクト作成を試みる
- **THEN** TaskDraft は保存されるが `project_info.error` が ai_analysis_log に残り、UI は再試行手段を提示できる
