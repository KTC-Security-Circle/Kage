# 検索APIガイド（Logic/Application 層）

本ドキュメントは、Kage のアプリケーション層に追加された検索APIの使い方をまとめたものです。最小限の実装で、部分一致・大文字小文字無視のキーワード検索を提供します。

## 共通ポリシー

- すべての検索は部分一致・大文字小文字無視です。
- `query` が空文字または空白のみの場合は空配列を返します（DBクエリは走らせません）。
- `with_details=True` を指定した場合、関連エンティティ（タグ/プロジェクト/メモ等）を事前ロードします。
- フィルタは狭める方向（AND）で適用し、タグは「いずれかを含む（OR）」でマッチさせます。

## API 一覧

### MemoApplicationService

```text
search(query: str, *, with_details: bool = False, status: MemoStatus | None = None, tags: list[UUID] | None = None) -> list[MemoRead]
```

- タイトル・本文を横断検索します。
- `status` が指定されている場合はサービスの `list_by_status` を活用して絞り込み。
- `tags` はリポジトリの `list_by_tag` を用い、指定されたタグのいずれかを持つメモのみを残します。

### TaskApplicationService

```text
search(query: str, *, with_details: bool = False, status: TaskStatus | None = None, tags: list[UUID] | None = None) -> list[TaskRead]
```

- サービスの `search_tasks` がタイトル・説明の両方を検索し、重複を除去します。
- `status` はサービスの `list_by_status` を用いて絞り込み。
- `tags` はリポジトリの `list_by_tag` を用いて OR 条件で絞り込み。

### ProjectService / ProjectApplicationService

```text
ProjectService.search_projects(query: str) -> list[ProjectRead]
ProjectApplicationService.search(query: str, *, status: ProjectStatus | None = None) -> list[ProjectRead]
```

- タイトルで検索します。
- Application 層では任意の `status` で追加絞り込みが可能です。

### TagApplicationService

```text
search(query: str) -> list[TagRead]
```

- `search_by_name` のエイリアスです。

### TerminologyApplicationService

```text
search(query: str | None = None, *, tags: list[UUID] | None = None, status: TermStatus | None = None, include_synonyms: bool = True) -> list[TermRead]
```

- サービス層の検索に委譲します。`include_synonyms=True` で同義語も検索対象。

## 簡単な使用例

```python
from logic.unit_of_work import SqlModelUnitOfWork
from logic.application.task_application_service import TaskApplicationService
from models import TaskStatus

app = TaskApplicationService(SqlModelUnitOfWork)

# 文字列で横断検索（タイトル・説明）
results = app.search("implement", with_details=True, status=TaskStatus.TODO)
for t in results:
    print(t.title)
```

## 注意点

- 高度な検索（フレーズ、正規表現、スコアリングなど）はサポートしていません。必要になった段階で別提案として拡張します。
- タグフィルタは OR 条件です。AND 条件が必要な場合はインターフェースを別途追加してください。
- ベクトル検索は非対応です（将来拡張）。
