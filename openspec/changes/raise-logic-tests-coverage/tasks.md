# Tasks: logic テストカバレッジ向上

<!-- OPENSPEC:START -->

1. [x] 設備: 既存 tests/logic を走らせ、現状の失敗とカバレッジ穴を収集 (pytest -q, --cov=src/logic)
2. [x] Service 層の例外・分岐テストを追加 (TaskService 一部: delete(force=False), remove_tag 未存在, list_by_status 未存在)
3. [x] Repository 層の例外・クエリ分岐テストを追加 (Task: list_by_status with_details=True)
4. [x] Application 層の不足シナリオを補完 (成功/失敗、境界値)
5. [x] 軽量統合: UnitOfWork/Factory のエッジ・ロールバック経路
6. [x] 冗長テストの整理とテスト名の明確化 (命名規約の統一)
7. [x] カバレッジ閾値の段階設定と CI 反映 (tooling)
8. [x] ドキュメント更新: tests/logic/COVERAGE_REPORT.md を刷新
9. [x] Service 層の残課題整理とカバレッジ 85% 達成 (memo_service convert_read_model、project_service force=True など)
10. [ ] Application 初期化コード (logic/application/apps.py など) のカバレッジ方針を策定

検証:

- poe test-cov を利用して src/logic の term-missing を確認
- 代表的な失敗パスがテストで再現されること
- 実行時間の増加が 20% 以内であること

依存関係:

- 既存のフィクスチャ (tests/logic/conftest.py, helpers.py) を流用
- DB マイグレーションは不要 (インメモリ/一時 DB)

<!-- OPENSPEC:END -->
