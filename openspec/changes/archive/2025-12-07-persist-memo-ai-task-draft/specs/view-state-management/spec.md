## ADDED Requirements

### Requirement: Persisted AiSuggestedTask Snapshot

AI 提案タスクを保持する State（例: `AiSuggestedTask`）は Task 永続化結果のスナップショットとして `task_id`、`route`、`status`（Draft or Approved）を必ず格納しなければならない (MUST)。State 復元時は `ai_analysis_log.draft_task_ids` を読み、足りない情報は TaskApplicationService 経由で取得する (MUST)。route などの情報をローカル再計算のみに頼ってはならない (MUST NOT)。

#### Scenario: Restore State After Navigation

- **GIVEN** 生成済み Draft Task が存在し、View を離れて戻った
- **WHEN** State が `ai_analysis_log` と Task API から復元される
- **THEN** 各 AiSuggestedTask が元の `task_id` と route を保持したまま再表示され、選択状態も維持される
