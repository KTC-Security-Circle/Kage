# Logic 層テストカバレッジレポート（最新）

最終更新: 2025-10-16

## サマリ

- 総合カバレッジ: 76%（前回 75% → +1pt）
- 実行結果: 190 件 すべて成功（pytest）
- 主な改善: TaskRepository の分岐網羅により 53% → 95% へ大幅上昇

## モジュール別ハイライト（抜粋）

- Repositories

  - logic/repositories/task.py: 95%
  - logic/repositories/project.py: 94%
  - logic/repositories/memo.py: 91%
  - logic/repositories/tag.py: 91%
  - logic/repositories/base.py: 83%

- Services（要改善）

  - logic/services/task_service.py: 80%
  - logic/services/settings_service.py: 99%
  - logic/services/memo_service.py: 68%
  - logic/services/project_service.py: 68%
  - logic/services/tag_service.py: 68%
  - logic/services/base.py: 83%

- Application

  - logic/application/task_application_service.py: 100%
  - logic/application/memo_application_service.py: 100%
  - logic/application/tag_application_service.py: 94%
  - logic/application/project_application_service.py: 72%
  - logic/application/base.py: 64%
  - logic/application/apps.py: 0%（未対象の初期化コード）

- Infra
  - logic/unit_of_work.py: 99%
  - logic/factory.py: 91%

※ 上記は `uv run pytest tests/logic --cov=src/logic --cov-report=term-missing` の直近実測値から抜粋。

## 今後の優先課題（短期）

1. Service 層の底上げ（目標 85% 以上）

   - memo_service / project_service / tag_service の未テスト分岐
   - 失敗パス（RepositoryError ラップ、想定外例外の wrap）の網羅

2. Application 層の不足補完

   - project_application_service のハッピーパス＋失敗系の追加
   - apps.py は初期化コードのため、E2E/統合実行テストでの間接カバーを検討

3. Repository の残り細部
   - base.py の NotFound/更新・削除失敗パスをもう一段厳密に

## 実施済み（この更新での差分）

- TaskRepository の以下分岐を網羅
  - add_tag/remove_tag/remove_all_tags（重複追加の冪等性、未関連削除、空時全削除、NotFound）
  - list_by_project / list_by_status / search_by_title の with_details 分岐と未ヒット時 NotFound

## 実行方法（参考）

- すべての logic テスト＋カバレッジ
  - uv run pytest tests/logic --cov=src/logic --cov-report=term-missing

## 備考

- 目標（OpenSpec）: logic 配下 85% 以上（段階的に強制）。現時点では 76% のため、Service 層と Application 層改善を継続。
