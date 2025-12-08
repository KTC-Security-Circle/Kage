# memo-to-task-agent Specification

## Purpose
TBD - created by archiving change add-memo-to-task-agent. Update Purpose after archive.
## Requirements
### Requirement: Memo-to-Task Agent
MemoToTaskエージェントは `MemoRead` モデルを入力に受け取り、`memo.content` をもとに 0..N 件のタスク候補（TaskDraft[]）へ変換できなければならない (MUST)。
`MemoRead` に含まれる id/title/status などのメタ情報は Clarify/Organize 判定ロジックから参照できなければならない (MUST)。

#### Scenario: 箇条書きMemoReadから複数タスク
- **GIVEN** `MemoRead` の `content` に「- 牛乳を買う\n- 予算案を仕上げる」を設定する
- **WHEN** エージェントにその `MemoRead` を与える
- **THEN** title を持つ 2 件の TaskDraft が返る

#### Scenario: 空のMemoRead本文
- **GIVEN** `MemoRead.content` が空文字列
- **WHEN** エージェントにその `MemoRead` を与える
- **THEN** 空配列を返す

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

### Requirement: Integration Hook
アプリの Agent 統合ポイントから `generate_tasks_from_memo(memo: MemoRead) -> TaskDraft[]` を提供しなければならない (MUST)。
Clarify結果の suggested_memo_status を返す公開メソッドは `MemoRead` をそのままエージェント状態に受け渡し、`MemoRead.content` を本文として扱わなければならない (MUST)。

#### Scenario: サービス層からの `MemoRead` 呼び出し
- **GIVEN** サービス層が DB から取得した `MemoRead` を保持している
- **WHEN** フック関数にその `MemoRead` を渡す
- **THEN** TaskDraft[] が返り、Clarify結果に基づく suggested_memo_status が得られる

### Requirement: Clarify Workflow Mapping

メモを Clarify/Organize の決定木に沿って分類し、各 TaskDraft に配置先を示すルート情報を付与できなければならない (MUST)。

- 2 分以内でできる → route=progress（即実行タスクリスト）
- 自分がやるべきでない → route=waiting（連絡待ち/委譲の待機リスト）
- 特定の日にやる → route=calendar（due_date に日付を設定）
- 上記以外の単一ステップ → route=next_action（次のアクションリスト）
- 複数ステップが必要 → project_title を付与し、少なくとも 1 件の Next Action を含める

#### Scenario: 2 分ルール（即実行）

- **GIVEN** メモ「会議室の予約を今日すぐやる」
- **WHEN** エージェントを実行
- **THEN** 返却の TaskDraft に route=progress が設定される

#### Scenario: 委譲/待機

- **GIVEN** メモ「経理へ請求書の支払いを依頼」
- **WHEN** エージェントを実行
- **THEN** 返却の TaskDraft に route=waiting が設定される

#### Scenario: カレンダー（期日指定）

- **GIVEN** メモ「11/15 に健康診断の予約」
- **WHEN** エージェントを実行
- **THEN** 返却の TaskDraft に route=calendar と due_date（ISO8601）が設定される

#### Scenario: 次のアクション

- **GIVEN** メモ「見積依頼メールを送る」
- **WHEN** エージェントを実行
- **THEN** 返却の TaskDraft に route=next_action が設定される

#### Scenario: 複数ステップ（プロジェクト化）

- **GIVEN** メモ「引越し準備を進める」
- **WHEN** エージェントを実行
- **THEN** 返却に project_title が含まれ、少なくとも 1 件の route=next_action タスクが含まれる

### Requirement: Memo Status Suggestion

Clarify の結果に基づいてメモのステータス提案（suggested_memo_status）を返せなければならない (MUST)。

- 行動不要 → idea
- タスク化された場合 → active

#### Scenario: 行動不要（アイデア化）

- **GIVEN** メモ「未来のアイデアメモ：いつかやりたいこと」
- **WHEN** エージェントを実行
- **THEN** suggested_memo_status=idea が返る（TaskDraft は空の可能性あり）

#### Scenario: タスク化（アクティブ化）

- **GIVEN** メモ「週報を作成」
- **WHEN** エージェントを実行
- **THEN** TaskDraft が 1 件以上返り、suggested_memo_status=active が返る

### Requirement: Tag Classification

メモ内容から既に登録済みのタグを推定し、TaskDraft.tags に付与できなければならない (MUST)。新規タグの自動作成は行ってはならない (MUST NOT)。

#### Scenario: 単一タグの一致（名前一致）

- **GIVEN** 既存タグに「請求書」があり、メモに「請求書の送付」と含まれる
- **WHEN** エージェントを実行
- **THEN** TaskDraft.tags に ["請求書"] が含まれる

#### Scenario: 複数タグの一致

- **GIVEN** 既存タグに「支払い」「経理」があり、メモに「経理へ支払い依頼」と含まれる
- **WHEN** エージェントを実行
- **THEN** TaskDraft.tags に ["支払い", "経理"] の両方が含まれる

#### Scenario: 一致なし

- **GIVEN** 既存タグに一致がない
- **WHEN** エージェントを実行
- **THEN** TaskDraft.tags は空、または未設定のままである

<!-- OPENSPEC:END -->

### Requirement: Draft Task Persistence

MemoToTaskAgent の結果は `MemoAiJobQueue` を通じて Task ドメインへ即時永続化しなければならない (MUST)。エージェントが返した各 TaskDraft は `TaskApplicationService.create` を用いて `TaskStatus.DRAFT` の Task レコードとして保存し、`memo_id` を必ず紐付けること (MUST)。永続化完了後は `ai_analysis_log` に参照用の `draft_task_ids` と route 情報を記録し、本文やタグなどの真実は Task テーブルを参照しなければならない (MUST)。

#### Scenario: Draft Persistence On Job Success

- **GIVEN** MemoAiJobQueue が MemoToTaskAgent の応答で 2 件の候補を受け取った
- **WHEN** ジョブが SUCCEEDED へ遷移する
- **THEN** 2 件の Task が `TaskStatus.DRAFT` で作成され、各 Task の ID と route が `ai_analysis_log` に保存される

### Requirement: Approval Uses Task Update/Delete

AI 提案タスクの承認・再生成・削除は Task ドメイン API を通じて実行しなければならない (MUST)。承認時は Draft Task の route に応じて TaskStatus を更新する（progress→PROGRESS、waiting→WAITING、calendar→TODAYS もしくは TODO ＋期限、next_action→TODO）(MUST)。破棄する場合は `TaskApplicationService.delete` を使用し、`MemoService` との関連を解除する (MUST)。

#### Scenario: Approve Draft Task

- **GIVEN** route=progress の Draft Task が存在する
- **WHEN** ユーザーが承認ボタンを押す
- **THEN** TaskStatus が PROGRESS へ更新され、Task は既存ビューにも表示される

#### Scenario: Delete Draft Task

- **GIVEN** Memo 詳細で Draft Task を削除したい
- **WHEN** ユーザーが削除操作を行う
- **THEN** TaskApplicationService.delete が呼ばれ、Task と Memo のリンクおよび `ai_analysis_log` 参照が削除される

