# Shared Components

views/sharedディレクトリには、複数のビュー間で再利用可能なコンポーネントが含まれています。

## コンポーネント一覧

### ActionBar

汎用的なアクションバーコンポーネント。タイトル、サブタイトル、検索フィールド、アクションボタンを含みます。

**使用例:**

```python
from views.shared.components import ActionBar, ActionBarData, ActionButtonData

# データを作成
action_bar_data = ActionBarData(
    title="メモ",
    subtitle="思考とアイデアを記録し、AIでタスクに変換",
    search_placeholder="メモを検索...",
    on_search=handle_search,
    action_buttons=[
        ActionButtonData(
            label="新しいメモ",
            icon=ft.Icons.ADD,
            on_click=handle_create,
            is_primary=True,
        ),
    ],
    show_search=True,
)

# コンポーネントを作成
action_bar = ActionBar(action_bar_data)
```

**主な機能:**

- タイトルとサブタイトルの表示
- 検索フィールド（オプション、最小入力文字数: 2文字）
- 複数のアクションボタン（アイコン付き、プライマリスタイル対応）
- 検索クエリの取得・設定・クリア

**公開メソッド:**

- `clear_search()`: 検索フィールドをクリア
- `get_search_query()`: 現在の検索クエリを取得
- `set_search_query(query: str)`: 検索クエリを設定
- `enable_button(button_id: str)`: 指定IDのボタンを有効化
- `disable_button(button_id: str)`: 指定IDのボタンを無効化

### 使用されているビュー

- **Memos**: メモ一覧画面で検索とメモ作成ボタンを提供
- **CreateMemo**: メモ作成画面で戻るボタン、キャンセルボタン、保存ボタンを提供
- （今後、Tags、Tasks、Projectsなどでも使用予定）

## データクラス

### ActionBarData

アクションバーの表示データ。

**属性:**

- `title: str` - メインタイトル
- `subtitle: str` - サブタイトル
- `search_placeholder: str` - 検索フィールドのプレースホルダー（デフォルト: "検索..."）
- `on_search: Callable[[str], None] | None` - 検索入力のコールバック
- `action_buttons: list[ActionButtonData] | None` - 右側のアクションボタンのリスト
- `leading_buttons: list[ActionButtonData] | None` - 左側のボタンのリスト（戻るボタン等）
- `show_search: bool` - 検索フィールドを表示するか（デフォルト: True）

### ActionButtonData

アクションボタンの表示データ。

**属性:**

- `label: str` - ボタンのラベルテキスト
- `on_click: Callable[[], None]` - クリック時のコールバック
- `icon: str | None` - ボタンのアイコン（オプション、例: `ft.Icons.ADD`）
- `is_primary: bool` - プライマリスタイル（強調表示）を使用するか（デフォルト: True）
- `tooltip: str | None` - ツールチップテキスト（オプション）
- `button_id: str | None` - ボタンの識別子（enable/disableで使用、オプション）
- `disabled: bool` - 初期状態で無効化するか（デフォルト: False）
- `is_outlined: bool` - アウトラインスタイルを使用するか（デフォルト: False）

## 設計原則

1. **データ駆動**: UIは整形済みのデータクラスを受け取る
2. **純粋性**: コンポーネントはビジネスロジックや状態管理を持たない
3. **再利用性**: 複数のビューで使用できる汎用的な設計
4. **型安全性**: すべてのパラメータとコールバックに型ヒントを付与
5. **エラーハンドリング**: ページ未追加時のエラーを適切に処理

## Presenter層との連携

各ビューのPresenter層で、ビュー固有のデータからActionBarDataを生成します。

**例（memos/presenter.py）:**

```python
def create_action_bar_data(
    *,
    title: str = "メモ",
    subtitle: str = "思考とアイデアを記録し、AIでタスクに変換",
    search_placeholder: str = "メモを検索...",
    on_create_memo: Callable[[], None] | None = None,
    on_search: Callable[[str], None] | None = None,
) -> ActionBarData:
    """ActionBarDataを生成する（汎用ActionBarData対応）。"""
    action_buttons = []
    if on_create_memo:
        action_buttons.append(
            ActionButtonData(
                label="新しいメモ",
                icon=ft.Icons.ADD,
                on_click=on_create_memo,
                is_primary=True,
            )
        )

    return ActionBarData(
        title=title,
        subtitle=subtitle,
        search_placeholder=search_placeholder,
        on_search=on_search,
        action_buttons=action_buttons if action_buttons else None,
        show_search=on_search is not None,
    )
```

## メモ作成画面での使用例

保存ボタンなど、動的に有効/無効を切り替える場合:

```python
# ヘッダーを作成
action_bar_data = ActionBarData(
    title="新しいメモを作成",
    subtitle="マークダウン形式で記述できます",
    show_search=False,
    leading_buttons=[
        ActionButtonData(
            label="戻る",
            icon=ft.Icons.ARROW_BACK,
            on_click=handle_back,
            is_outlined=True,
            is_primary=False,
        ),
    ],
    action_buttons=[
        ActionButtonData(
            label="キャンセル",
            on_click=handle_cancel,
            is_outlined=True,
            is_primary=False,
        ),
        ActionButtonData(
            label="保存",
            icon=ft.Icons.SAVE,
            on_click=handle_save,
            is_primary=True,
            button_id="save_button",
            disabled=True,  # 初期状態は無効
        ),
    ],
)
action_bar = ActionBar(action_bar_data)

# 後で動的に有効化
action_bar.enable_button("save_button")

# 保存中は無効化
action_bar.disable_button("save_button")
```

## 今後の拡張

- Tags用のActionBar設定例の追加
- Tasks用のActionBar設定例の追加
- Projects用のActionBar設定例の追加
- フィルタボタンの統合
- エクスポートボタンの統合
