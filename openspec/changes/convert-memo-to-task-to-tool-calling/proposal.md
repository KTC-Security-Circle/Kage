# 提案: MemoToTaskAgent を Tool Calling 化し、TaskDraft を用いずにタスクを永続化する

本提案は、MemoToTaskAgent を Tool Calling 方式へ移行し、TaskDraft を経由せずにタスクを DB へ直接保存するアーキテクチャ変更を定義します。ドラフト状態は新規の DraftStatus 型ではなく、TaskStatus に DRAFT（文字列は "draft"）を追加して表現します。ツールによる DB 変更は、必ず既存のアプリケーション層（ApplicationService）経由で実行します。

## 概要（Summary）

- MemoToTaskAgent の出力フローを構造化出力グラフから Tool Calling 方式へ置き換える。
- 実行時の TaskDraft は廃止し、タスクは直接 DB に保存する。
- DraftStatus 型は導入せず、TaskStatus に DRAFT を追加してドラフト状態を表現する（文字列は "draft"）。
- create_tasks / update_memo_status などのツールは、TaskApplicationService 等のアプリケーション層経由でデータ操作を行い、Repository を直接呼び出さない。
- エージェントの最終応答には、意思決定の要約（decision_summary）を含める（安全配慮した簡潔・構造化された根拠）。

## 背景・目的（Motivation）

- ツール呼び出し（Function/Tool Calling）により、決定的な副作用（DB 永続化）とリトライ容易性を確保する。
- AI 生成タスクをファーストクラスのエンティティとして扱う。レビューが必要なものは TaskStatus.DRAFT でシンプルに運用する。

## スコープ（Scope）

- コード: `src/agents/task_agents/memo_to_task/{agent.py, tools.py, prompt.py?}`、`src/models`、アプリケーション層サービスの利用。
- DB: 既存の `taskstatus` 列挙に `DRAFT` を追加（新規カラムは追加しない）。
- テスト: エージェントテストの更新と、ツールの単体テストを追加。
- ドキュメント: 本提案および詳細仕様（spec）を更新。

## 非対象（Out of Scope）

- DRAFT 専用の UI/UX（ビュー大規模変更）。
- マルチターンの複雑なツールループ（本変更では最小 1 回のツール実行を目標とする）。

## オープンな論点（Open Questions）

- 新規タスクの既定状態を常に DRAFT にするか、メモの意図に応じて運用状態（NEXT_ACTION/PROGRESS/WAITING 等）へ直接マップするか。
- 旧 `TaskDraft.route` → `Task.status` の最終マッピング（初期案は spec に記載）。
- ツールの冪等性（同一メモからの重複作成防止）方針。

## リスクと緩和策（Risks and Mitigations）

- マイグレーション: `taskstatus` 列挙へ `DRAFT` を追加。DB 種別（SQLite/PostgreSQL 等）ごとの差異に留意し、安全な適用とダウングレード方針を用意する。
- 互換性: 既存テスト・ヘルパー等で `TaskDraft` を参照している箇所は段階的に除去。エージェントの実行時出力としては使用しない。

## 設計ノート（Design Notes）

- すべての DB 変更はアプリケーション層サービス（例: `TaskApplicationService`, `MemoApplicationService`）経由で行う。ツールは薄いファサードとする。
- メモがアクショナブルな内容である場合、エージェントは少なくとも 1 回はツールを実行してタスクを永続化する。
- decision_summary は、適用ルール・抽出要点・各タスクのマッピング理由・検証注記などを短文で保持し、長文の思考連鎖は記録しない。

## 実行手順（Implementation Workflow：ここではコマンドのみ提示し、実行はしない）

1. マイグレーションリビジョンの作成（コマンドで実施）

   ```powershell
   # 変更名は例です。運用に合わせて調整してください。
   poe revision "add-draft-to-taskstatus"
   ```

2. 生成されたリビジョンの確認・編集

   - 目的: 既存の `taskstatus` enum に `DRAFT`（"draft"）を追加する。
   - 備考: 環境によっては Alembic の自動検出で enum 追加が拾われない場合がある。その場合は、
     - PostgreSQL: `ALTER TYPE taskstatus ADD VALUE 'DRAFT'` 等の実行をリビジョンに記述。
     - SQLite: テーブル再作成（一時テーブル経由）でチェック制約を更新する戦略をとる。

3. マイグレーションの適用（別途タイミングで実施）

   ```powershell
   poe migrate
   ```

4. エージェントとツールの実装（別フェーズ）

   - Tool Calling フローへの置換、アプリ層サービス呼び出しの配線、テスト更新を行う。

# Proposal: Convert MemoToTaskAgent to Tool Calling and Persist Tasks without TaskDraft

- Do NOT introduce a new DraftStatus type. Instead, add DRAFT as one of TaskStatus values.

## Motivation

## Scope

- DB: extend TaskStatus enum by adding DRAFT; Alembic migration to add 'DRAFT' to existing taskstatus enum (no new column).

- UI changes (views) to expose DRAFT-specific UX (out of scope for this change).

# 提案: MemoToTaskAgent を Tool Calling 化し、TaskDraft を使わずにタスクを永続化する

## 概要（Summary）

- MemoToTaskAgent の出力フローを構造化出力グラフから Tool Calling 方式へ置き換える。
- 実行時の TaskDraft は廃止し、タスクは直接 DB に保存する。
- 新しい DraftStatus 型は導入せず、TaskStatus に DRAFT（文字列は "draft"）を追加してドラフト状態を表現する。
- ツール（create_tasks, update_memo_status など）は既存のアプリケーション層（例: TaskApplicationService）経由でデータ操作を行い、リポジトリを直接叩かない。

## 背景・目的（Motivation）

- ツール呼び出し（Function/Tool Calling）による決定的な副作用（DB 永続化）とリトライ容易性を確保する。
- AI 生成タスクをファーストクラスのエンティティとして扱い、レビューが必要なものは TaskStatus.DRAFT で表現してシンプルに運用する。

## スコープ（Scope）

- コード: `src/agents/task_agents/memo_to_task/{agent.py, tools.py, prompt.py?}`、`src/models`、アプリケーション層のサービス利用。
- DB: 既存の `taskstatus` 列挙に `DRAFT` を追加（新規カラムは追加しない）。
- テスト: エージェントテストの更新と、ツールの単体テストを追加。
- ドキュメント: 本 OpenSpec 提案および詳細仕様（spec）を更新。

## 非対象（Out of Scope）

- DRAFT 専用 UI/UX（ビューの大きな変更）は対象外。
- マルチターンの複雑なツールループ。本変更では最小 1 回のツール実行に留める。

## オープンな論点（Open Questions）

- 新規作成タスクの既定状態を常に DRAFT にするか、メモの意図により運用状態（NEXT_ACTION/PROGRESS/WAITING など）へ直接マップするか。
- 旧 `TaskDraft.route` → `Task.status` の最終マッピング（初期案は spec 参照）。
- ツールの冪等性（重複作成防止）戦略。

## リスクと緩和策（Risks and Mitigations）

- マイグレーション: 既存の `taskstatus` 列挙に `DRAFT` を追加する必要がある。環境差（SQLite/PostgreSQL 等）に応じた安全な適用とダウングレード方針を明記する。
- 互換性: 既存コード（テスト・ヘルパー）で `TaskDraft` 型を参照している箇所は段階的に除去。エージェントの実行時出力としては使用しない。

## 設計ノート（Design Notes）

- すべての DB 変更はアプリケーション層サービス（例: `TaskApplicationService`, `MemoApplicationService`）経由で行う。ツールは薄いファサードとする。
- メモがアクショナブルな内容である場合、エージェントは少なくとも 1 回はツールを実行してタスクを永続化する。

## 実行手順（Implementation Workflow：コマンドは参考、ここでは実行しない）

1. マイグレーションリビジョンの作成（コマンドで実施）

````powershell
## Open Questions

- Whether newly created tasks default to DRAFT or mapped operational statuses depends on the memo context; baseline mapping is defined in spec below.

2) 生成されたリビジョンの確認・編集
- 目的: 既存の `taskstatus` enum に `DRAFT`（"draft"）を追加する。
- 環境によっては Alembic の自動検出で enum 追加が拾われない場合があるため、必要に応じて手動で enum 追加ロジック（例: PostgreSQL の `ALTER TYPE`, SQLite のテーブル再作成戦略）を記述する。

3) マイグレーションの適用（別途タイミングで実施）

```powershell
- Mapping from old TaskDraft.route → Task.status; initial mapping defined in spec below.


4) エージェントとツールの実装（別フェーズ）
- Tool Calling フローへの置換、アプリ層サービス呼び出しの配線、テスト更新を行う。
## Risks and Mitigations

- Migration risk: extend enum 'taskstatus' with 'DRAFT' safely across environments.
- Backward-compat: Keep TaskDraft schema types available for now for test/helpers, but the agent will not produce TaskDraft at runtime.

## Design Notes

- All DB mutations MUST go through Application layer services (e.g., TaskApplicationService, MemoApplicationService). Tools are thin façades.
- Tool Calling flow MUST execute at least one tool for task creation when the memo is actionable.
````
