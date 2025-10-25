# Tasks: add-memo-to-task-agent

## 1. Implementation

- [ ] 1.1 TaskDraft スキーマ定義（title 必須、description/due_date/priority/tags/estimate_minutes 任意）
- [ ] 1.2 メモ → タスク変換エージェントの最小実装（LLM プロンプト＋構造化出力）
- [ ] 1.3 バリデーション：スキーマ整合性チェック（不正項目は除外、必須欠落はスキップ）
- [ ] 1.4 単体テスト：
  - [ ] 単純な箇条書きメモ → 複数タスク
  - [ ] 日付を含むメモ →due_date 抽出
  - [ ] 空メモ → 空配列
- [ ] 1.5 タグ分類（既存タグのみ選択）
  - [ ] 名前の部分一致（ケース非依存）でのタグ推定
  - [ ] 一致なし時は tags 未設定
  - [ ] 複数一致時は重複除去のうえ複数付与
- [ ] 1.6 Agent 統合フック（`generate_tasks_from_memo(memo: str) -> list[TaskDraft]`）

## 2. Integration (Optional / Next)

- [ ] 2.1 Service 層に TaskDraft[] 受け入れのユースケースを追加
- [ ] 2.2 UI/CLI からの起動導線（メモ入力 → タスク候補確認ダイアログ）

## 3. Validation

- [ ] 3.1 `openspec validate add-memo-to-task-agent --strict` が通る
- [ ] 3.2 `pytest -q` テストが緑
