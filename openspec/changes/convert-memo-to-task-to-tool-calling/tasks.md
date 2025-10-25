# タスク一覧（Tasks）

1. モデル・仕様の合意

   - TaskStatus に DRAFT（文字列は "draft"）を追加する設計を確定（新規カラムは追加しない）。

2. マイグレーションの作成（コマンドのみ提示）

   - リビジョン生成: `poe revision "add-draft-to-taskstatus"`
   - リビジョン内容: 既存の `taskstatus` enum に 'DRAFT' を追加（環境に応じて ALTER TYPE もしくはテーブル再作成）。
   - 適用手順: `poe migrate`（適用は実装フェーズで実行）。

3. ツール設計（アプリ層経由）

   - create_tasks: 入出力・エラーモデル・ルート → ステータスマッピングを確定。永続化は TaskApplicationService 経由。
   - update_memo_status: 入出力・エラーモデルを確定。更新は MemoApplicationService 経由。

4. エージェントの Tool Calling 化設計

   - LLM へのツールバインド、最小 1 回のツール実行、最終応答（created_task_ids と suggested_memo_status）の構造を定義。
   - 最終応答へ decision_summary を追加（適用ルール / 抽出要点 / 各タスクの選定理由 / 検証注記 / 信頼度）。

5. テスト方針の更新

   - ルート → ステータスマッピング、DRAFT（要レビュー時）の保存、アプリ層経由呼び出しの検証をユニットテストで担保。
   - decision_summary の構造と内容（簡潔・構造化、長文思考の不含）を検証。

6. 品質ゲート
   - ruff / pyright / pytest をパスする実装計画を明記（実行は実装フェーズ）。
