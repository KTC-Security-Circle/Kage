## 1. サービス/モデル基盤

- [x] 1.1 WeeklyReviewInsights 系の DTO(dataclass)と JSON シリアライズスキーマを追加する
- [x] 1.2 Task/MemoRepository へ期間指定・未処理抽出クエリを追加し、単体テストで条件分岐を確認する
- [x] 1.3 WeeklyReviewInsightsService を実装し、Task/Memo/Llm クライアント依存を DI 経由で解決する

## 2. ステップ別 AI ロジック

- [x] 2.1 成果サマリー生成プロンプト/レスポンス検証コードを追加し、肯定トーン+3 件要約を強制する
- [x] 2.2 ゾンビタスク検知+提案(分割・延期・Someday・削除)ロジックと整形コードを追加する
- [x] 2.3 未処理メモ棚卸しロジックを実装し、アクティブプロジェクトとの関連付け推論を含める

## 3. API/アプリ層

- [x] 3.1 Application サービスまたは Router 層に review insights フェッチ用の公開メソッド/エンドポイントを追加する
- [x] 3.2 エンドポイントの I/O バリデーション(期間指定、LLM 失敗時のフォールバック)を実装し単体テストする

## 4. テスト/検証

- [x] 4.1 WeeklyReviewInsightsService の pytest を追加し、リポジトリ/LLM クライアントをモックして各ステップの出力を確認する
- [x] 4.2 OpenAPI/JSONSchema や pydantic モデルのスナップショットテストでレスポンス形式を保証する
- [x] 4.3 `uv run poe test`で関連テスト群を実行し、README またはタスクメモに結果を記録する
