# Tags View 実装TODO

このファイルは、Tags View の完全な実装に必要なロジック部分の実装タスクをまとめたものです。

## 1. ApplicationService層の実装

### 1.1 TagApplicationService

**ファイル**: `src/logic/application/tag_application_service.py`

**必要なメソッド**:
- `get_all_tags() -> list[Tag]`: 全タグを取得
- `get_tag_by_id(tag_id: str) -> Tag | None`: IDでタグを取得
- `create_tag(name: str, color: str, description: str) -> Tag`: タグを新規作成
- `update_tag(tag_id: str, name: str, color: str, description: str) -> Tag`: タグを更新
- `delete_tag(tag_id: str) -> bool`: タグを削除（カスケード: Task_Tag, Memo_Tag）
- `get_tag_item_counts(tag_name: str) -> dict[str, int]`: タグのアイテム件数を取得

**依存**:
- `TagRepository` (src/logic/repositories/tag.py)
- `Tag` model (src/models/tag.py)

**注意事項**:
- 削除時は関連メモ・タスクが存在する場合、ユーザーに警告を表示すべき
- トランザクション管理が必要（UnitOfWork パターン）

---

### 1.2 MemoApplicationService 拡張

**ファイル**: `src/logic/application/memo_application_service.py`

**追加が必要なメソッド**:
- `get_memos_by_tag_name(tag_name: str) -> list[Memo]`: タグ名で関連メモを取得

**実装方針**:
- Memo_Tag 中間テーブルを JOIN してフィルタリング
- または `src/logic/queries/memo_queries.py` に専用クエリを追加

---

### 1.3 TaskApplicationService 拡張

**ファイル**: `src/logic/application/task_application_service.py`

**追加が必要なメソッド**:
- `get_tasks_by_tag_name(tag_name: str) -> list[Task]`: タグ名で関連タスクを取得

**実装方針**:
- Task_Tag 中間テーブルを JOIN してフィルタリング
- または `src/logic/queries/task_queries.py` に専用クエリを追加

---

## 2. Queries層の実装

### 2.1 TagQueries

**ファイル**: `src/logic/queries/tag_queries.py` (新規作成 or 拡張)

**必要なクエリ**:
- `count_memos_by_tag(tag_name: str) -> int`: タグに紐づくメモ件数
- `count_tasks_by_tag(tag_name: str) -> int`: タグに紐づくタスク件数

**実装方針**:
- COUNT() クエリで効率的に件数を取得（全件取得して len() は非効率）
- SQLModel の select() + func.count() を使用

---

### 2.2 MemoQueries 拡張

**ファイル**: `src/logic/queries/memo_queries.py`

**追加が必要なクエリ**:
- `get_memos_by_tag_name(tag_name: str) -> list[Memo]`

**実装例**:
```python
from sqlmodel import select
from models.memo import Memo
from models.memo_tag import MemoTag
from models.tag import Tag

def get_memos_by_tag_name(session: Session, tag_name: str) -> list[Memo]:
    statement = (
        select(Memo)
        .join(MemoTag, Memo.id == MemoTag.memo_id)
        .join(Tag, MemoTag.tag_id == Tag.id)
        .where(Tag.name == tag_name)
    )
    return session.exec(statement).all()
```

---

### 2.3 TaskQueries 拡張

**ファイル**: `src/logic/queries/task_queries.py`

**追加が必要なクエリ**:
- `get_tasks_by_tag_name(tag_name: str) -> list[Task]`

**実装例**:
```python
from sqlmodel import select
from models.task import Task
from models.task_tag import TaskTag
from models.tag import Tag

def get_tasks_by_tag_name(session: Session, tag_name: str) -> list[Task]:
    statement = (
        select(Task)
        .join(TaskTag, Task.id == TaskTag.task_id)
        .join(Tag, TaskTag.tag_id == Tag.id)
        .where(Tag.name == tag_name)
    )
    return session.exec(statement).all()
```

---

## 3. UI Components の実装

### 3.1 TagCreateDialog

**ファイル**: `src/views/tags/components/tag_create_dialog.py` (新規作成)

**目的**: タグ新規作成ダイアログ

**Props**:
- `on_submit: Callable[[str, str, str], None]`: 作成ボタン押下時のコールバック（name, color, description）
- `on_cancel: Callable[[], None]`: キャンセルボタン押下時のコールバック

**機能**:
- タグ名入力（必須）
- カラー選択（カラーパレットダイアログ統合）
- 説明入力（任意）
- バリデーション（名前の重複チェック、空文字チェック）

**参考**: `src/views_old/template/src/components/TagsScreen.tsx` のモーダル実装

---

### 3.2 TagEditDialog

**ファイル**: `src/views/tags/components/tag_edit_dialog.py` (新規作成)

**目的**: タグ編集ダイアログ

**Props**:
- `tag: TagDict`: 編集対象のタグデータ
- `on_submit: Callable[[str, str, str, str], None]`: 更新ボタン押下時のコールバック（tag_id, name, color, description）
- `on_cancel: Callable[[], None]`: キャンセルボタン押下時のコールバック

**機能**:
- 既存タグ情報の表示（デフォルト値）
- TagCreateDialog と同様の入力・バリデーション
- 削除ボタンの追加（確認ダイアログ表示）

---

### 3.3 ColorPaletteDialog

**ファイル**: `src/views/tags/components/color_palette_dialog.py` (新規作成 or 既存を統合)

**目的**: カラーパレット選択ダイアログ

**Props**:
- `selected_color: str`: 現在選択されている色（HEX）
- `on_select: Callable[[str], None]`: 色選択時のコールバック

**機能**:
- `theme.TAG_COLOR_PALETTE` を使用してカラーグリッドを表示
- 選択中の色をハイライト
- カスタムカラー入力機能（オプション）

**参考**: `src/views/theme.py` の `TAG_COLOR_PALETTE`

---

## 4. Controller の依存注入

### 4.1 TagsController の修正

**ファイル**: `src/views/tags/controller.py`

**変更内容**:
```python
class TagsController:
    def __init__(
        self,
        state: TagsViewState,
        tag_service: TagApplicationService,
        memo_service: MemoApplicationService,
        task_service: TaskApplicationService,
    ) -> None:
        self.state = state
        self.tag_service = tag_service
        self.memo_service = memo_service
        self.task_service = task_service
```

**注意**:
- 依存注入は `src/logic/container.py` で管理
- View初期化時にコンテナからサービスを取得して注入

---

## 5. ルーティング統合

### 5.1 メモ詳細への遷移

**実装箇所**: `src/views/tags/view.py` の `_on_memo_click()`

**実装内容**:
```python
def _on_memo_click(self, _e: ft.ControlEvent, memo_id: str) -> None:
    self.page.go(f"/memos/{memo_id}")
```

**必要な確認**:
- `src/router.py` で `/memos/{memo_id}` ルートが定義されているか
- MemosView が特定メモの選択状態復元に対応しているか

---

### 5.2 タスク詳細への遷移

**実装箇所**: `src/views/tags/view.py` の `_on_task_click()`

**実装内容**:
```python
def _on_task_click(self, _e: ft.ControlEvent, task_id: str) -> None:
    self.page.go(f"/tasks/{task_id}")
```

**必要な確認**:
- `src/router.py` で `/tasks/{task_id}` ルートが定義されているか
- TasksView が特定タスクの選択状態復元に対応しているか

---

## 6. テスト実装（オプション）

**注意**: プロジェクトポリシーでは `src/views/` 配下のテストは不要ですが、
ロジック層（ApplicationService, Repository, Queries）は必ずテストを追加してください。

### 6.1 TagApplicationService のテスト

**ファイル**: `tests/logic/application/test_tag_application_service.py`

**テストケース**:
- タグの作成・取得・更新・削除
- カスケード削除（関連する Task_Tag, Memo_Tag も削除される）
- 件数取得の正確性

---

### 6.2 Queries のテスト

**ファイル**: `tests/logic/queries/test_tag_queries.py`

**テストケース**:
- `count_memos_by_tag()` の正確性
- `count_tasks_by_tag()` の正確性
- `get_memos_by_tag_name()` のJOIN動作
- `get_tasks_by_tag_name()` のJOIN動作

---

## 7. 実装優先順位

### Phase 1: 基本CRUD（必須）
1. TagApplicationService 実装
2. TagQueries 実装（件数取得）
3. Controller の依存注入対応
4. TagCreateDialog / TagEditDialog 実装

### Phase 2: 関連アイテム表示（推奨）
1. MemoQueries / TaskQueries 拡張
2. MemoApplicationService / TaskApplicationService 拡張
3. Controller の関連アイテム取得を実サービスに置き換え

### Phase 3: 画面遷移（推奨）
1. ルーティング設定確認
2. メモ/タスク詳細への遷移実装

### Phase 4: 高度な機能（オプション）
1. タグのドラッグ&ドロップ並び替え
2. タグの一括操作（複数選択、一括削除）
3. タグの使用頻度分析

---

## 8. ドキュメント更新

実装完了後、以下のドキュメントを更新してください:

- `docs/app/tags.md`: ユーザー向けタグ管理機能説明
- `docs/dev/architecture.md`: アーキテクチャ図にTags Viewを追加
- `CHANGELOG.md`: 変更履歴に追記

---

## 9. 参考リソース

- Template実装: `src/views_old/template/src/components/TagsScreen.tsx`
- Memos View: `src/views/memos/` (レイヤー構成の参考)
- Theme定義: `src/views/theme.py`
- プロジェクトガイドライン: `.github/copilot-instructions.md`

---

**更新日**: 2025-01-13
**担当**: AI Agent (Flet Layered Views Engineer v1)
