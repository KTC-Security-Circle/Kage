# Views の書き方ガイド

このガイドでは View レイヤーの設計・実装パターンと最新の Component Launcher (Strict Preview Mode) 仕様をまとめます。

---

## CRUD 操作の実装パターン

```python
# タスク作成の例
def _on_task_created(self, command: CreateTaskCommand) -> None:
    """タスク作成時の処理"""
    try:
        # Application Serviceを通じてビジネスロジックを実行
        new_task = self._task_app_service.create_task(command)

        # 成功時のUI更新
        self._refresh_tasks()
        self._show_success_message(f"タスク '{new_task.title}' を作成しました")

    except TaskServiceError as e:
        # ビジネスロジックエラーの処理
        self._show_error_message(f"タスク作成に失敗しました: {e}")
        logger.error(f"Task creation failed: {e}")

    except Exception as e:
        # 予期しないエラーの処理
        self._show_error_message("予期しないエラーが発生しました")
        logger.exception(f"Unexpected error in task creation: {e}")

# タスク更新の例
def _on_task_status_change(self, task_id: str, new_status: TaskStatus) -> None:
    """タスクステータス変更時の処理"""
    try:
        command = UpdateTaskStatusCommand(task_id=task_id, status=new_status)
        updated_task = self._task_app_service.update_task_status(command)

        # リアルタイムUI更新
        self.tasks_board.update_task_status(task_id, new_status)
        self._show_success_message(f"タスクステータスを {new_status.value} に変更しました")

    except TaskServiceError as e:
        self._show_error_message(f"ステータス変更に失敗しました: {e}")
        # UI状態をロールバック
        self.tasks_board.revert_task_status(task_id)
```

## コマンド/クエリパターンの活用

```python
# Command（状態変更）とQuery（状態取得）を明確に分離

# Command例 - 状態を変更する操作
def _handle_quick_action(self, action: QuickActionCommand) -> None:
    """クイックアクション実行"""
    try:
        result = self._task_app_service.execute_quick_action(action)
        self._refresh_tasks()  # UI更新
        self._show_success_message(f"{action.action_name} を実行しました")

    except Exception as e:
        self._show_error_message(f"アクション実行に失敗しました: {e}")

# Query例 - データ取得のみ
def _load_tasks_by_status(self, status: TaskStatus) -> list[TaskRead]:
    """指定ステータスのタスクを取得"""
    try:
        query = GetTasksByStatusQuery(status=status)
        return self._task_app_service.get_tasks_by_status(query)

    except Exception as e:
        logger.error(f"Failed to load tasks with status {status}: {e}")
        self._show_error_message("タスクの読み込みに失敗しました")
        return []
```

## GTD 特化のワークフロー実装

```python
# GTD Inbox Reviewの一括処理例
def _process_inbox_review(self, decisions: list[InboxDecision]) -> None:
    """Inbox Review - GTD固有のワークフロー"""
    try:
        # Application Serviceが複雑なワークフローを管理
        results = self._task_app_service.process_gtd_inbox_review(decisions)

        # UI側は結果の表示に専念
        processed_count = len(results)
        self._show_success_message(f"{processed_count}件のタスクを処理しました")

        # ボード全体を更新
        self._refresh_tasks()

    except GTDWorkflowError as e:
        self._show_error_message(f"Inbox Review処理に失敗しました: {e}")

# 週次レビューワークフロー
def _start_weekly_review(self) -> None:
    """GTD週次レビューの開始"""
    try:
        review_data = self._task_app_service.prepare_weekly_review()

        # 専用ダイアログでレビュー画面を表示
        self._open_weekly_review_dialog(review_data)

    except Exception as e:
        self._show_error_message(f"週次レビューの準備に失敗しました: {e}")
```

## Component Launcher（Strict Preview Mode）

現在の Component Launcher は **`@classmethod preview` を持つ `ft.Control` サブクラスのみ** を対象にした厳格モードです。

必須条件:

- クラスが `ft.Control` を継承
- `@classmethod preview(cls) -> ft.Control` を実装（内部でダミーデータ生成）

削除された旧仕様:

- 任意ファクトリ関数 (`create_control` など)
- 引数注入オプション (`--props`, `--props-file`)
- フォールバック命名探索
- `--wrap-layout` 明示フラグ（ラップは既定で有効 / `-nw` で解除）

### 使用例

```powershell
# プレビュー（簡易レイアウト付き）
poe component --target views.memos.components.memo_card:MemoCard

# レイアウト無し表示
poe component --target views.memos.components.memo_card:MemoCard -nw
```

### オプション (現行)

| オプション          | 説明                                                 |
| ------------------- | ---------------------------------------------------- |
| `--target`          | `module:Class` または `path/to/file.py:Class` (必須) |
| `--no-wrap` / `-nw` | 簡易レイアウトラップを無効化（既定はラップ有効）     |

### 自動適用

- ログ初期化
- ページ設定（フォント/テーマ）
- 簡易 View ラップ（除去時は `-nw`）
- ブラウザ起動 (AppView.WEB_BROWSER, port=8000)

### preview 実装例

```python
class MemoCard(ft.Container):
    @classmethod
    def preview(cls) -> "MemoCard":
        from datetime import datetime
        from uuid import uuid4
        from views.sample import SampleMemo
        sample = SampleMemo(
            id=uuid4(),
            title="プレビュー用メモ",
            content="これは MemoCard 単体プレビューのダミーコンテンツです。",
            created_at=datetime.now(),
        )
        return cls(memo=sample, is_selected=True)
```

### 移行ガイド

| 旧機能                      | 新仕様                    | 対応方法                    |
| --------------------------- | ------------------------- | --------------------------- |
| `create_control` ファクトリ | 廃止                      | クラスへ統合し preview 実装 |
| `--props` / `--props-file`  | 廃止                      | preview 内でデータ生成      |
| フォールバック命名探索      | 廃止                      | preview を必ず定義          |
| `--wrap-layout`             | 既定ラップ / `-nw` で解除 | 必要なら `-nw` 使用         |
| ネイティブウィンドウ表示    | ブラウザ表示に統一        | スクリプト変更で復帰可      |

### 拡張のヒント

- コンポーネントギャラリー: `ComponentsGallery(ft.Column)` に複数子コンポーネントを配置し preview で返す。
- 共通モックデータ: `views/_preview_data.py` 等を新設して再利用性向上。
- 表示モード切替: `ft.app(... view=ft.AppView.FLET_APP)` に変更してネイティブ復帰。

旧オプションを利用している既存ドキュメントやスクリプトは削除・更新してください。

## Context（コンテキスト）ベースのフィルタリング UI

```python
# views/shared/context_filter.py - GTDコンテキストフィルター
class ContextFilter(ft.Row):
    """GTDコンテキスト（@電話、@外出等）によるフィルタリングUI"""

    def __init__(self, on_context_change: Callable[[list[str]], None]):
        super().__init__()
        self.on_context_change = on_context_change
        self.selected_contexts: set[str] = set()

        # GTD標準コンテキストの定義
        self.gtd_contexts = [
            ("@電話", ft.icons.PHONE, ft.colors.BLUE),
            ("@外出", ft.icons.DIRECTIONS_CAR, ft.colors.GREEN),
            ("@PC", ft.icons.COMPUTER, ft.colors.PURPLE),
            ("@家", ft.icons.HOME, ft.colors.ORANGE),
            ("@買い物", ft.icons.SHOPPING_CART, ft.colors.RED),
            ("@待機", ft.icons.SCHEDULE, ft.colors.YELLOW),
        ]

        self._build_context_chips()

    def _build_context_chips(self) -> None:
        """コンテキストチップを構築"""
        context_chips = []

        for context, icon, color in self.gtd_contexts:
            chip = ft.FilterChip(
                label=ft.Text(context),
                leading=ft.Icon(icon),
                selected=context in self.selected_contexts,
                on_select=lambda e, ctx=context: self._on_context_toggle(ctx, e.data),
                bgcolor=color if context in self.selected_contexts else None
            )
            context_chips.append(chip)

        self.controls = [
            ft.Text("コンテキスト:", weight=ft.FontWeight.BOLD),
            ft.Wrap(context_chips, spacing=8)
        ]
```

## 2-Minute Rule (2 分ルール) サポート

```python
# views/task/components/quick_actions.py - クイックアクション
class QuickActionButton(ft.ElevatedButton):
    """GTD 2分ルールに基づくクイックアクション"""

    def __init__(self, action: QuickActionCommand, on_click: Callable):
        super().__init__()
        self.action = action

        # アクションタイプに応じた表示設定
        self._setup_action_appearance()
        self.on_click = lambda _: on_click(action)

    def _setup_action_appearance(self) -> None:
        """アクションタイプに応じた外観設定"""
        action_configs = {
            "DO_NOW": {  # 2分以内で完了
                "text": "今すぐ実行",
                "icon": ft.icons.FLASH_ON,
                "color": ft.colors.GREEN,
                "tooltip": "2分以内で完了できるタスクをすぐに実行"
            },
            "DEFER": {  # 後で実行
                "text": "後で実行",
                "icon": ft.icons.SCHEDULE,
                "color": ft.colors.BLUE,
                "tooltip": "Next Actionリストに追加"
            },
            "DELEGATE": {  # 委譲
                "text": "委譲",
                "icon": ft.icons.PERSON_ADD,
                "color": ft.colors.ORANGE,
                "tooltip": "他の人に委譲"
            },
            "DELETE": {  # 削除
                "text": "削除",
                "icon": ft.icons.DELETE,
                "color": ft.colors.RED,
                "tooltip": "不要なタスクを削除"
            }
        }

        config = action_configs.get(self.action.action_type, action_configs["DEFER"])

        self.text = config["text"]
        self.icon = config["icon"]
        self.bgcolor = config["color"]
        self.tooltip = config["tooltip"]
        self.style = ft.ButtonStyle(color=ft.colors.WHITE)
```

## Project 階層表示コンポーネント

```python
# views/task/components/project_tree.py - プロジェクト階層表示
class ProjectTreeView(ft.Container):
    """GTDプロジェクトの階層表示"""

    def __init__(self, projects: list[ProjectRead], on_project_select: Callable):
        super().__init__()
        self.projects = projects
        self.on_project_select = on_project_select

        self._build_project_tree()

    def _build_project_tree(self) -> None:
        """プロジェクト階層ツリーを構築"""
        tree_items = []

        # アクティブプロジェクトを先頭に表示
        active_projects = [p for p in self.projects if p.status == ProjectStatus.ACTIVE]
        waiting_projects = [p for p in self.projects if p.status == ProjectStatus.WAITING]
        someday_projects = [p for p in self.projects if p.status == ProjectStatus.SOMEDAY_MAYBE]

        if active_projects:
            tree_items.append(self._create_project_section("🚀 アクティブプロジェクト", active_projects))

        if waiting_projects:
            tree_items.append(self._create_project_section("⏳ 待機中プロジェクト", waiting_projects))

        if someday_projects:
            tree_items.append(self._create_project_section("🤔 いつか/多分プロジェクト", someday_projects))

        self.content = ft.Column(tree_items, spacing=16)

    def _create_project_section(self, title: str, projects: list[ProjectRead]) -> ft.ExpansionTile:
        """プロジェクトセクションを作成"""
        project_tiles = []

        for project in projects:
            # プロジェクトの進捗状況を計算
            progress = self._calculate_project_progress(project)

            tile = ft.ListTile(
                leading=ft.Icon(ft.icons.FOLDER, color=ft.colors.BLUE_400),
                title=ft.Text(project.title, weight=ft.FontWeight.BOLD),
                subtitle=ft.Text(f"進捗: {progress:.0%} | タスク数: {len(project.tasks)}"),
                trailing=ft.LinearProgressBar(value=progress, width=100),
                on_click=lambda e, p=project: self.on_project_select(p)
            )
            project_tiles.append(tile)

        return ft.ExpansionTile(
            title=ft.Text(title, weight=ft.FontWeight.BOLD),
            controls=project_tiles,
            initially_expanded=title.startswith("🚀")  # アクティブプロジェクトは初期展開
        )
```

## 関数ベースのアプローチ

関数ベースのアプローチは、単純な機能や再利用可能なコンポーネントに適しています。

### 関数ベースの特徴

- **シンプル**: 理解しやすく、書きやすい
- **軽量**: 状態管理が不要な場合に最適
- **再利用性**: 純粋関数として設計しやすい

### 関数ベースの実装例

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

### 関数ベースの使用場面

- 単純な UI コンポーネント
- 状態を持たない表示要素
- 複数の画面で再利用されるコンポーネント
- ユーティリティ関数

## クラスベースのアプローチ

クラスベースのアプローチは、複雑な状態管理やライフサイクル管理が必要な場合に適しています。

### クラスベースの特徴

- **状態管理**: インスタンス変数で状態を保持できる
- **ライフサイクル**: 初期化、更新、破棄のタイミングを制御できる
- **カプセル化**: 関連する機能をまとめて管理できる

### クラスベースの実装例

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

### クラスベースの使用場面

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

## 依存性注入と Service Container 使用

Views 層で Application Service を使用する際は、Service Container パターンを活用して依存性注入を実現します。これにより、テスタビリティと保守性を向上させます。

### 1. Service Container の基本的な使用方法

```python
# views/task/view.py - Service Container使用例
class TaskView(BaseView):
    """Service Containerを使用したタスクビュー"""

    def __init__(self, page: ft.Page) -> None:
        super().__init__(page)

        # BaseViewで管理されているcontainerから必要なサービスを取得
        self._task_service = self.container.get_task_application_service()
        self._project_service = self.container.get_project_application_service()
        self._tag_service = self.container.get_tag_application_service()
```

### 2. 依存性の明示的な管理

```python
# views/shared/service_aware_view.py - サービス対応ベースビュー
class ServiceAwareView(BaseView):
    """Application Serviceに依存するビューの基底クラス"""

    def __init__(
        self,
        page: ft.Page,
        container: ApplicationServiceContainer | None = None
    ) -> None:
        # BaseViewを初期化（containerは自動的に設定される）
        super().__init__(page)

        # テスト時にはモックコンテナで上書き可能
        if container is not None:
            self.container = container

        # 必要なサービスを初期化時に取得
        self._initialize_services()

    def _initialize_services(self) -> None:
        """必要なApplication Serviceを初期化"""
        self._task_service = self.container.get_task_application_service()
        # 他のサービスも必要に応じて取得
```

### 3. 階層的な依存性管理

```python
# views/task/components/task_dialog.py - 子コンポーネントへの依存性伝播
class TaskDialog(ft.AlertDialog):
    """タスク作成・編集ダイアログ"""

    def __init__(
        self,
        page: ft.Page,
        task_service: TaskApplicationService,  # 親から注入
        on_task_created: Callable[[TaskRead], None] | None = None
    ) -> None:
        super().__init__()
        self._page = page
        self._task_service = task_service  # 注入されたサービスを使用
        self.on_task_created = on_task_created

        self._build_dialog()

    def _on_save_clicked(self, _: ft.ControlEvent) -> None:
        """保存処理（注入されたサービスを使用）"""
        try:
            command = CreateTaskCommand(
                title=self.title_field.value,
                description=self.description_field.value
            )

            # 注入されたサービスを使用
            new_task = self._task_service.create_task(command)

            if self.on_task_created:
                self.on_task_created(new_task)

            self._close_dialog()

        except Exception as e:
            self._show_error(f"タスク作成に失敗しました: {e}")

# 親ビューでの使用例
class TaskView(ServiceAwareView):
    def _initialize_components(self) -> None:
        # サービスを子コンポーネントに注入
        self.task_dialog = TaskDialog(
            page=self._page,
            task_service=self._task_service,  # 依存性を注入
            on_task_created=self._on_task_created
        )
```

### 4. テスト用のモック注入

```python
# tests/views/test_task_view.py - テスト用モック注入例
class MockApplicationServiceContainer:
    """テスト用のモックコンテナ"""

    def __init__(self):
        self.mock_task_service = Mock(spec=TaskApplicationService)

    def get_task_application_service(self) -> TaskApplicationService:
        return self.mock_task_service

def test_task_creation():
    """タスク作成のテスト"""
    # モックコンテナを準備
    mock_container = MockApplicationServiceContainer()
    mock_container.mock_task_service.create_task.return_value = TaskRead(
        id="test-id",
        title="Test Task",
        status=TaskStatus.INBOX
    )

    # テスト対象のビューにモックを注入
    page = Mock(spec=ft.Page)
    view = TaskView(page=page, container=mock_container)

    # テスト実行
    command = CreateTaskCommand(title="Test Task")
    view._on_task_created(command)

    # モックが正しく呼ばれたことを確認
    mock_container.mock_task_service.create_task.assert_called_once_with(command)
```

## リアルタイム更新とイベント処理

GTD タスク管理では、タスクの状態変更やプロジェクトの進捗をリアルタイムで UI に反映する必要があります。

### 1. Observer パターンによる状態同期

```python
# views/shared/observable_view.py - 観察可能なビュー
class ObservableView(ServiceAwareView):
    """状態変更を観察するビューの基底クラス"""

    def __init__(self, page: ft.Page, container: ApplicationServiceContainer | None = None):
        super().__init__(page, container)
        self._observers: list[Callable] = []

    def add_observer(self, callback: Callable) -> None:
        """状態変更の観察者を追加"""
        self._observers.append(callback)

    def _notify_observers(self, event_type: str, data: dict) -> None:
        """観察者に変更を通知"""
        for callback in self._observers:
            try:
                callback(event_type, data)
            except Exception as e:
                logger.error(f"Observer notification failed: {e}")

# 実装例
class TaskView(ObservableView):
    def _on_task_status_changed(self, task_id: str, new_status: TaskStatus) -> None:
        """タスクステータス変更時の処理"""
        try:
            # Application Service経由で更新
            command = UpdateTaskStatusCommand(task_id=task_id, status=new_status)
            updated_task = self._task_service.update_task_status(command)

            # UI更新
            self._update_task_in_board(updated_task)

            # 他のコンポーネントに変更を通知
            self._notify_observers("task_status_changed", {
                "task_id": task_id,
                "old_status": self.tasks_board.get_task_status(task_id),
                "new_status": new_status
            })

        except Exception as e:
            self._show_error(f"ステータス変更に失敗しました: {e}")
            # UI状態をロールバック
            self._revert_task_status(task_id)
```

### 2. 楽観的 UI 更新パターン

```python
# views/task/components/tasks_board.py - 楽観的更新
class TasksBoard(ft.Container):
    """楽観的更新を実装したタスクボード"""

    def move_task_optimistic(
        self,
        task_id: str,
        target_status: TaskStatus,
        revert_callback: Callable[[], None]
    ) -> None:
        """楽観的にタスクを移動（即座にUI更新）"""

        # 1. 即座にUIを更新（楽観的更新）
        task_card = self._find_task_card(task_id)
        old_status = task_card.task.status

        # UIからタスクを移動
        self._move_task_card_immediately(task_card, target_status)

        # 2. バックエンド更新を非同期で実行
        async def update_backend():
            try:
                command = UpdateTaskStatusCommand(task_id=task_id, status=target_status)
                await self._task_service.update_task_status_async(command)

                # 成功時のフィードバック
                self._show_success_feedback(f"タスクを {target_status.value} に移動しました")

            except Exception as e:
                # 失敗時はUIをロールバック
                logger.error(f"Task status update failed: {e}")
                self._move_task_card_immediately(task_card, old_status)
                revert_callback()
                self._show_error(f"ステータス変更に失敗しました: {e}")

        # 非同期実行
        asyncio.create_task(update_backend())
```

### 3. プロジェクト進捗のリアルタイム反映

```python
# views/task/components/project_progress.py - プロジェクト進捗バー
class ProjectProgressBar(ft.Container):
    """プロジェクト進捗をリアルタイム表示"""

    def __init__(self, project: ProjectRead):
        super().__init__()
        self.project = project
        self._build_progress_bar()

        # タスク変更の監視
        self._setup_task_monitoring()

    def _setup_task_monitoring(self) -> None:
        """タスク変更の監視設定"""
        # イベントバスまたはObserverパターンでタスク変更を監視
        task_event_bus.subscribe("task_status_changed", self._on_task_changed)

    def _on_task_changed(self, event_data: dict) -> None:
        """タスク変更時の進捗更新"""
        task_id = event_data.get("task_id")

        # このプロジェクトのタスクかどうかチェック
        if task_id in [task.id for task in self.project.tasks]:
            # 進捗を再計算してUI更新
            self._update_progress()

    def _update_progress(self) -> None:
        """進捗バーの更新"""
        completed_tasks = len([t for t in self.project.tasks if t.status == TaskStatus.DONE])
        total_tasks = len(self.project.tasks)

        if total_tasks > 0:
            progress = completed_tasks / total_tasks
            self.progress_bar.value = progress
            self.progress_text.value = f"{completed_tasks}/{total_tasks} 完了 ({progress:.0%})"
        else:
            self.progress_bar.value = 0
            self.progress_text.value = "タスクなし"

        self.update()
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

from logic.task import TaskService
from models.task import Task

if TYPE_CHECKING:
    from models.user import User

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

### ケース 1: 状態管理の問題

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

### ケース 2: エラーハンドリングの問題

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

### ケース 3: レイアウトの問題

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

### ケース 4: import の問題

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

### ケース 5: 命名の問題

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

### 基本設計原則

1. **Clean Architecture 準拠**: Application Service 層を通じてビジネスロジックにアクセス
2. **適切なアプローチの選択**: 関数ベースかクラスベースかを適切に選ぶ
3. **明確な責務の分離**: UI 表示とビジネスロジックを完全に分離

### GTD 固有の設計

1. **GTD 概念の視覚化**: TaskStatus、コンテキスト、プロジェクト階層の適切な表現
2. **ワークフロー対応**: Inbox Review、週次レビュー等の GTD プロセスを UI 化
3. **2 分ルールサポート**: クイックアクションによる即座の判断・実行

### 技術的品質

1. **依存性注入**: Service Container パターンによるテスタブルな設計
2. **エラーハンドリング**: ユーザーフレンドリーなエラー表示とリカバリー
3. **リアルタイム更新**: 楽観的 UI 更新によるレスポンシブな体験
4. **テスタビリティ**: MVP 패턴とインターフェース分離によるユニットテスト対応

### 開発効率

1. **再利用性**: 共通コンポーネントと Mixin の活用
2. **保守性**: 明確なファイル構造とコーディング規約
3. **拡張性**: 新機能追加に対応できる柔軟な設計

これらの指針に従うことで、GTD の思想を適切に反映し、保守性が高く理解しやすい View レイヤーを構築できます。特に、Application Service 層との適切な連携により、Views 層は UI 表示に専念でき、ビジネスロジックの複雑さから分離された設計を実現できます。

## 旧 Component Launcher 記述の削除について

このセクションは旧仕様（`create_control` / `--props` / `--props-file` / `--wrap-layout` など）に基づく内容だったため Strict Preview Mode 移行に伴い削除されました。最新仕様は本ファイル前半の「現在の Component Launcher は ... 厳格モードです」節を参照してください。

主な変更点要約:

- 旧: ファクトリ関数や JSON 経由の引数注入を許容 → 新: `@classmethod preview` に統一
- 旧: PowerShell クォート回避策 (`--props-file`) → 新: preview 内でダミーデータ生成
- 旧: 明示 `--wrap-layout` → 新: デフォルトラップ / `-nw` で解除
- 旧: 多数の終了コード (JSON_ERROR など) → 新: 簡素化されたエラーセット

ドキュメント更新時は旧オプションの記述を再導入しないでください。
