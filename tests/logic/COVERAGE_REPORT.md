# Logic 層テストカバレッジレポート（最新）

最終更新: 2025-10-16（再計測）

## サマリ

- 総合カバレッジ: 79%（前回 78% → +1pt）
- 実行結果: 247 passed, 3 skipped（テスト全体。logic 配下の測定対象で集計）
- 主な改善: task_service/memo_service のテストを拡張し、task_service は 87% へ、memo_service は 73% へ上昇。light/extra テストの統合完了。

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
  - logic/application/project_application_service.py: 72%
  - logic/application/base.py: 64%
  - logic/application/apps.py: 0%（未対象の初期化コード）

- Infra
  - logic/unit_of_work.py: 99%
  - logic/factory.py: 91%

※ 上記は `uv run pytest tests/logic --cov=src/logic --cov-report=term-missing` の直近実測値から抜粋。

## 今後の優先課題（短期）

1. Service 層の底上げ（目標 85% 以上）

- memo*service の未テスト分岐追加（search_memos での search_by*\* 経路、convert_read_model 経路の網羅）
- project_service の残り分岐（update/convert_read_model 経路、force=True 経路）
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

- Service 層の追加テスト
  - TagService: get_by_name/search_by_name/get_or_create を追加、例外透過性と ReadModel 変換を確認（86%）
  - ProjectService: list_by_status の NotFound 透過、remove_task の NotFound 経路を追加（76%）
  - TaskService: light を本体へ統合。RepoRaiser/RepoUnexpected 経路、remove_tag（存在しないタグ/存在するタグ）を追加（87%）。
  - MemoService: 予期しない例外 wrap、get_all(with_details=True)、list_by_status NotFound 経路を追加。ダミーリポジトリに list_by_status を実装（73%）。

なお、保守性向上のため service テストの light/extra を統合しました。legacy ファイル（test_tag_service_light/extra.py, test_project_service_light/extra.py, test_task_service_light.py）は当面の安定性確保のため module-level skip のプレースホルダーとして残置しています（今後のクリーンアップ対象）。

## 実行方法（参考）

- すべての logic テスト＋カバレッジ
  - uv run pytest tests/logic --cov=src/logic --cov-report=term-missing

## 備考

- 目標（OpenSpec）: logic 配下 85% 以上（段階的に強制）。現時点では 76% のため、Service 層と Application 層改善を継続。
