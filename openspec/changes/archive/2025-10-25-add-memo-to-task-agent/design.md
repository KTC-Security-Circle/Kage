# Design: add-memo-to-task-agent

## Context

自由形式のメモから、アプリ内部のタスク作成に渡せる TaskDraft[] を生成するエージェントを導入する。最初は最小構成（低リスク、依存最小）で始め、段階的に精度を高める。

## Goals / Non-Goals

- Goals: シンプルなプロンプト＋構造化出力で、壊れにくい最小機能を提供
- Non-Goals: 高度なランキング・重複排除・レビューフローの自動化（後続提案）

## Decisions

- Agent 形式: 既存 Agent 基盤（`src/agents/base.py` 相当）に準拠
- 出力契約: JSON の TaskDraft[]（title 必須、description/due_date/priority/tags/estimate_minutes 任意）
- エラー処理: 解析不能な要素は除外。全体失敗を避け、部分成功を許容
- バリデーション: 受理前にスキーマ一致を厳格チェック
- タグ推定: 既存タグからのみ選択（MUST）。初期はケース非依存の部分一致で十分（SHOULD）。

## Data Contract (Draft)

TaskDraft

- title: string (required)
- description: string | null
- due_date: string (ISO 8601, date-only or datetime) | null
- priority: "low" | "normal" | "high" | null
- tags: string[] | null
- estimate_minutes: integer | null

## Risks / Trade-offs

- LLM 出力破損 → 厳格 JSON 指示＋ post-validate で緩和
- 不要な分割（過分解）→ 後続でマージ UI を検討

## Integration Hook

- 関数: `generate_tasks_from_memo(memo: str) -> list[TaskDraft]`
- 参照: `openspec/specs/agent-integration/spec.md`

## Open Questions

- due_date のタイムゾーン・曖昧日付の扱い（例: 来週、来月）
- UI 反映の最小導線（どの画面から起動するか）
- タグ推定のしきい値や曖昧一致（後続で強化: トークナイズ/ベクトル化など）
