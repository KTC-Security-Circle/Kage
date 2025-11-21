# Logic 層テストカバレッジレポート（最新）

最終更新: 2025-10-17（サービス層拡張テスト後の再計測）

## サマリ

- 総合カバレッジ: 89.9%（前回 80% → +9.9pt）
- 実行結果: 232 passed（logic スイートのみ計測）
- 主な改善: ApplicationServices の初期化契約を網羅し、service/base の例外ラップ経路と memo/project の細部を追加検証。

## モジュール別ハイライト（抜粋）

- Repositories

  - logic/repositories/task.py: 95%
  - logic/repositories/project.py: 94%
  - logic/repositories/memo.py: 91%
  - logic/repositories/tag.py: 91%
  - logic/repositories/base.py: 83%

- Services（要改善）

  - logic/services/task_service.py: 87%
  - logic/services/settings_service.py: 99%
  - logic/services/memo_service.py: 92%
  - logic/services/project_service.py: 90%
  - logic/services/tag_service.py: 86%
  - logic/services/base.py: 94%

- Application

  - logic/application/task_application_service.py: 100%
  - logic/application/memo_application_service.py: 100%
  - logic/application/tag_application_service.py: 94%
  - logic/application/project_application_service.py: 100%
  - logic/application/base.py: 100%
  - logic/application/apps.py: 83%（DI コンテナ初期化周りを追加）
  - logic/application/one_liner_application_service.py: 37%（未着手の主要対象）

- Infra
  - logic/unit_of_work.py: 99%
  - logic/factory.py: 91%

※ 上記は `uv run pytest tests/logic --cov=src/logic --cov-report=term-missing` の直近実測値から抜粋。

## 実行方法（参考）

- すべての logic テスト＋カバレッジ
  - uv run pytest tests/logic --cov=src/logic --cov-report=term-missing

## 備考

- 目標（OpenSpec）: logic 配下 85% 以上（段階的に強制）。現時点で 89.9% を確保。環境変数 LOGIC_COV_THRESHOLD=85 を指定すると CI で 85% を強制できる。

## 今後の優先課題（短期）

1. `one_liner_application_service` のテスト整備

- 現状 37%。UnitOfWork 連携とハッピーパス／エラー伝搬を追加する。

1. Application 層初期化コードの残タスク

- `ApplicationServices.configure` のバリデーション周りと `apps.py` 内の例外経路を補完する。

1. repository/base のエラーパス厳密化

- 83% で足踏み。NotFound と Integrity エラーの再現テストを追加する。

## 実施済み（本更新での差分）

- `tests/logic/application/test_apps.py` を追加し、DI キャッシュ／リセット／例外分岐を網羅。
- `tests/logic/services/test_memo_service.py` に検索重複排除・タグ／タスク付与・例外ラップを追加。
- `tests/logic/services/test_project_service.py` にタスク削除成功パスと強制削除経路を追加。
- `tests/logic/services/test_service_base_conversion.py` で `convert_read_model` の単体／配列ハンドリングを網羅。
- `scripts/run_logic_cov.py` で logic 限定カバレッジを 80%→85% 超えに引き上げ、実測 89.9% を確認。
