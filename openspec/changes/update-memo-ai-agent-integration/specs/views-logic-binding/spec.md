# Capability: views-logic-binding

## MODIFIED Requirements

### Requirement: Application Service Boundary

MemosView の「AI でタスク生成」ボタンは MemoApplicationService に enqueue API を呼び出し、結果のジョブ ID とステータスを state へ反映しなければならない (MUST)。UI での処理は ViewState を通じて Pending/Available/Failed を更新し、直接 Presenter に状態を埋め込んではならない (MUST NOT)。

#### Scenario: Enqueue 呼び出し

- **GIVEN** ユーザーがメモ詳細で AI ボタンを押す
- **WHEN** View が ApplicationService.enqueue_memo_for_ai を呼ぶ
- **THEN** 返却されたジョブ ID/初期ステータスを state に記録し、UI が Pending へ遷移する

### Requirement: Asynchronous Operations

AI ジョブ完了通知は非同期で受け取り、View は `with_loading` とは別の listener/ポーリングで state を更新しなければならない (SHOULD)。ジョブ失敗時は既存の既知/未知エラー分類ポリシーに従う (MUST)。

#### Scenario: キュー完了通知

- **GIVEN** キュー内ジョブが完了し結果イベントが届く
- **WHEN** View が state.update_ai_result を呼び出す
- **THEN** ステータスが AVAILABLE へ遷移し、承認可能なタスク集合が描画される
