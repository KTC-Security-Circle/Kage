## Context
MemoToTaskAgent の Clarify フローは "project" 分岐でも Draft タスクだけを返し、Project ドメインへは何も連携していない。Memo 詳細ビューではタスク承認 UI しか存在せず、プロジェクト化を促す導線が欠落している。

## Goals / Non-Goals
- Goals: project 分岐で新規 Project を自動作成し、ai_analysis_log から UI へ project_info を伝搬する。MemosView から ProjectsView へ即座に遷移できる導線を用意する。
- Non-Goals: 既存の Task 承認 API や Projects View 自体の UX を全面改修すること。

## Decisions
1. **Project creation timing**: MemoAiJobQueue が Draft タスク永続化と同じループ内で ProjectApplicationService.create を呼び出し、project_id をタスク作成時に紐付ける。これにより race condition を避け、UI が job snapshot から完全な情報を読める。
2. **Description source**: プロジェクト description は memo.content の先頭 200 文字 (改行含む) をトリムしたものを利用し、空のときは `"(AI生成)"` を設定する。
3. **Spec propagation**: ai_analysis_log を version 3 に上げ、`project_info` ブロックを常設する。旧ログとの互換性は読み込み時に version 判定で維持。
4. **UI binding**: MemosViewState に `linked_project` 情報を保持し、Presenter がプロジェクト作成済みカードと ProjectsView へのボタンを表示。on_open_project は TasksView の遷移ロジックと同様に client_storage を経由して `/projects` を開く。

## Risks / Trade-offs
- Job queue での project 作成失敗がキュー全体を止める可能性 → 例外を捕捉し、project_info に `error` を記録して Draft タスク生成は継続する。
- ai_analysis_log の互換性: version を切り替えないと旧ログを壊す恐れがあるため、読み込みコードを必ずバージョンチェック対応にする。

## Migration Plan
1. Spec/Proposal 作成とレビュー。
2. Agent スキーマ → Application → JobQueue → UI の順に実装。
3. 影響するテストを更新、`uv run poe check` / `uv run poe test` で回帰確認。

## Open Questions
- プロジェクトタイトルの最終決定ロジック（LLM出力 vs memo.title）: まずは LLM から返る `project_plan.project_title` を優先し、fallback として memo.title を使用する。
