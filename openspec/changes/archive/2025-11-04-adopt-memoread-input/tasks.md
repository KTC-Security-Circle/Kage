## 1. 実装
- [x] 1.1 `MemoToTaskState` に `memo: MemoRead` を追加し、従来の `memo_text` 利用箇所を置き換える
- [x] 1.2 `MemoToTaskAgent` の入力生成・分岐ロジックを `memo.content` 参照に更新する
- [x] 1.3 メモアプリケーションサービスの Clarify / generate フローを `MemoRead` 契約へ更新し、呼び出し元を追従する

## 2. テスト
- [x] 2.1 既存ユニットテストを `MemoRead` 入力に合わせて更新し、新たなシナリオ（タイトル情報参照など）を追加する
- [x] 2.2 `poe test` ですべての関連テストスイートが成功することを確認する