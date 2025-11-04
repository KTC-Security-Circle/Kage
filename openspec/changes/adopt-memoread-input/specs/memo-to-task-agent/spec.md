## MODIFIED Requirements
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

### Requirement: Integration Hook
アプリの Agent 統合ポイントから `generate_tasks_from_memo(memo: MemoRead) -> TaskDraft[]` を提供しなければならない (MUST)。
Clarify結果の suggested_memo_status を返す公開メソッドは `MemoRead` をそのままエージェント状態に受け渡し、`MemoRead.content` を本文として扱わなければならない (MUST)。

#### Scenario: サービス層からの `MemoRead` 呼び出し
- **GIVEN** サービス層が DB から取得した `MemoRead` を保持している
- **WHEN** フック関数にその `MemoRead` を渡す
- **THEN** TaskDraft[] が返り、Clarify結果に基づく suggested_memo_status が得られる