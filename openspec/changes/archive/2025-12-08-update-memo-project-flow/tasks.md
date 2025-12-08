## 1. 実装
- [x] 1.1 MemoToTaskAgent のスキーマ・出力に project 情報を追加し、FAKE レスポンスを更新する
- [x] 1.2 MemoApplicationService / MemoAiJobQueue で project 作成 + draft 永続化を実行し、ai_analysis_log v3 を書き込む
- [x] 1.3 MemosViewState / Presenter / View に project_info を表示する UI を追加し、ProjectsView への導線を実装する
- [x] 1.4 既存テスト更新と新規テスト（job queue、state、presenter）を追加する
- [x] 1.5 `uv run poe check` と `uv run poe test` を実行して結果を記録する
