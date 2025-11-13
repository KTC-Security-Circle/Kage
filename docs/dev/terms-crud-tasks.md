# 用語管理CRUD実装タスクリスト

## クイックスタート

UI層は完成済み。以下の順番でロジック層を実装してください。

## 実装タスク

### Phase 1: Repository層 (1日目)

- [ ] **TermRepository の実装**
  - ファイル: `src/logic/repositories/term_repository.py`
  - メソッド: `create()`, `find_by_id()`, `find_by_key()`, `list_all()`, `update()`, `delete()`
  - テスト: `tests/logic/repositories/test_term_repository.py`

- [ ] **SynonymRepository の実装**
  - ファイル: `src/logic/repositories/synonym_repository.py`
  - メソッド: `create()`, `list_by_term()`, `delete_by_term()`
  - テスト: `tests/logic/repositories/test_synonym_repository.py`

### Phase 2: ApplicationService層 (1日目)

- [ ] **TermApplicationService の実装**
  - ファイル: `src/logic/application/term_application_service.py`
  - メソッド:
    - `create_term(data: TermCreate) -> TermRead`
    - `create_synonyms(term_id, synonyms) -> list[SynonymRead]`
    - `update_term(term_id, data) -> TermRead`
    - `delete_term(term_id) -> bool`
    - `get_term_by_id(term_id) -> TermRead | None`
    - `list_terms(status) -> list[TermRead]`
    - `get_synonyms(term_id) -> list[SynonymRead]`
    - `update_synonyms(term_id, new_synonyms) -> list[SynonymRead]`
  - バリデーション: キーの一意性チェック
  - テスト: `tests/logic/application/test_term_application_service.py`

### Phase 3: Controller統合 (2日目)

- [ ] **Controller への ApplicationService 注入**
  - ファイル: `src/views/terms/controller.py`
  - 変更: `__init__` に `app_service` パラメータ追加

- [ ] **Controller CRUD メソッド実装**
  - `async def create_term(form_data) -> None`
  - `async def update_term(term_id, form_data) -> None`
  - `async def delete_term(term_id) -> None`
  - State更新処理の統合

- [ ] **load_initial_terms() の非同期化**
  - ApplicationService.list_terms() を呼び出すように変更

### Phase 4: View統合 (2日目)

- [ ] **View の非同期対応**
  - ファイル: `src/views/terms/view.py`
  - `_handle_dialog_create()` を非同期化
  - エラーハンドリング追加（ValueError, Exception）

- [ ] **依存性注入の設定**
  - ファイル: `src/logic/container.py`
  - ApplicationServices に term_service 追加

### Phase 5: テスト・動作確認 (3日目)

- [ ] **ユニットテストの実行**
  ```bash
  uv run poe test tests/logic/repositories/
  uv run poe test tests/logic/application/
  ```

- [ ] **Web UI での動作確認**
  ```bash
  uv run poe web
  ```
  - [ ] 用語作成（必須項目のみ）
  - [ ] 用語作成（全項目 + 同義語）
  - [ ] キー重複時のエラー表示
  - [ ] 作成後のリスト更新
  - [ ] ステータス別表示

- [ ] **エラーケースのテスト**
  - [ ] 重複キーエラー
  - [ ] 必須項目不足（UI側でブロック済み）
  - [ ] DB接続エラー

## 重要なファイルパス

### 実装対象
- `src/logic/repositories/term_repository.py` ← NEW
- `src/logic/repositories/synonym_repository.py` ← NEW
- `src/logic/application/term_application_service.py` ← NEW
- `src/views/terms/controller.py` ← TODO部分を実装
- `src/views/terms/view.py` ← TODO部分を実装
- `src/logic/container.py` ← term_service追加

### テスト対象
- `tests/logic/repositories/test_term_repository.py` ← NEW
- `tests/logic/repositories/test_synonym_repository.py` ← NEW
- `tests/logic/application/test_term_application_service.py` ← NEW

### 参考資料
- `src/models/__init__.py` ← データモデル定義
- `docs/dev/terms-crud-handover.md` ← 詳細な実装ガイド
- `src/views/memos/` ← 参考実装（似た構造）

## form_data の構造（作成ダイアログから渡される）

```python
{
    "key": str,              # 必須、一意、最大100文字
    "title": str,            # 必須、最大200文字
    "description": str | None,  # 任意、最大2000文字
    "status": str,           # "draft", "approved", "deprecated"
    "source_url": str | None,   # 任意、最大500文字、http/https
    "synonyms": list[str],   # 同義語リスト（空もあり）
}
```

## コマンド早見表

```bash
# 依存関係の同期
uv run poe sync

# マイグレーション適用
uv run poe migrate

# テスト実行
uv run poe test

# Lint & Format
uv run poe fix

# アプリ起動
uv run poe web

# ログ確認（開発時）
tail -f logs/app.log
```

## 完了条件

✅ 全てのユニットテストがパス  
✅ Web UI で用語の作成が正常に動作  
✅ 重複キーのエラーハンドリングが正しく動作  
✅ 作成後のリスト自動更新が動作  
✅ 同義語が正しく保存・表示される  
✅ ruff check がパス  

## 質問先

- 詳細仕様: `docs/dev/terms-crud-handover.md`
- コーディング規約: `.github/copilot-instructions.md`
- TODOコメント: `src/views/terms/controller.py`, `src/views/terms/view.py`
