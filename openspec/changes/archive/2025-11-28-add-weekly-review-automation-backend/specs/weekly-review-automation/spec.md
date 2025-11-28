## ADDED Requirements

### Requirement: Weekly Review Insights Service

バックエンドは WeeklyReviewInsightsService (または等価のアプリケーションファサード) を提供し、単一の呼び出しで週次レビュー 3 ステップ分のデータを集計しなければならない (MUST)。

- 入力: `user_id`, `start_date`, `end_date`, `zombie_threshold_days`, `project_filters`。
- 出力: `highlights`, `zombie_tasks`, `memo_audits` を含む JSON で、各配列は空でも構造を維持する (MUST)。
- デフォルト期間は直近 7 日、ゾンビ判定は 14 日経過 (設定で変更可能) を適用しなければならない (MUST)。
- LLM 呼び出しが失敗した場合でも、各ステップの `status` と `fallback_message` を返し、API が 200 を維持できるようにする (MUST)。

#### Scenario: 単一呼び出しで 3 ステップ取得

- **GIVEN** start/end を明示せずに API を呼び出す
- **WHEN** WeeklyReviewInsightsService.generate_insights(...) を実行する
- **THEN** `highlights`, `zombie_tasks`, `memo_audits` をまとめた JSON が返り、`metadata.period.start` に直近 7 日の開始日が含まれる

### Requirement: Achievement Summary Generation

システムは指定期間に完了したタスクと関連メモを LLM へ渡し、肯定的なトーンで 3 件の主要成果を生成しなければならない (MUST)。

- ハイライトは `title`, `description`, `source_task_ids` を含む 3 件の bullet を返す (MUST)。
- LLM には「労いの言葉を添え、質的な成果を強調する」プロンプトテンプレートを適用しなければならない (MUST)。
- 完了タスクが 3 件未満の場合は、取得できた件数ぶん + 追加の前向きメッセージを返す (SHOULD)。

#### Scenario: 3 件の成果ハイライト

- **GIVEN** 直近 7 日で完了タスクが 5 件ある
- **WHEN** 成果サマリーステップを実行
- **THEN** `highlights.items` に 3 件の bullet が入り、各 bullet に最低 1 つの `source_task_ids` が紐付き、「お疲れさまです」などの肯定トーンのメッセージが `intro` フィールドに含まれる

### Requirement: Zombie Task Remediation Suggestions

システムは作成から `zombie_threshold_days` 経過しても完了していないタスクを抽出し、各タスクに対して LLM が提案する 3 つ以上の処分オプションを返さなければならない (MUST)。

- データ: タスクタイトル、元メモ、現在のプロジェクト/タグ、経過日数をコンテキストとして渡す (MUST)。
- LLM 応答は `action` (split, defer, someday, delete など) と `rationale`、必要なら `suggested_subtasks` を含める (MUST)。
- 抽出する最大件数は最新 20 件程度に制限し、UI がカード表示しやすい JSON を返す (SHOULD)。

#### Scenario: 2 週間以上停滞したタスク提案

- **GIVEN** 15 日前に作成され未完了の「資料作成」タスクが存在する
- **WHEN** zombie ステップを実行
- **THEN** そのタスクが `zombie_tasks[0]` に含まれ、`suggestions` に `split`/`someday`/`delete` の 3 アクションが並び、それぞれに説明文が入る

### Requirement: Unprocessed Memo Shelf Audit

システムは指定期間に作成され、ステータスが idea/processing のままタスク化されていないメモを抽出し、LLM による棚卸し提案を返さなければならない (MUST)。

- 出力は `memo_id`, `summary`, `recommended_route` (task, reference, discard) と optional `linked_project` を含む (MUST)。
- LLM はアクティブプロジェクト一覧を参照し、関連しそうなプロジェクトを推定できる (SHOULD)。
- ユーザーに「タスク化すべき」「資料へ移動」「Someday」など Yes/No 判断を求める短いテキストを生成する (MUST)。

#### Scenario: 未タスク化メモの棚卸し

- **GIVEN** 今週作成され status=idea のメモが 2 件あり、いずれも TaskRepository には紐付いていない
- **WHEN** memo 棚卸しステップを実行
- **THEN** それぞれ `memo_audits` に含まれ、`recommended_route` が "task" または "reference" として提案され、推定した `linked_project.title` が返る
