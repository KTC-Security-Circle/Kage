## 1. Agent / Domain ロジック

- [ ] 1.1 `WeeklyReviewTaskAgent` を task_agents/weekly_review_actions に追加し、split 用の構造化レスポンス + 単体テストを実装する
- [ ] 1.2 WeeklyReviewActionService (domain) と WeeklyReviewApplicationService.apply_actions API を実装し、split/someday/delete 決定を TaskApplicationService へ橋渡しするテストを書く

## 2. UI / Controller

- [ ] 2.1 WeeklyReviewController に決定 DTO の構築と action API 呼び出し + 結果集計のロジックを追加する
- [ ] 2.2 WeeklyReviewView Step2 の UI を更新し、実行ボタン・ローディング・再取得処理を実装してテストで状態遷移を検証する

## 3. QA

- [ ] 3.1 `uv run poe check` と `uv run poe test` を実行し、主要な WeeklyReview 関連テストを通過させる
