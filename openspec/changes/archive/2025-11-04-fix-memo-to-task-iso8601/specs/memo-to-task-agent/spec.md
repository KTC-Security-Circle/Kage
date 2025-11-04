## MODIFIED Requirements
### Requirement: Structured JSON Output

エージェントの出力は厳格な JSON で、以下の TaskDraft スキーマに一致しなければならない (MUST)。

- title: string (required)
- description: string (optional)
- due_date: ISO 8601 (date または datetime、UTC "Z" を含む表現を許容) (optional)
- priority: one of [low, normal, high] (optional)
- tags: string[] (optional)
- estimate_minutes: integer (optional)
- route: one of [progress, waiting, calendar, next_action] (optional)
- project_title: string (optional; 複数ステップ検出時)

#### Scenario: 期限付きメモの解析
- **GIVEN** 「金曜までにレポートを提出」
- **WHEN** エージェントを実行
- **THEN** TaskDraft の due_date に今週金曜日相当の ISO 日付が入る（解釈できない場合は省略）

#### Scenario: UTCタイムゾーン付き期日
- **GIVEN** メモに「次のレビューは 2025-03-10T09:00:00Z に実施」と記載されている
- **WHEN** エージェントを実行
- **THEN** TaskDraft の due_date に "2025-03-10T09:00:00Z" が維持される（Z を含む ISO8601 として検証を通過する）
