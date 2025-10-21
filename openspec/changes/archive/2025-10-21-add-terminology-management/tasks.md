# Tasks: Terminology Management

<!-- OPENSPEC:START -->

- [x] 1. DB スキーマ追加（terms, synonyms, term_tags）と Alembic マイグレーション（タグは既存 `tags` を使用）
   - Validation: `uv run poe migrate` が成功し、テーブルが作成される（`tags` は既存のまま）
- [x] 2. Models/Repositories/Services の追加（CRUD/検索/同義語/タグ）
   - Validation: ユニットテスト（happy + NotFound + 既存キーエラー）
- [x] 3. インポート/エクスポート（CSV/JSON）ロジックとテスト
   - Validation: 100 件往復でデータ一致
- [x] 4. for_agents API（top-k 抽出/整形）の追加とテスト
   - Validation: 指定タグ/除外タグ/同義語含めた抽出が期待通り
- [ ] 5. UI: 本提案のスコープ外（別提案にて対応）
- [x] 6. 設定/DI 統合（Container/UnitOfWork へ登録）
   - Validation: 既存アプリ起動 + ページ表示
- [x] 7. ドキュメント: README/docs 追記（運用手順、バックアップ、制限）
   - Validation: チェックリストを満たす
- [x] 8. Vector Index 抽象の雛形と設定フラグ（未実装の場合は no-op）
   - Validation: オフ時に動作を変えない

<!-- OPENSPEC:END -->
