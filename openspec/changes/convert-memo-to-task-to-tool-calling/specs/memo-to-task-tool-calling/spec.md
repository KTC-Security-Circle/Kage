# 仕様: MemoToTask の Tool Calling 化（TaskDraft 廃止、TaskStatus.DRAFT 採用）

## MODIFIED Requirements

### Requirement: Tool Calling でタスクを直接永続化する

- The agent MUST replace structured output with Tool Calling for actionable memos and MUST persist tasks directly.
- The agent MUST bind tools and MUST issue at least one task-creation tool call when actionable.
- The agent MUST NOT return intermediate TaskDraft in its final payload (summary-only output is allowed).
- All DB changes MUST go through Application Services (e.g., TaskApplicationService, MemoApplicationService). Repositories MUST NOT be called directly by tools.

#### Scenario: アクショナブルなメモでツールを 1 回以上呼び出す

- メモ本文が具体的行動を示すとき、create_tasks を呼び出し、作成されたタスクの ID 群を返す。
- suggested_memo_status を返し、decision_summary に判断根拠を要約する。

### Requirement: ドラフト状態は TaskStatus.DRAFT で表現する

- TaskStatus MUST include 'DRAFT' (canonical string value: "draft").
- No new column SHALL be introduced. Migration SHALL only extend the existing 'taskstatus' enum.

#### Scenario: 要レビュー示唆時は DRAFT で保存

- メモが「検討/レビューが必要」を示す場合、status=DRAFT で保存し、decision_summary に根拠を記載する。

### Requirement: DB 操作用ツール（create_tasks, update_memo_status）の提供

- The system SHALL provide two DB operation tools: create_tasks and update_memo_status.
- Both tools MUST delegate to the Application layer and MUST NOT access repositories directly.
- Inputs and outputs for each tool SHALL be validated; invalid payloads MUST be rejected with a safe error response.

- ツール: create_tasks
  - 入力: tasks: 配列（各要素は { title, description?, due_date?(ISO8601 日付), route?("next_action"|"progress"|"waiting"|"calendar"), tags?[], project_title? }）
  - 挙動: TaskApplicationService 経由で永続化。route → Task.status のマッピングは以下。
    - next_action → TODO
    - progress → PROGRESS
    - waiting → WAITING
    - calendar → TODO（due_date を日付として設定）
    - メモが「要レビュー」を示唆する場合、status を DRAFT として保存してよい（実装時にプロンプト/ロジックで判定）。
  - 出力: { created_task_ids: UUID 配列 }

#### Scenario: クイックアクション（Quick action task）

- メモが短時間で着手すべき行動を示す場合、create_tasks を 1 件呼び出し、route=="progress" を指定。
- 戻り値の suggested_memo_status は "active"、created_task_ids は 1 件を想定。
- decision_summary.applied_rules に "quick_action" 系ルールが含まれ、mapping_reasons[0] に短い根拠が列挙される。

#### Scenario: 委任タスク（Delegated task）

- 委任が適切な場合、create_tasks の route=="waiting" を指定。戻り値 suggested_memo_status は "active"。
- decision_summary.mapping_reasons に "waiting" 選定理由（例: "依頼/確認待ちの表現を検出"）が含まれる。

#### Scenario: カレンダー（期限あり）

- 期限が示される場合、create_tasks の route=="calendar" を指定し、due_date を日付として設定。戻り値 suggested_memo_status は "active"。
- decision_summary.mapping_reasons に期日抽出の根拠（例: "日付表現(YYYY-MM-DD)を検出"）が含まれる。

#### Scenario: プロジェクト化（Project plan）

- 複数ステップの提案がある場合、共通の project_title を付けて複数件を作成。先頭は next_action（TODO）に、以降は progress（PROGRESS）にマップする。戻り値 suggested_memo_status は "active"。
- decision_summary.applied_rules に "project_first_step→next_action" 等のルールが含まれる。

- ツール: update_memo_status（シナリオにより任意）
  - 入力: { memo_id: UUID, status: "inbox"|"active"|"idea"|"archive" }
  - 挙動: MemoApplicationService 経由でメモの状態を更新。

## REMOVED Requirements

- DraftStatus 型と Task.draft_status カラムの導入。
  - 理由: モデル表面を増やさず、TaskStatus.DRAFT に統合するほうがシンプルであるため。

## ADDED Requirements

### Requirement: 最終応答に意思決定の要約（decision_summary）を含める

- The final response MUST include decision_summary capturing the rationale at a high level.
- 目的: 「なぜその判断に至ったか」を簡潔・構造化して残すため（監査性・説明責任）。
- 形式（例）:
  - decision_summary: {
    memo_insights: string[]; // メモから抽出した要点（短文）
    applied_rules: string[]; // 適用したルール名/規則（例: "quick_action<=2min→PROGRESS"）
    mapping_reasons: Array<{ // 各作成タスクのルート/ステータス選定理由
    title: string;
    route: "next_action"|"progress"|"waiting"|"calendar";
    status: string; // 実際に保存した TaskStatus
    reasons: string[]; // 簡潔な根拠（最大 3 点程度）
    }>;
    safety_notes?: string[]; // バリデーション・制約の注記（省略可）
    confidence?: "low"|"medium"|"high"; // 信頼度（任意）
    }
- プライバシー/安全方針: 内部の逐語的思考過程（長文の思考連鎖）は記録しない。根拠は簡潔な要約・ルール参照・入力の必要最小限の抜粋に限定する。

#### Scenario: 最終応答に decision_summary を含める

- created_task_ids / suggested_memo_status とともに、decision_summary（要点・適用ルール・マッピング理由）が返る。

### Scenarios

（このセクションの個別シナリオは、上記の各 Requirement 配下に記載しました）

## マイグレーション（Migration Notes）

- 既存の 'taskstatus' enum に 'DRAFT' を追加する。
- 新規テーブル/カラムは不要。ダウングレード方針は、DRAFT を含むデータが存在する場合の取り扱い（例: DRAFT→TODO へマップまたはダウングレードをブロック）を定義する。
- 生成コマンド（実行は別工程）:

  ```powershell
  poe revision "add-draft-to-taskstatus"
  ```

- リビジョンでは環境に応じて enum 追加の実装を調整（PostgreSQL: ALTER TYPE、SQLite: テーブル再作成）。

## バリデーション（Validation）

- エージェントは、アクショナブルなメモに対して少なくとも 1 回のツール呼び出しを行うこと。
- ツールはアプリケーション層へ委譲し、Repository を直接操作しないこと。
- ルート → ステータスのマッピング、および「要レビュー」時の DRAFT 保存をユニットテストで確認すること。
- 最終応答に decision_summary が含まれ、上記の構造を満たすこと（長文の逐語的思考連鎖は含めない）。
