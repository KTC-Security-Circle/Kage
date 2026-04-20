## ADDED Requirements

### Requirement: Weekly Review Task Agent

WeeklyReview の Step2 で「細分化」を選択したタスク群は、新設する `WeeklyReviewTaskAgent` を通じてサブタスク案を生成できなければならない (MUST)。
エージェントは `task_agents/weekly_review_actions` 配下に置かれ、入力として `task_id`, `title`, `stale_days`, `context`(reason/memo_excerpt) を含む配列を受け取り、各要素に対して `split_plan` を返さなければならない (MUST)。
`split_plan.subtasks` には 1..5 件の `{title, description, first_step_hint, estimate_minutes?}` を含み、JSON Schema に準拠した構造化レスポンスのみを返さなければならない (MUST)。
エージェントが失敗した場合は parent_task_id ごとにフォールバック (空配列と rationale) を返し、UI 側が再処理できるよう `status=failure` を含む必要がある (SHOULD)。

#### Scenario: Generate split plan for stale task

- **GIVEN** `WeeklyReviewTaskAgent` に `[{"task_id": "123", "title": "資料作成", "stale_days": 18, "context": "2週間停滞"}]` を渡す
- **WHEN** エージェントを実行する
- **THEN** `split_plan` と 2 件以上の `subtasks` を含む JSON を返し、各 subtask に title/description/first_step_hint が含まれる

### Requirement: Weekly Review Cleanup Action Service

WeeklyReviewActionService は UI から渡される `TaskCleanupDecision[]` (task_id/action) を受け取り、単一トランザクションで処理結果を返さなければならない (MUST)。
`action="split"` の場合、対象タスクを `WeeklyReviewTaskAgent` にまとめて渡し、戻り値の subtasks を `TaskApplicationService.create` 経由で Draft タスク (`TaskStatus.DRAFT`) として一括作成し、作成された task_id をレスポンスへ含めなければならない (MUST)。Draft 作成後に親タスクを `TaskStatus.PROGRESS` へ更新し、Draft が承認されるまでは既存リストへ表示されないようにしなければならない (SHOULD)。
`action="someday"` は `TaskApplicationService.update` で `status=TaskStatus.WAITING`, `due_date=None` を設定し、「Someday/Maybe」タグ (存在しなければ TagApplicationService で作成) を紐付けなければならない (MUST)。
`action="delete"` は `TaskApplicationService.delete` を呼び、削除件数をレスポンスに含める (MUST)。
レスポンスは `created_subtasks`, `split_task_ids`, `moved_to_someday`, `deleted_tasks`, `errors` を含み、View 層が SnackBar に表示できるよう集計済みサマリー文字列を返さなければならない (SHOULD)。

#### Scenario: Apply mixed decisions atomically

- **GIVEN** `decisions=[{"task_id":"A","action":"split"},{"task_id":"B","action":"someday"},{"task_id":"C","action":"delete"}]`
- **WHEN** WeeklyReviewActionService.apply_actions を呼び出す
- **THEN** A の subtask が 2 件作成され親が PROGRESS へ更新され、B は WAITING+Someday タグに更新され、C は削除され、レスポンスに各件数が集計される

### Requirement: Weekly Review Cleanup Execution UI

WeeklyReviewView Step2 は UI 上で選択された `ZombieTaskAction` を集計し、1 件以上の決定がある場合のみナビゲーション直下の「実行」ボタンを活性化しなければならない (MUST)。アクションボタン（細分化/いつか/削除）は選択状態を視覚的に示す強調スタイル（色反転など）を適用し、どの操作が有効か即座に分かるようにしなければならない (MUST)。
実行ボタン押下時は `with_loading` を使って WeeklyReviewApplicationService.apply_actions を非同期呼び出しし、成功時には `controller.load_initial_data()` を再実行してゾンビ/メモカードを最新化し、結果サマリーを SnackBar で表示しなければならない (MUST)。
処理中はボタンを disabled にし、失敗時には決定状態を維持したままエラーメッセージを通知し、ログへ詳細例外を残さなければならない (MUST)。
決定が 0 件の場合にボタンを押しても service を呼ばず、「実行する項目を選択してください」という Info SnackBar を表示するべきである (SHOULD)。
Draft タスクが生成された場合、Step2 画面内に「AI が提案したサブタスク（承認待ち）」セクションを表示し、各 Draft について承認（TaskStatus を TODO へ更新）/破棄（削除）/内容確認のアクションを提供しなければならない (MUST)。承認または破棄が完了した Draft は即座に UI から除去し、処理結果を SnackBar で通知しなければならない (SHOULD)。

#### Scenario: Execute cleanup and refresh view

- **GIVEN** 2 件のゾンビタスクで「細分化」と「削除」を選択している
- **WHEN** Step2 下部の実行ボタンを押す
- **THEN** View が loading 状態になり、処理成功後に Insights を再取得して該当カードからタスクが消え、SnackBar で「細分化 1 件 / 削除 1 件」を表示したのち選択状態をリセットする
