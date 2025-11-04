## 1. Implementation
- [x] 1.1 FAKE シード生成で空メモ時のタイトル/説明取得を安全化し、IndexError を防止する
- [x] 1.2 TaskDraft の ISO8601 検証および MemoToTaskAgent の due_date サニタイズを UTC "Z" や +00:00 オフセットに対応させる
- [x] 1.3 期日サニタイズと FAKE ルートのリグレッションを防ぐ単体テストを追加し、pytest を実行して挙動を確認する
