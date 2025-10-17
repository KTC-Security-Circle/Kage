# Logic 層テストカバレッジレポート（最新）

最終更新: 2025-10-17（再計測）

## サマリ

- 総合カバレッジ: 80%（前回 79% → +1pt）
- 実行結果: 210 passed（logic スイートのみ計測）
- 主な改善: application 層（task/project/base）が 100% に到達。UnitOfWork の例外経路テストを追加し、Factory 系の冗長テストを整理。

## モジュール別ハイライト（抜粋）

- Repositories

  - logic/repositories/task.py: 95%
  - logic/repositories/project.py: 94%
  - logic/repositories/memo.py: 91%
  - logic/repositories/tag.py: 91%
  - logic/repositories/base.py: 83%

- Services（要改善）

  - logic/services/task_service.py: 87%（+7pt）
  - logic/services/settings_service.py: 99%
  - logic/services/memo_service.py: 73%（+5pt）
  - logic/services/project_service.py: 76%
  - logic/services/tag_service.py: 86%
  - logic/services/base.py: 88%

- Application

  - logic/application/task_application_service.py: 100%
  - logic/application/memo_application_service.py: 100%
  - logic/application/tag_application_service.py: 94%
  - logic/application/project_application_service.py: 100%
  - logic/application/base.py: 100%
  - logic/application/apps.py: 0%（未対象の初期化コード）

- Infra
  - logic/unit_of_work.py: 99%
  - logic/factory.py: 91%

※ 上記は `uv run pytest tests/logic --cov=src/logic --cov-report=term-missing` の直近実測値から抜粋。

- 今後の優先課題（短期）

1. Service 層の底上げ（目標 85% 以上）

- memo_service の未テスト分岐（convert_read_model、search 系の失敗パス）
- project_service の force=True 経路と convert_read_model
- service/base.py のログ分岐・例外ラップパス

1. アプリケーション初期化コードの扱い

- logic/application/apps.py は現状 0%。E2E/結合テストでの間接カバー方針を決める

1. Repository の残り細部

- base.py の NotFound/更新・削除失敗パスをもう一段厳密に

- 実施済み（この更新での差分）

- TaskApplicationService: with_details 分岐と削除の戻り値検証を追加
- ProjectApplicationService: バリデーション/削除失敗/一覧 API を網羅し 100% 達成
- BaseApplicationService: get_instance シングルトン契約のテストを追加し 100% 達成
- UnitOfWork: 例外時 rollback 呼び出しと get_service 経路の直接検証を追加
- Factory テスト: キャッシュ関連の重複ケースを統合し、命名を整理
- poe test-cov: scripts/run_logic_cov.py 経由で logic に限定したカバレッジ計測と閾値（既定 80%、環境変数で 85% へ引き上げ可能）を強制

## 実行方法（参考）

- すべての logic テスト＋カバレッジ
  - uv run pytest tests/logic --cov=src/logic --cov-report=term-missing

## 備考

- 目標（OpenSpec）: logic 配下 85% 以上（段階的に強制）。現時点では 80% のため、Service 層中心の改善を継続。環境変数 LOGIC_COV_THRESHOLD=85 を指定すると CI で 85% を強制できる。
