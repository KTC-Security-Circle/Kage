# Capability: memo-to-task-agent

## MODIFIED Requirements

### Requirement: Integration Hook

MemoToTaskAgent を起動する公開 API (`generate_tasks_from_memo` など) は View 層からの「AI でタスク生成」アクションをトリガーとして呼び出されるよう Application Service 経由で公開しなければならない (MUST)。呼び出しは同期 UI から切り離され、即時にキューへジョブ ID を返すべきである (SHOULD)。

#### Scenario: AI ボタン押下でジョブ登録

- **GIVEN** ユーザーが MemosView の「AI でタスク生成」ボタンを押下する
- **WHEN** View が MemoApplicationService 経由で MemoToTaskAgent のフックを呼び出す
- **THEN** そのメモが生成キューに enqueue され、ジョブ ID がビューへ返り、進捗表示が更新される

### Requirement: Serialized Generation Queue

MemoToTaskAgent の実行は 1 件ずつ順序通りに処理する in-memory キューで管理しなければならない (MUST)。キューマネージャは将来的な永続化バックエンド差し替えを想定した抽象を提供し、現在はメモリ実装 s marking persistence extension points
An abstract interface/protocol that would allow backend replacement
Documentation about how to replace the in-memory implementation
Consider adding:

TODO comments at key extension points (e.g., \_jobs dictionary, enqueue, get_snapshot)
A Protocol or ABC defining the queue interface
Documentation about the persistence strategy ＋永続化 TODO コメントを残すこと (SHOULD)。キューイング済みメモが完了したら結果と suggested_memo_status を呼び出し元へ通知しなければならない (MUST)。

#### Scenario: 単一並列キュー

- **GIVEN** 同時に 3 件のメモが enqueue される
- **WHEN** キューワーカーが処理を開始
- **THEN** メモは FIFO 順に 1 件ずつ MemoToTaskAgent に渡され、処理中は他ジョブが開始されない

#### Scenario: 永続化への備え

- **GIVEN** 現実装が in-memory queue を利用している
- **WHEN** コードを確認
- **THEN** 将来の永続化キュー実装へ差し替えられるよう、インターフェースや TODO コメントで拡張ポイントが明記されている
