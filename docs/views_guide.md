# Views の書き方ガイド

このドキュメントでは、SigotoDekiruKun プロジェクトにおける View レイヤーの実装方法について説明します。Python 初学者がメンバーに入った際に読んで理解できるように、基本的な考え方から具体的な実装方法まで体系的に解説しています。

## 目次

1. [View レイヤーとは](#viewレイヤーとは)
2. [プロジェクトのディレクトリ構造](#プロジェクトのディレクトリ構造)
3. [関数ベースのアプローチ](#関数ベースのアプローチ)
4. [クラスベースのアプローチ](#クラスベースのアプローチ)
5. [どちらを選ぶべきか](#どちらを選ぶべきか)
6. [実装テンプレート](#実装テンプレート)
7. [ベストプラクティス](#ベストプラクティス)
8. [よくある間違いとその解決策](#よくある間違いとその解決策)

## Viewレイヤーとは

View レイヤーは MVC アーキテクチャにおける「V」に相当する部分で、ユーザーインターフェース（UI）を担当します。このプロジェクトでは、Flet ライブラリで GUI アプリケーションを構築するため、View レイヤーが画面の表示とユーザーインタラクションを管理します。

### 役割と責務

- **表示（Display）**: データを画面に表示する
- **相互作用（Interaction）**: ユーザーの操作（クリック、入力）に対応する
- **レイアウト（Layout）**: UI コンポーネントの配置と構成を管理する

### 他のレイヤーとの関係

```plain text
┌─────────────────┐
│     Views       │ ← UIの表示とユーザーインタラクション
├─────────────────┤
│     Logic       │ ← ビジネスロジック、データ処理
├─────────────────┤
│     Models      │ ← データベースモデル、データ構造
└─────────────────┘
```

## プロジェクトのディレクトリ構造

```plain text
src/views/
├── __init__.py           # ビューのエクスポート定義
├── layout.py             # 共通レイアウト（ヘッダー等）
├── shared/               # 共有コンポーネント
│   ├── __init__.py
│   └── app_bar.py        # アプリケーションバー
├── home/                 # ホーム画面
│   ├── __init__.py
│   ├── view.py           # メインビュー
│   └── components.py     # 個別コンポーネント
└── task/                 # タスク管理画面
    ├── __init__.py
    ├── view.py           # メインビュー
    └── components.py     # 個別コンポーネント
```

### ディレクトリ構造の考え方

1. **機能ごとの分割**: `home/`, `task/` のように機能ごとにディレクトリを分ける
2. **共通要素の分離**: `shared/` ディレクトリに再利用可能なコンポーネントを配置
3. **役割による分離**: `view.py` (メインビュー) と `components.py` (個別コンポーネント) に分ける

## 関数ベースのアプローチ

関数ベースのアプローチは、単純な機能や再利用可能なコンポーネントに適しています。

### 特徴

- **シンプル**: 理解しやすく、書きやすい
- **軽量**: 状態管理が不要な場合に最適
- **再利用性**: 純粋関数として設計しやすい

### 実装例

```python
import flet as ft
from typing import Callable

def create_welcome_message() -> ft.Container:
    """ウェルカムメッセージを作成.

    Returns:
        ウェルカムメッセージのContainerコンポーネント
    """
    return ft.Container(
        content=ft.Text(
            "タスク管理でもっと効率的に！",
            size=18,
            color=ft.colors.GREY_700,
        ),
        alignment=ft.alignment.center,
    )

def create_action_button(
    text: str,
    icon: str,
    on_click: Callable,
    width: int = 200
) -> ft.ElevatedButton:
    """アクションボタンを作成.

    Args:
        text: ボタンのテキスト
        icon: アイコン名
        on_click: クリック時のハンドラー
        width: ボタンの幅

    Returns:
        設定されたElevatedButtonコンポーネント
    """
    return ft.ElevatedButton(
        text=text,
        icon=icon,
        width=width,
        height=50,
        style=ft.ButtonStyle(
            bgcolor=ft.colors.BLUE_600,
            color=ft.colors.WHITE,
        ),
        on_click=on_click,
    )
```

### 使用場面

- 単純な UI コンポーネント
- 状態を持たない表示要素
- 複数の画面で再利用されるコンポーネント
- ユーティリティ関数

## クラスベースのアプローチ

クラスベースのアプローチは、複雑な状態管理やライフサイクル管理が必要な場合に適しています。

### 特徴

- **状態管理**: インスタンス変数で状態を保持できる
- **ライフサイクル**: 初期化、更新、破棄のタイミングを制御できる
- **カプセル化**: 関連する機能をまとめて管理できる

### 実装例

```python
import flet as ft
from typing import Callable, Optional
from models.task import Task

class TaskCreateForm(ft.Column):
    """タスク作成フォームコンポーネント

    新しいタスクを作成するためのフォームUIを提供します。
    """

    def __init__(
        self,
        page: ft.Page,
        on_task_created: Optional[Callable[[Task], None]] = None
    ) -> None:
        """TaskCreateFormのコンストラクタ

        Args:
            page: Fletのページオブジェクト
            on_task_created: タスク作成時のコールバック関数
        """
        super().__init__()
        self._page = page
        self.on_task_created = on_task_created

        # フォーム要素の初期化
        self._initialize_components()

        # レイアウトの構築
        self._build_layout()

    def _initialize_components(self) -> None:
        """各コンポーネントを初期化"""
        self.title_field = ft.TextField(
            label="タスクタイトル",
            hint_text="タスクのタイトルを入力してください",
            max_length=100,
            width=400,
        )

        self.description_field = ft.TextField(
            label="説明（任意）",
            multiline=True,
            max_lines=3,
            width=400,
        )

        self.create_button = ft.ElevatedButton(
            text="タスクを作成",
            icon=ft.icons.ADD,
            on_click=self._on_create_clicked,
        )

    def _build_layout(self) -> None:
        """レイアウトを構築"""
        self.controls = [
            ft.Text("新しいタスクを作成", style=ft.TextThemeStyle.HEADLINE_SMALL),
            self.title_field,
            self.description_field,
            self.create_button,
        ]

    def _on_create_clicked(self, _: ft.ControlEvent) -> None:
        """タスク作成ボタンクリック時の処理"""
        # バリデーション
        if not self.title_field.value:
            self._show_error("タイトルを入力してください")
            return

        # タスク作成ロジック
        # ... 実装 ...

        # フォームクリア
        self._clear_form()

    def _clear_form(self) -> None:
        """フォームをクリア"""
        self.title_field.value = ""
        self.description_field.value = ""
        self.update()

    def _show_error(self, message: str) -> None:
        """エラーメッセージを表示"""
        self._page.open(ft.SnackBar(content=ft.Text(message)))
```

### 使用場面

- 複雑な状態管理が必要な場合
- フォームやリストなどのインタラクティブなコンポーネント
- ライフサイクル管理が重要な場合
- 複数のメソッドで状態を共有する場合

## どちらを選ぶべきか

### 判断基準

| 項目             | 関数ベース | クラスベース |
| ---------------- | ---------- | ------------ |
| 状態管理         | 不要       | 必要         |
| 複雑さ           | シンプル   | 複雑         |
| 再利用性         | 高い       | 中程度       |
| インタラクション | 少ない     | 多い         |
| ライフサイクル   | 単純       | 複雑         |

### 具体的な選択指針

#### 関数ベースを選ぶ場合

- 単純な表示コンポーネント
- 状態を持たない UI 要素
- 純粋な表示機能のみ
- 複数画面で再利用されるコンポーネント

```python
# ✅ 関数ベースが適している例
def create_loading_spinner() -> ft.ProgressRing:
    return ft.ProgressRing()

def create_divider() -> ft.Divider:
    return ft.Divider(height=1, color=ft.colors.GREY_300)
```

#### クラスベースを選ぶ場合

- フォーム入力
- リスト表示（動的な追加・削除）
- 状態の変更が必要
- 複数のイベントハンドラーが必要

```python
# ✅ クラスベースが適している例
class TaskList(ft.Column):
    """複数のタスクを管理するリストコンポーネント"""
    pass

class LoginForm(ft.Column):
    """ログインフォームコンポーネント"""
    pass
```

## 実装テンプレート

### 関数ベーステンプレート

```python
"""機能名のコンポーネントモジュール."""

import flet as ft
from typing import Callable, Optional

def create_component_name(
    param1: str,
    param2: Optional[str] = None,
    on_click: Optional[Callable] = None
) -> ft.Control:
    """コンポーネントの説明.

    Args:
        param1: パラメータの説明
        param2: オプショナルパラメータの説明
        on_click: クリック時のハンドラー

    Returns:
        作成されたコンポーネント
    """
    return ft.Container(
        content=ft.Text(param1),
        on_click=on_click,
    )

def create_another_component() -> ft.Control:
    """別のコンポーネントの説明.

    Returns:
        作成されたコンポーネント
    """
    # 実装
    pass
```

### クラスベーステンプレート

```python
"""機能名のビューモジュール."""

from __future__ import annotations
from typing import TYPE_CHECKING, Callable, Optional

import flet as ft

if TYPE_CHECKING:
    from models.example import ExampleModel

class ComponentName(ft.Column):  # またはft.Container, ft.Row等
    """コンポーネントの説明

    詳細な説明をここに記述します。
    """

    def __init__(
        self,
        page: ft.Page,
        param1: str,
        on_event: Optional[Callable] = None
    ) -> None:
        """コンストラクタ

        Args:
            page: Fletのページオブジェクト
            param1: パラメータの説明
            on_event: イベントハンドラー
        """
        super().__init__()
        self._page = page
        self.param1 = param1
        self.on_event = on_event

        # 設定
        self.spacing = 10
        self.expand = True

        # 初期化
        self._initialize_components()
        self._build_layout()

    def _initialize_components(self) -> None:
        """各コンポーネントを初期化"""
        self.some_field = ft.TextField(
            label="ラベル",
            hint_text="ヒント",
        )

        self.some_button = ft.ElevatedButton(
            text="ボタン",
            on_click=self._on_button_clicked,
        )

    def _build_layout(self) -> None:
        """レイアウトを構築"""
        self.controls = [
            ft.Text("タイトル", style=ft.TextThemeStyle.HEADLINE_SMALL),
            self.some_field,
            self.some_button,
        ]

    def _on_button_clicked(self, _: ft.ControlEvent) -> None:
        """ボタンクリック時の処理"""
        # イベント処理を実装
        if self.on_event:
            self.on_event()

    def update_data(self, new_data: str) -> None:
        """データを更新する公開メソッド

        Args:
            new_data: 新しいデータ
        """
        self.some_field.value = new_data
        self.update()

def create_component_view(page: ft.Page) -> ft.Container:
    """ビューを作成する関数

    Args:
        page: Fletのページオブジェクト

    Returns:
        作成されたビューのコンテナ
    """
    return ft.Container(
        content=ComponentName(page, "example"),
        expand=True,
        padding=20,
    )
```

## ベストプラクティス

### 1. 命名規則

#### ファイル名

- `view.py`: メインビューファイル
- `components.py`: 個別コンポーネントファイル
- `snake_case`で命名

#### クラス名

- `PascalCase`で命名
- 明確で説明的な名前を使用
- 例: `TaskCreateForm`, `UserProfileCard`

#### 関数名

- `snake_case`で命名
- `create_` プレフィックスを付ける
- 例: `create_task_button()`, `create_user_list()`

### 2. コードの構造化

#### import 順序

```python
"""モジュールの説明."""

from __future__ import annotations
from typing import TYPE_CHECKING, Callable, Optional

import flet as ft

from logic.task import TaskService
from models.task import Task

if TYPE_CHECKING:
    from models.user import User
```

#### クラスの構造

```python
class ExampleComponent(ft.Column):
    """コンポーネントの説明"""

    def __init__(self, ...):
        """コンストラクタ"""
        # 1. super().__init__()
        # 2. インスタンス変数の設定
        # 3. 初期化メソッドの呼び出し

    def _initialize_components(self) -> None:
        """プライベート: コンポーネント初期化"""

    def _build_layout(self) -> None:
        """プライベート: レイアウト構築"""

    def _on_event_happened(self, _: ft.ControlEvent) -> None:
        """プライベート: イベントハンドラー"""

    def update_something(self, data: str) -> None:
        """パブリック: 外部から呼び出される操作"""
```

### 3. エラーハンドリング

```python
def _on_save_clicked(self, _: ft.ControlEvent) -> None:
    """保存ボタンクリック時の処理"""
    try:
        # バリデーション
        if not self._validate_input():
            return

        # 実際の処理
        result = self.service.save_data(self.input_field.value)

        # 成功時の処理
        self._show_success_message()

    except ValueError as e:
        self._show_error(f"入力エラー: {e}")
    except Exception as e:
        self._show_error(f"予期しないエラーが発生しました: {e}")

def _validate_input(self) -> bool:
    """入力値のバリデーション"""
    if not self.input_field.value:
        self._show_error("値を入力してください")
        return False
    return True

def _show_error(self, message: str) -> None:
    """エラーメッセージを表示"""
    self._page.open(ft.SnackBar(
        content=ft.Text(message, color=ft.colors.WHITE),
        bgcolor=ft.colors.RED_400,
    ))

def _show_success_message(self) -> None:
    """成功メッセージを表示"""
    self._page.open(ft.SnackBar(
        content=ft.Text("保存しました", color=ft.colors.WHITE),
        bgcolor=ft.colors.GREEN_400,
    ))
```

### 4. 状態管理

```python
class TaskList(ft.Column):
    """タスクリストコンポーネント"""

    def __init__(self, page: ft.Page) -> None:
        super().__init__()
        self._page = page

        # 状態を明確に定義
        self.tasks: list[Task] = []
        self.current_filter: str = "all"
        self.is_loading: bool = False

        self._initialize_components()

    def load_tasks(self) -> None:
        """タスクを読み込み"""
        self.is_loading = True
        self._update_loading_state()

        try:
            self.tasks = self.service.get_all_tasks()
            self._update_task_list()
        finally:
            self.is_loading = False
            self._update_loading_state()

    def _update_loading_state(self) -> None:
        """ローディング状態の表示を更新"""
        self.loading_indicator.visible = self.is_loading
        self.task_container.visible = not self.is_loading
        self.update()
```

### 5. コールバック処理

```python
class ParentComponent(ft.Column):
    """親コンポーネント"""

    def __init__(self, page: ft.Page) -> None:
        super().__init__()
        self._page = page

        # 子コンポーネントにコールバックを渡す
        self.child_form = ChildForm(
            page=page,
            on_data_changed=self._on_child_data_changed,
        )

    def _on_child_data_changed(self, new_data: str) -> None:
        """子コンポーネントからのデータ変更通知"""
        # 親コンポーネントでの処理
        self._update_display(new_data)

class ChildForm(ft.Column):
    """子コンポーネント"""

    def __init__(
        self,
        page: ft.Page,
        on_data_changed: Optional[Callable[[str], None]] = None
    ) -> None:
        super().__init__()
        self._page = page
        self.on_data_changed = on_data_changed

    def _on_submit(self, _: ft.ControlEvent) -> None:
        """データ送信時の処理"""
        # データ処理
        processed_data = self._process_data()

        # 親に通知
        if self.on_data_changed:
            self.on_data_changed(processed_data)
```

## よくある間違いとその解決策

### 1. 状態管理の問題

#### ❌ 間違った例

```python
# グローバル変数を使用（避けるべき）
current_user = None

def create_user_profile():
    global current_user
    # 問題: グローバル状態は管理が困難
```

#### ✅ 正しい例

```python
class UserProfile(ft.Column):
    def __init__(self, page: ft.Page, user: User) -> None:
        super().__init__()
        self._page = page
        self.user = user  # インスタンス変数として管理
```

### 2. エラーハンドリングの問題

#### ❌ 間違った例

```python
def _on_save_clicked(self, _: ft.ControlEvent) -> None:
    # エラーハンドリングなし
    result = self.service.save_data(self.input_field.value)
    self._show_success()
```

#### ✅ 正しい例

```python
def _on_save_clicked(self, _: ft.ControlEvent) -> None:
    try:
        if not self._validate_input():
            return
        result = self.service.save_data(self.input_field.value)
        self._show_success()
    except Exception as e:
        self._show_error(f"保存に失敗しました: {e}")
```

### 3. レイアウトの問題

#### ❌ 間違った例

```python
def __init__(self, page: ft.Page) -> None:
    super().__init__()
    # 全ての要素を__init__に詰め込む（読みにくい）
    self.controls = [
        ft.Text("タイトル"),
        ft.TextField(label="入力"),
        ft.ElevatedButton("保存", on_click=self._save),
        # ... 長いリスト
    ]
```

#### ✅ 正しい例

```python
def __init__(self, page: ft.Page) -> None:
    super().__init__()
    self._page = page
    self._initialize_components()
    self._build_layout()

def _initialize_components(self) -> None:
    self.title_text = ft.Text("タイトル")
    self.input_field = ft.TextField(label="入力")
    self.save_button = ft.ElevatedButton("保存", on_click=self._save)

def _build_layout(self) -> None:
    self.controls = [
        self.title_text,
        self.input_field,
        self.save_button,
    ]
```

### 4. import の問題

#### ❌ 間違った例

```python
# 循環インポートを引き起こす可能性
from models.task import Task
from models.user import User  # Userモデル内でTaskを参照している場合
```

#### ✅ 正しい例

```python
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.user import User  # 型チェック時のみインポート
```

### 5. 命名の問題

#### ❌ 間違った例

```python
class TaskForm(ft.Column):  # あいまいな命名
    def click(self, _):     # 何をクリックするのか不明
        pass

def make_task():            # 何を作るのか不明
    pass
```

#### ✅ 正しい例

```python
class TaskCreateForm(ft.Column):  # 明確な命名
    def _on_create_button_clicked(self, _):  # 具体的な操作
        pass

def create_task_list_item():  # 具体的な戻り値
    pass
```

## まとめ

View レイヤーの実装では以下のポイントを意識してください：

1. **適切なアプローチの選択**: 関数ベースかクラスベースかを適切に選ぶ
2. **明確な責務の分離**: 表示ロジックとビジネスロジックを分ける
3. **エラーハンドリング**: ユーザーフレンドリーなエラー表示
4. **状態管理**: 適切なスコープでの状態管理
5. **再利用性**: 共通コンポーネントの活用

これらの指針に従うことで、保守性が高く理解しやすい View レイヤーを構築できます。
