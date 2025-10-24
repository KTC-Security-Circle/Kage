# Kage Views 再実装プロポーザル（Flet版 / OpenSpec）

本提案は、`src/views/template`（React + Vite + shadcn/ui 構成）を情報源として、Kage のビュー層を Python + Flet で1から再実装するための仕様・計画を示します。Kageのアーキテクチャガイドライン（.github/copilot-instructions.md）と既存の `src/` 構成に準拠します。

## 目的と非目的

- 目的
  - React テンプレートの画面/UIコンポーネント構成・UXを参照し、Fletで等価な体験を提供する。
  - Kage のドメイン層（application/services/repositories）と疎結合に接続できる再利用可能な UI レイヤーを設計・実装する。
  - モダン・直感的・一貫性のあるテーマと、テスト容易性、保守性を両立する。
- 非目的
  - Web版の完全互換（アニメーション/微細なUI挙動を完全一致させることは目標外）。
  - 全てのshadcn/uiコンポーネントの完全模倣。Fletネイティブ/実現可能な代替を優先。

## スコープ（画面・機能）
`template/src/components/*.tsx` 相当の画面を Flet Views に対応付けます。

- 共通レイアウト
  - Sidebar / メインコンテンツ / フッター（AppBarは使用しない）
- 主要画面
  - HomeScreen（ホーム）
  - ProjectsScreen（プロジェクト一覧/編集）
  - TagsScreen（タグ一覧/編集）
  - TasksScreen（タスクボード/一覧/編集）
  - MemosScreen + InboxMemosScreen + ProcessingMemosScreen + MemoHistoryScreen（メモ一覧/収集箱/処理中/履歴）
  - TermsScreen（用語集/辞書）
  - WeeklyReviewScreen（週間レビュー）
  - SettingsScreen（設定）
- CRUDダイアログ
  - Create/Edit Project/Tag/Task/Term/Memo ダイアログ

## ディレクトリとファイル構成（提案）

```
src/views/
  layout.py                 # 全体レイアウトとナビゲーション
  theme.py                  # アプリ共通テーマ/デザイントークン
  shared/                   # 共通UI部品とMixin
    base_view.py            # BaseView / ErrorHandlingMixin
    sidebar.py              # サイドバー
    dialogs.py              # 共通ダイアログ/フォーム骨格
  home/
    view.py
  projects/
    view.py
    components/
      project_list.py
      project_form.py
  tags/
    view.py
    components/
      tag_list.py
      tag_form.py
  tasks/
    view.py
    components/
      tasks_board.py
      task_form.py
      quick_actions.py
  memos/
    inbox_view.py
    processing_view.py
    history_view.py
    view.py
    components/
      memo_list.py
      memo_form.py
  terms/
    view.py
    components/
      term_list.py
      term_form.py
  settings/
    view.py
```

- 既存の `src/router.py` との統合を前提（詳細は下記ルーティング）。
- `logic/container.py`（DI）から Application Service を取得して使用。

## ルーティング設計（Flet）

- ルート例（想定）
  - `/` -> Home
  - `/projects` -> Projects
  - `/tags` -> Tags
  - `/tasks` -> Tasks
  - `/memos` -> Memos
  - `/memos/inbox` -> Inbox Memos
  - `/memos/processing` -> Processing Memos
  - `/memos/history` -> Memo History
  - `/terms` -> Terms
  - `/weekly-review` -> Weekly Review
  - `/settings` -> Settings
- `src/router.py` のパターンに合わせて `ft.RouteChangeEvent` を受け取り、`page.views` を切り替える。

### ルーター配線スニペット（例）

```python
# src/router.py（イメージ）
from __future__ import annotations
from typing import Callable
import flet as ft
from src.views.layout import build_layout

RouteHandler = Callable[[ft.Page, str], None]

def configure_routes(page: ft.Page) -> None:
    """ページのルーティングを初期化する。

    Args:
        page: Fletのページオブジェクト
    """
    def route_change(e: ft.RouteChangeEvent) -> None:
        route = page.route
        page.views.clear()
        page.views.append(build_layout(page, route))
        page.update()

    page.on_route_change = route_change
    page.go(page.route or "/")
```

## UIコンポーネント写像（主な例）

- Sidebar（shadcn/ui） -> `ft.NavigationDrawer` またはカスタム `ft.Container + ft.Column`
- Button -> `ft.ElevatedButton` / `ft.FilledButton` / `ft.OutlinedButton`
- Dialog -> `ft.AlertDialog`
- Tabs -> `ft.Tabs`
- Table -> `ft.DataTable`
- Select/Dropdown -> `ft.Dropdown`
- Switch -> `ft.Switch`
- Slider -> `ft.Slider`
- Toast/Snackbar -> `ft.SnackBar`

shadcn特有の密なインタラクション（コマンドパレット等）は、Fletの制約内で近似実装（ショートカット + Dialog/Autocomplete）を提案します。
備考: 本UIではトップバー（AppBar）は採用しないため、Toolbar相当は設けません。

## 状態管理と疎結合

- View StateはUIと分離してデータクラスで保持。
- Application Service からの結果を受け取り、State更新 -> `page.update()` の順。
- 依存性注入（DI）: `logic/container.py` 経由でサービスを取得。
- イベント境界: UIは「意図（Intent）」を発行、Application層が処理する。

### Stateクラス（例）

```python
# src/views/tasks/state.py
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class TaskItem:
    id: int
    title: str
    done: bool = False
    project_id: Optional[int] = None

@dataclass
class TasksViewState:
    """タスク画面の表示状態。"""
    items: List[TaskItem] = field(default_factory=list)
    loading: bool = False
    error_message: Optional[str] = None
```

## レイアウトと共通部品

- `layout.py` が Sidebar とコンテンツ領域を構成（AppBarなし）。
- `shared/` に BaseView, ErrorHandlingMixin, 共通ダイアログ/フォームを配置。

### BaseView スケルトン（例）

```python
# src/views/shared/base_view.py
from __future__ import annotations
from typing import Optional
import flet as ft

class BaseView(ft.UserControl):
    """全Viewの共通基底。ライフサイクルとエラーハンドリングを提供する。"""

    def __init__(self, page: ft.Page) -> None:
        super().__init__()
        self.page = page

    def did_mount(self) -> None:  # type: ignore[override]
        self.page.pubsub.subscribe(self._on_message)

    def will_unmount(self) -> None:  # type: ignore[override]
        self.page.pubsub.unsubscribe(self._on_message)

    def _on_message(self, message: object) -> None:
        """グローバルメッセージの受信。必要に応じオーバーライド。"""
        return
```

### レイアウトビルダー（例）

```python
# src/views/layout.py
from __future__ import annotations
import flet as ft
from src.views.shared.sidebar import build_sidebar
from src.views.home.view import HomeView
from src.views.projects.view import ProjectsView
# ... 他Viewのimport

ROUTE_TO_VIEW = {
    "/": HomeView,
    "/projects": ProjectsView,
    # ...
}

def build_layout(page: ft.Page, route: str) -> ft.View:
    content = ROUTE_TO_VIEW.get(route, HomeView)(page)
    return ft.View(
        route=route,
        controls=[
      ft.Row([
        build_sidebar(page),
        ft.Container(content, expand=True, padding=10),
      ], expand=True),
        ],
        vertical_alignment=ft.MainAxisAlignment.START,
        horizontal_alignment=ft.CrossAxisAlignment.START,
    )
```

## テーマとスタイル

- `theme.py` に色/余白/角丸/フォント等のデザイントークンを集中管理。
- 明暗テーマ対応（Flet の `ThemeMode.SYSTEM` / 切替UIをSettingsに配置）。

## ドキュメント参照ポリシー（Context7 MCPの活用）

- 参照元: Context7 MCP を用い、Flet公式の最新ドキュメント/サンプル（ID: `/flet-dev/flet`）を常時参照する。
- 対象API（主要）
  - ルーティング: `page.on_route_change`, `page.on_view_pop`, `page.go`, `TemplateRoute`, `page.route`
  - コンポーネント: `UserControl`, `Ref`, `Tabs`/`TabBar`, `AlertDialog`/`CupertinoAlertDialog`, `NavigationRail`/`NavigationDrawer`, `DataTable`
  - レイアウト: `Row`/`Column`/`Container`、`expand`/`expand_loose`
- 実装時は、該当箇所のAPIをContext7で再確認してから記述し、必要に応じてコード例のプロパティ（例: `selected_index`, `on_change`, `content`, `tabs`）を最新仕様に揃える。
- 参考リンク（Context7より）
  - Routing: navigation-and-routing（`on_route_change`, `TemplateRoute`, `page.go`）
  - Tabs: controls/tabs（基本/ネスト/動的追加/プログラム切替/TabBarTheme）
  - Dialog: tutorials/chat（`AlertDialog`の構築と`page.dialog`の操作）
  - Navigation: tutorials/trolli（`NavigationRail`活用、サイドバー構成）/ controls/navigationdrawer
  - Refs: cookbook/control-refs（`Ref`での参照管理）

## エラーハンドリングとログ

- すべての公開関数に型ヒント/Googleスタイルdocstring。
- 例外はユーザ通知（Dialog / SnackBar）と `loguru` での記録を両立。
- API/DB呼出はタイムアウト + リトライ（Application層で実装）を想定。

## アクセシビリティ/操作性

- キーボードショートカット（例: Nで新規、/で検索、?でヘルプ）。
- フォーカスインジケータ、タブナビゲーション、コントラスト配慮。

## パフォーマンスと非同期

- 重い処理は `page.run_async` / スレッド実行 + ローディングUI。
- リスト/ボードは仮想化（可視領域のみ再構成）を意識した構造に。

## ダミー実装とTODOポリシー

- 本フェーズでは、UIの結線を優先し、ロジック層との統合はダミー実装で対応します。
- ダミー実装の原則
  - ViewはProtocolベースのServiceインターフェースに依存し、初期段階は`Dummy*Service`を注入します。
  - 各ダミー箇所には「TODO: 置換予定」「理由（現状できない理由）」「想定置換先（Application/Service/Repository）」をコメントで明記します。
  - 例外ハンドリングやリトライは最小限に留め、統合フェーズで本実装に置換します。
- 現状ロジックで未実現（例と理由）
  - タスクボードの「列内リオーダー/並び順の永続化」
    - 理由: Taskモデル/Repositoryに順序（position/order）カラム/APIが見当たらないため。
    - TODO: モデルに順序フィールド追加 + Repository/Serviceに並び替えAPIを追加。
  - メモのAI処理キュー/非同期ワークフロー（ProcessingMemos）
    - 理由: サービスにジョブディスパッチ/進捗問い合わせのAPIが未整備。
    - TODO: Application層にジョブ管理（キュー/状態遷移）を追加し、UIから操作可能にする。
  - 週間レビューの集計/チャート（完了件数の週次集約など）
    - 理由: 集計用のQueries/Analyticsサービスが未実装。
    - TODO: `logic/queries/` に集計関数を追加し、Service/Application経由で提供。
  - コマンドパレット/グローバル検索（shadcn相当）
    - 理由: 同等UIとショートカットの包括的APIが未定義。
    - TODO: 検索APIとショートカットマップを定義し、段階的に提供。

## 破壊的変更方針（置換/削除）

- 本再実装は破壊的変更を許容し、現行の `src/views/` 配下の実装は新構成に置き換えます。
- 実施内容
  - 旧View/コンポーネント/不要な共有部品（例: AppBar関連）を削除。
  - 新ディレクトリ構成に従い `layout.py`、`shared/`、各画面 `*/view.py` と `components/` を作成。
  - ルーター（`src/router.py`）は新しい `build_layout` に接続するよう更新。
- 影響範囲
  - 旧Viewに依存するimportはビルドエラーとなるため、合わせて呼び出し側の修正を行います。
  - ドキュメント/READMEのUIスクリーンショットや説明は更新が必要です。

## 実装段階（マイルストーン）

1. 基盤整備（0.5w）
   - ディレクトリ/ファイル生成、`theme.py`、BaseView/レイアウト骨格
   - ルーティング接続、Sidebar/Navigation
2. 主要画面スケルトン（1.0w）
   - Home / Projects / Tags / Tasks / Memos / Terms / Settings / WeeklyReview
  - 各画面の最小UI + ダミーデータ描画（Dummy Service注入 + TODOコメント付与）
3. CRUDダイアログ/フォーム（1.0w）
   - Create/Edit 各種フォーム、バリデーション
4. Application層統合（1.0w）
   - DIでサービス接続、実データ読み書き、例外処理
5. 品質（0.5w）
  - ruff/pyright 対応、アクセシビリティ基本対応（フォーカス/コントラスト）
6. 仕上げ（0.5w）
   - テーマ/アクセシビリティ/ショートカット、微調整

想定合計: 4.0〜4.5週間（テスト除外）。

## 受け入れ基準（抜粋）

- すべての公開関数に型ヒントとGoogleスタイルdocstringがある。
- uv/poe の `poe fix`（lint/format）と型チェックがPASS（テストはスコープ外）。
- 指定ルートに移動可能で、主要画面が表示される。
- Projects/Tags/Tasks/Terms/Memos の一覧 + 作成/編集が動作する。
- エラー時にユーザ通知とログ記録が行われる。
- 設定画面でテーマ切替が可能。
 - 旧ビュー実装は削除され、新ディレクトリ構成へ置換されている（AppBar未使用を反映）。
 - ダミー実装箇所にTODOコメントがあり、「理由」と「置換先（どの層/APIに繋ぐか）」が明記されている。

## リスクと対策

- FletのUI制約でshadcn相当のリッチUIが難しい。
  - 対策: 重要度の高い操作を優先し、代替UIを設計。必要に応じてカスタム描画。
- タスクボード等の複雑UIのパフォーマンス。
  - 対策: コントロール階層の簡素化、差分更新、非同期ロード。
- ルーティングと状態の整合。
  - 対策: Stateを単一責任で保持し、画面遷移時に明示的にリロード/破棄。

## 想定インターフェース（例）

```python
# src/views/tasks/view.py（インターフェース例）
from __future__ import annotations
from typing import Any, Protocol
import flet as ft
from .state import TasksViewState, TaskItem

class TasksService(Protocol):
    def list_tasks(self) -> list[dict[str, Any]]: ...
    def create_task(self, payload: dict[str, Any]) -> dict[str, Any]: ...

class TasksView(ft.UserControl):
    """タスク画面のビュー。TasksServiceに依存し、UIイベントを意図に変換する。"""

    def __init__(self, page: ft.Page, service: TasksService) -> None:
        super().__init__()
        self.page = page
        self.service = service
        self.state = TasksViewState()

  def build(self) -> ft.Control:
    # TODO(UI): 検索/フィルタ/ソートはダミー。統合フェーズでServiceに接続して置換する。
    return ft.Column([
      ft.Text("Tasks"),
      ft.ElevatedButton("Reload", on_click=self._on_reload),
    ])

  def load_data(self) -> None:
    self.state.loading = True
    self.update()

    # TODO(DATA): 現在はダミーデータ/ダミーサービス。Application層の実装に置換する。
    # 理由: 並び順/追加メタ情報（例: position, assignee）を含むAPIが現状未整備。
    items = [TaskItem(**d) for d in self.service.list_tasks()]
    self.state.items = items

    self.state.loading = False
    self.update()

    def _on_reload(self, e: ft.ControlEvent) -> None:
        self.load_data()
```

## 作業・レビュー体制

- ブランチ戦略: featureブランチ単位で画面/機能ごとにPR。Conventional Commits遵守。
- ドキュメント: 本OpenSpecを起点に、`docs/app/` に画面仕様の補遺を追記。

## 前提/仮定

- 既存 `src/router.py` を中心にページ切替可能であること。
- Application Service が CRUD API を提供済み、または同等のモックが用意できること。
- Windowsデスクトップ（Fletアプリ）を主ターゲット、Web/モバイルは副次。

---

このプロポーザルに合意後、マイルストーン1（基盤整備）から着手します。レビュー結果に応じて、順次詳細仕様（各画面のUI構成/バリデーション項目/ショートカット一覧）を `docs/app/` に拡充します。
