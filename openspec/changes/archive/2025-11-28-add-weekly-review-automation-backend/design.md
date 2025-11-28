## Context

- 週次レビュー画面は既存 Task/Memo API を組み合わせて手動レビューする前提で、AI 支援は Clarify/Memo agent のみ。
- 今回は UI 実装前にバックエンドの収集/要約/API を固め、LLM 出力を Wizard 形式(3 ステップ)で返す。
- TaskService/MemoService は CRUD とステータス別取得が中心で、期間集計や "未タスク化メモ" 抽出 API が不足している。

## Goals / Non-Goals

- Goals:
  - 指定期間(デフォルトは直近 7 日)に基づく成果サマリー、滞留タスク、未処理メモの 3 セットの JSON を 1 API で返す。
  - 期間、対象プロジェクト、しきい値(ゾンビ判定日数)をクエリで切り替えられるようにする。
  - LLM プロンプト生成を専用ビルダーに分離し、モック可能な `ReviewCopilotAgent` を追加する。
  - LLM 失敗時はフォールバックメッセージ/ローカル推論(例: oldest task)でレスポンス構造を崩さない。
- Non-Goals:
  - Flet UI/ウィザード実装
  - カレンダー連携や自動リスケ(後続フェーズ)
  - 永続的なフィードバック保存 (今回返すのはセッションレスデータ)

## Decisions

- Decision: `WeeklyReviewInsightsService` を `logic/services` に追加し、Task/Memo repo と Agent を注入して `generate_insights(request: WeeklyReviewInsightsQuery) -> WeeklyReviewInsights` を実装する。
  - Alternatives: Router 層にロジックを直接書く案 → テスト困難・責務集中。
- Decision: DTO は `models/review.py` などに dataclass+pydantic モデルを定義し、UI で再利用できる JSON Schema を生成する。
- Decision: LLM プロンプトを `agents/task_agents/review_copilot.py` に集約し、3 種のサブプロンプト(成果/ゾンビ/棚卸し)を 1 呼び出しでまとめて返すよう function-call 形式にする。
- Decision: Repository 拡張で `TaskRepository.list_completed_between(start, end)`、`TaskRepository.list_stale_tasks(created_before, status_filter)`、`MemoRepository.list_unconverted_memos(since)` を追加。
- Decision: 期間・閾値は設定でデフォルトを管理(`settings/review.py`)し、`DEFAULT_REVIEW_RANGE_DAYS=7` と `DEFAULT_ZOMBIE_THRESHOLD_DAYS=14` を定義して API がクエリ指定なしの場合に自動適用する。

## Risks / Trade-offs

- LLM レスポンス不整合 → Strict JSON Schema と再試行(最大 2 回)ロジックをエージェント側で持つ。
- データ量増大時のレスポンス遅延 → LLM へ送るコンテキストを summarizer で絞り、タスク/メモ数の上限を設定(例: latest 50)。
- 既存 Clarify agent との混同 → Review 用 Agent を別 namespace に配置し、設定キーを分離。

## Migration Plan

1. DTO/設定/リポジトリ拡張を追加して既存テストを更新。
2. Review Agent + Service 実装後、pytest モックで期待出力を検証。
3. Application API を追加し、新エンドポイント用の統合テスト( FastAPI or router unit )を作成。

## Open Questions

- メモ棚卸し対象の「未タスク化」判定基準 (status=idea?) → Memo モデル仕様の確認が必要。
