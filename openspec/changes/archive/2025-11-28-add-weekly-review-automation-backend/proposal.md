## Why

週次レビュー画面に「成果サマリー」「滞留タスク整理」「未処理メモの棚卸し」を自動生成するバックエンド機能が存在せず、ユーザーが全てのリストを手作業で確認する必要がある。タスク完了実績のモチベーション向上、長期停滞タスクの整理、メモからタスク化されていない情報の掘り起こしを AI が肩代わりする設計を先に固めたい。

## What Changes

- WeeklyReviewInsights サービスを追加し、週次レビュー 3 ステップのデータ収集と LLM 呼び出しを一括管理する
- タスク/メモリポジトリへ期間フィルタや「未タスク化メモ」などの集計クエリを追加する
- 成果サマリー、ゾンビタスク提案、メモ棚卸し提案を返す構造化 DTO を定義し、API(backend only)で提供する
- Review 用 LLM プロンプト/レスポンススキーマとガードレール(肯定トーン、提案メニュー)を追加する
- pytest ベースのサービス/リポジトリテストを用意し、想定データに対するレスポンス加工を検証する

## Impact

- Affected specs: weekly-review-automation (新規)
- Affected code: `src/logic/services/task_service.py`, `src/logic/services/memo_service.py`, `src/logic/application`, `src/agents`, `src/models`, `tests/logic/*`
