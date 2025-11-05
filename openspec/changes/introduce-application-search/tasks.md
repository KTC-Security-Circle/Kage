# Tasks: introduce-application-search

## 1. Implementation

- [ ] 1.1 Memo Application: `MemoApplicationService` に `search(query: str, with_details: bool=False) -> list[MemoRead]` を追加（`MemoService.search_memos` を呼び出し）
- [ ] 1.2 Task Repository: `search_by_description(query, with_details=False)` を追加（部分一致・大小無視）
- [ ] 1.3 Task Service: `search_tasks(query: str, with_details: bool=False) -> list[TaskRead]` を追加（title/description を統合し重複除去）
- [ ] 1.4 Task Application: `TaskApplicationService` に `search(query: str, with_details: bool=False) -> list[TaskRead]` を追加
  - [ ] Task フィルタ: `status: TaskStatus | None`, `tags: list[UUID] | None` を search にオプション追加（Repository で `list_by_status`/タグJOINを活用）
- [ ] 1.5 Project Service: `search_projects(query: str) -> list[ProjectRead]` を追加（Repository の `search_by_title` を活用）
- [ ] 1.6 Project Application: `ProjectApplicationService` に `search(query: str) -> list[ProjectRead]` を追加
  - [ ] Project フィルタ: `status: ProjectStatus | None` を search にオプション追加（`list_by_status` を活用）
- [ ] 1.7 Tag Application: `TagApplicationService` に `search(query: str) -> list[TagRead]` を追加（Service の `search_by_name` を委譲）
- [ ] 1.8 Terminology Application: `TerminologyApplicationService` に `search(query: str | None, tags: list[UUID] | None, status: TermStatus | None, include_synonyms: bool=True) -> list[TermRead]` を追加（Service の `search` を委譲）
  - [ ] Memo フィルタ: `status: MemoStatus | None`, `tags: list[UUID] | None` を search にオプション追加（Repository の `list_by_status`/`list_by_tag` を活用）

## 2. Tests

- [ ] 2.1 Repository: `TaskRepository.search_by_description` のユニットテスト（ヒット/未ヒット/大文字小文字/部分一致）
- [ ] 2.2 Service: `TaskService.search_tasks` のユニットテスト（重複除去、with_details 反映）
- [ ] 2.3 Application: `MemoApplicationService.search` と `TaskApplicationService.search` のユニットテスト（空クエリで空配列、正常系、with_details）
- [ ] 2.4 Service: `ProjectService` の検索ユニットテスト（タイトル一致/未一致）
- [ ] 2.5 Application: `ProjectApplicationService.search` のユニットテスト
- [ ] 2.6 Application: `TagApplicationService.search` のユニットテスト
- [ ] 2.7 Application: `TerminologyApplicationService.search` のユニットテスト（synonyms含む/除外、タグ/ステータスフィルタ）

## 3. Docs

- [ ] 3.1 開発ドキュメント更新: docs/dev/logic/README もしくは該当箇所に検索 API の使い方を追記
- [ ] 3.2 変更履歴: OpenSpec の変更を README/CHANGELOG にリンク（必要に応じて）

## 4. Validation

- [ ] 4.1 `openspec validate introduce-application-search --strict` を通過
- [ ] 4.2 `uv run poe test` が成功、関連カバレッジに回帰がないことを確認
