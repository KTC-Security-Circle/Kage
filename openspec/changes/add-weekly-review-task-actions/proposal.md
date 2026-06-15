## Why

- 週次レビュー Step2 で提示される停滞タスクに対して、ユーザーが決めた「細分化/いつかやる/削除」の判断がアプリ上では一切反映されていない。
- タスク細分化は LLM の支援がないと十分な粒度のサブタスクを作れず、現状の UI だと提案止まりで業務改善になっていない。
- 判断後に実行ボタンでドメイン操作をまとめて行い、UI を最新状態へ更新する導線がない。

## What Changes

- 週次レビュー専用の Task Action Agent を `src/agents/task_agents/weekly_review_actions/` に追加し、split 要求に対して構造化サブタスク案を返すようにする。
- 新しい application/service 層 (`WeeklyReviewActionService` 経由) で、選択されたアクションを TaskApplicationService へ適用し、split 時にはサブタスクを作成・親タスクの状態更新まで行う API を提供する。
- WeeklyReviewView Step2 の UI を拡張し、決定済みのタスクが存在する場合のみ「実行」ボタンを有効化。押下で非同期に action API を呼び、完了後に Insights を再取得して画面を更新する。
- アクションの結果 (作成件数/削除件数/サマリー) を UI で通知し、状態をリセットするガードロジックを追加する。

## Impact

- Affected specs: weekly-review-task-actions (new capability)
- Affected code: `src/agents/task_agents/*`, `logic/services/*`, `logic/application/*`, `views/weekly_review/*`, `tests/agents/*`, `tests/views/weekly_review/*`, `tests/logic/*`
