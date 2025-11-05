# Proposal: アプリケーション層に検索機能を横断追加（全テーブル対象）

<!-- OPENSPEC:START -->

## Why

テーブルを持つ主要エンティティで横断検索できる機能が不足しており、UI/CLI/エージェントからの利用で「見つける」体験が弱い。既に Repository/Service 層には一部検索機能が存在するが、Application 層が提供していない領域があり、統一されたエントリポイントがないため、セッション管理や with_details の扱いが各呼び出し元に漏れている。

## What Changes

- 方針: 「テーブルがあり、検索機能を追加したほうが良いものにはすべて導入」する。
- Application 層に横断的な検索 API を追加（Unit of Work を内包し、View/CLI から簡潔に利用可能にする）
- 初期対象: Memo / Task / Project / Tag / Term（Terminology）
- タスクは Service/Repository に不足している検索（description を含む部分一致）を追加
- Project は Service/Application 層に検索公開を追加（Repository の title 検索を活用）
- Tag は Application 層で `search(query)` を提供（Service の search_by_name を委譲；with_details は将来拡張）
- Terminology は Application 層で `search(query, tags, status, include_synonyms)` を提供（Service の search を委譲）
- Memo/Task は `status` や `tags` によるフィルタをサポート（Task は tags、Memo は tags／OR/AND は将来拡張）
- Project は `status` フィルタをサポート
- 共通の呼び出しパラメータ（query, with_details）に optional filters を加え、失敗時の動作は「例外ではなく空配列」を基本とする
- 最小実装（ページングや高度なフィルタは将来拡張とし SHOULD レベルで仕様化）

## Impact

- 影響する仕様（capabilities）:
  - memo-search（新規）
  - task-search（新規）
  - project-search（新規）
  - tag-search（新規）
  - term-search（新規）
- 影響するコード:
  - `src/logic/application/memo_application_service.py`
  - `src/logic/application/task_application_service.py`
  - `src/logic/application/project_application_service.py`
  - `src/logic/application/tag_application_service.py`
  - `src/logic/application/terminology_application_service.py`
  - `src/logic/services/task_service.py`
  - `src/logic/services/project_service.py`
  - `src/logic/services/tag_service.py`
  - `src/logic/services/terminology_service.py`
  - `src/logic/repositories/task.py`
  - `src/logic/repositories/project.py`
  - `src/logic/repositories/tag.py`
  - `src/logic/repositories/term.py`
  - テスト: `tests/logic/application/**`, `tests/logic/services/**`, `tests/logic/repositories/**`

## Non-goals

- 本提案では高度なランキング/スコアリングや AND/OR の複合条件検索は行わない
- インデックス最適化や検索バックエンドの変更は対象外（必要になった時点で別提案）

## Success Criteria

- Application 層から `search(query, with_details=False)` 相当の API で Memo/Task/Project/Tag/Term の検索が可能
- キーワード部分一致（大文字小文字を無視）でタイトル（および内容/説明/キー/名前）にヒットした結果が返る
- with_details=True で関連（タグ/プロジェクト/メモ-タスク関連/同義語）が読み込まれる（Tag は将来拡張）

<!-- OPENSPEC:END -->
