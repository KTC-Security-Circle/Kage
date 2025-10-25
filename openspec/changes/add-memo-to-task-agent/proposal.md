# Proposal: Add Memo-to-Task Agent

## Why

ユーザーは自由形式のメモから実行可能なタスクを素早く作りたい。現在は手動でタスク化しており、粒度や締切の抜け漏れが発生しやすい。メモから構造化タスクへ自動変換するエージェントを導入し、入力摩擦を減らす。

## What Changes

- LLM ベースの「メモ → タスク変換エージェント」を追加（free-text → TaskDraft[]）
- 出力は厳格な JSON 仕様（タイトル必須、説明/期限/優先度/タグ/見積りは任意）
- エージェントをアプリの Agent 統合ポイントにフックする（サービス層から呼び出せる関数）
- 最小実装で開始し、品質向上は後続（評価指標・再プロンプトなど）は別提案で段階導入

## Impact

- Affected specs: memo-to-task-agent（新規）、agent-integration（フック明示）
- Affected code (予定):
  - src/agents/task_agents/memo_to_task_agent.py（新規）
  - src/logic/services/task_service.py（Draft 取込みのエントリポイント追加の可能性）
  - tests/agents/test_memo_to_task_agent.py（新規）
