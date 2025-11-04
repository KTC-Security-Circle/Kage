## Why
メモ→タスク変換エージェントの入力が素の文字列で渡されているため、メモIDやタイトルなどの文脈情報を参照できず、将来の判定ロジック拡張に制約があるため。

## What Changes
- エージェントの状態入力を `MemoRead` モデル経由に置き換え、本文は `memo.content` から参照するよう仕様化する
- アプリケーションサービスの公開メソッド・内部フックを `MemoRead` を受け取る契約へ更新する (**BREAKING**)
- 既存の Clarify/Organize 判定で `MemoRead` に含まれる付帯情報（タイトル・ステータスなど）を渡せることを確認するテスト整備を追記する

## Impact
- Affected specs: memo-to-task-agent
- Affected code: src/agents/task_agents/memo_to_task/state.py, src/agents/task_agents/memo_to_task/agent.py, src/logic/application/memo_application_service.py, tests/logic/application/test_memo_application_service.py