## Context

- Step2 cleanup flow ではゾンビタスクに対して split/someday/delete のラジオボタンを提供しているが、決定を永続化する経路が存在しない。
- WeeklyReviewInsightsService は提案 JSON を返すだけで、操作フロー (タスク作成・更新) が別モジュールに分離されていない。
- エージェント実装は review_copilot 配下に限定されており、タスク細分化用の独立した agent が存在しない。

## Goals / Non-Goals

- Goals:
  - split 指定されたタスク群から AI がサブタスク案を生成し、TaskApplicationService を経由して実際の Task を作成する。
  - someday/delete 決定を Task ドメインへ安全に適用する API を公開し、UI から一括実行できるようにする。
  - 実行後に WeeklyReviewView の状態 (ステップ UI, カード) を再構築し、結果サマリーをユーザーへ通知する。
- Non-Goals:
  - 週次レビュー Insights の生成アルゴリズム自体を再設計すること。
  - Memo audit (create_task/archive/skip) のアクション適用まで一緒に実装すること。
  - AI ワークフロー (Queue) への常駐連携を行うこと。

## Decisions

- 新規 Agent: `WeeklyReviewTaskAgent` (仮称) を `task_agents/weekly_review_actions` に配置し、`split` 用の構造化応答 (parent_task_id + subtasks[]) を返す。LLMProvider は既存の設定 (agents.review) を再利用。
- 新規 Service: `WeeklyReviewActionService` を logic.services に追加し、決定 DTO を受け取って TaskRepository + Agent を協調させる。ApplicationService へ `apply_actions(decisions)` を追加して View が境界を跨がないようにする。
- Someday 処理: 当面は `TaskStatus.WAITING` と `due_date=None` へ更新し、「Someday」タグをタグリレーションへ追加する事でリストから除外できるようにする。
- 実行 UI: `WizardNavigation` 直下に `FilledButton` を追加し、`WeeklyReviewState` の決定が 1 件以上ある場合に enabled。押下で `with_loading` を使い、成功時は再読込と SnackBar を発生させる。
- ロギング: controller/service で `loguru` を用いて実行結果 (split 作成件数, deleted ids 等) を INFO に残す。

## Risks / Trade-offs

- LLM 応答失敗時のフォールバック: split action 実行時に agent が失敗した場合、親タスクのみ `WAITING` へ更新してユーザーへ再試行を促す。
- Someday タグの同期: 既にタグが存在しない場合は自動作成する必要があるため、TagApplicationService 依存が増える。タグ命名を固定化して誤作成を避ける。
- 画面更新のタイムラグ: Insights 再取得には再度 review_service の LL.M 呼び出しが伴う。最小限の差分更新 (該当タスクのみ除去) も検討したが、整合性優先で再取得とする。

## Migration Plan

1. Agent / Service のテストを追加し、TaskRepository の fakes を使って split/someday/delete の挙動を検証する。
2. WeeklyReviewView へ実行ボタンと controller 呼び出しを追加し、UI テスト (golden) ではなくロジックテストで状態遷移を確認する。
3. 既存の WeeklyReviewInsights 取得フローは変更せず、アクション実行後に `controller.load_initial_data()` を再利用する。
