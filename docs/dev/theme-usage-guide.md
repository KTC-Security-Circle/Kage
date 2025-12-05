# テーマ使用ガイド

このドキュメントは、Kage プロジェクトにおける `src/views/theme.py` の使用方法と、Flet アプリケーションのテーマ管理のベストプラクティスを説明します。

## 目次

1. [概要](#概要)
2. [theme.py の構造](#themepy-の構造)
3. [色の使用方法](#色の使用方法)
4. [Flet のテーマシステム](#flet-のテーマシステム)
5. [実装例](#実装例)
6. [ダークモード対応](#ダークモード対応)

## 概要

`src/views/theme.py` は、アプリケーション全体で使用する色、フォント、間隔、角丸などのデザイントークンを一元管理します。すべてのビューとコンポーネントは、このファイルで定義された関数を使用して色を取得することで、統一されたデザインと容易なテーマ変更を実現します。

### 主な利点

- **一元管理**: すべての色定義が一箇所に集約
- **容易な変更**: theme.py を変更するだけで全体の配色を変更可能
- **ダークモード対応**: ライト/ダークテーマの切り替えが容易
- **型安全性**: すべての関数に型ヒントが付与され、IDE の補完が利用可能

## theme.py の構造

### データクラス

```python
@dataclass
class ColorTokens:
    """色定義のデータクラス"""
    primary: str
    on_primary: str
    secondary: str
    on_secondary: str
    background: str
    on_background: str
    surface: str
    on_surface: str
    error: str
    on_error: str
    success: str
    warning: str
    info: str

@dataclass
class TagColors:
    """タグ用のカラーパレット定義"""
    red: str = "#f44336"
    pink: str = "#e91e63"
    # ... 他の色

@dataclass
class StatusColors:
    """プロジェクト・タスクのステータス色定義"""
    in_progress: str = "#2196f3"
    planned: str = "#ff9800"
    completed: str = "#4caf50"
    on_hold: str = "#9e9e9e"
    cancelled: str = "#f44336"

@dataclass
class UIColors:
    """UI全般で使用する汎用色定義"""
    grey_50: str = "#fafafa"
    # ... 他のグレースケール
    primary: str = "#2196f3"
    error: str = "#f44336"
    success: str = "#4caf50"
```

### 定義済みのテーマ

```python
# ライトテーマ
LIGHT_COLORS = ColorTokens(
    primary="#6750A4",
    on_primary="#FFFFFF",
    # ...
)

# ダークテーマ
DARK_COLORS = ColorTokens(
    primary="#D0BCFF",
    on_primary="#381E72",
    # ...
)
```

## 色の使用方法

### 基本的な使用方法

コンポーネントで色を使用する場合は、必ず `theme.py` から関数をインポートして使用します。

#### ❌ 悪い例（ハードコード）

```python
import flet as ft

# 色を直接指定（NG）
ft.Container(
    bgcolor="#2196f3",
    border=ft.border.all(1, "#e0e0e0"),
)

# Flet の定数を直接使用（NG）
ft.Text("Hello", color=ft.Colors.BLUE_400)
```

#### ✅ 良い例（theme.py を使用）

```python
import flet as ft
from views.theme import (
    get_primary_color,
    get_outline_color,
    get_on_surface_color,
)

# theme.py の関数を使用
ft.Container(
    bgcolor=get_primary_color(),
    border=ft.border.all(1, get_outline_color()),
    content=ft.Text("Hello", color=get_on_surface_color()),
)
```

### 主要な色取得関数

#### プライマリカラー

```python
from views.theme import get_primary_color, get_on_primary_color

# プライマリカラー（例: ボタンの背景）
bgcolor = get_primary_color()

# プライマリカラー上のテキスト色
text_color = get_on_primary_color()
```

#### サーフェスとアウトライン

```python
from views.theme import (
    get_surface_color,           # カード・パネルの背景
    get_on_surface_color,        # サーフェス上のテキスト
    get_surface_variant_color,   # 選択状態などの強調背景
    get_outline_color,           # 境界線・Divider
    get_text_secondary_color,    # 補助テキスト
)

# カードコンポーネント
ft.Container(
    bgcolor=get_surface_color(),
    border=ft.border.all(1, get_outline_color()),
    content=ft.Column([
        ft.Text("タイトル", color=get_on_surface_color()),
        ft.Text("説明", color=get_text_secondary_color()),
    ])
)
```

#### ステータスとエラー

```python
from views.theme import (
    get_status_color,    # ステータス名から色を取得
    get_error_color,     # エラー色
    get_success_color,   # 成功色
)

# ステータスバッジ
status_badge = ft.Container(
    content=ft.Text("進行中"),
    bgcolor=get_status_color("進行中"),
)

# エラーメッセージ
error_msg = ft.Text(
    "エラーが発生しました",
    color=get_error_color(),
)
```

#### グレースケール

```python
from views.theme import get_grey_color

# 50, 100, 200, ..., 900 のシェードが使用可能
light_grey = get_grey_color(100)
medium_grey = get_grey_color(500)
dark_grey = get_grey_color(900)
```

### コンポーネントでの使用例

#### カードコンポーネント

```python
from dataclasses import dataclass
import flet as ft
from views.theme import (
    get_primary_color,
    get_outline_color,
    get_surface_color,
    get_surface_variant_color,
    get_on_surface_color,
    get_text_secondary_color,
)

@dataclass(frozen=True, slots=True)
class CardData:
    title: str
    description: str
    is_selected: bool

class MyCard(ft.Container):
    def __init__(self, data: CardData):
        super().__init__(
            content=ft.Column([
                ft.Text(
                    data.title,
                    color=get_on_surface_color(),
                    weight=ft.FontWeight.BOLD,
                ),
                ft.Text(
                    data.description,
                    color=get_text_secondary_color(),
                ),
            ]),
            bgcolor=get_surface_variant_color() if data.is_selected else get_surface_color(),
            border=ft.border.all(
                width=2 if data.is_selected else 1,
                color=get_primary_color() if data.is_selected else get_outline_color(),
            ),
            padding=16,
            border_radius=8,
        )
```

## Flet のテーマシステム

### ページレベルのテーマ設定

Flet では、`Page` レベルでアプリケーション全体のテーマを設定できます。

```python
import flet as ft

def main(page: ft.Page):
    # ライトテーマの設定
    page.theme = ft.Theme(
        color_scheme=ft.ColorScheme(
            primary="#6750A4",
            secondary="#625B71",
            surface="#FFFBFE",
            background="#FFFBFE",
            error="#BA1A1A",
        )
    )
    
    # ダークテーマの設定
    page.dark_theme = ft.Theme(
        color_scheme=ft.ColorScheme(
            primary="#D0BCFF",
            secondary="#CCC2DC",
            surface="#141218",
            background="#141218",
            error="#F2B8B5",
        )
    )
    
    # テーマモードの設定（SYSTEM, LIGHT, DARK）
    page.theme_mode = ft.ThemeMode.SYSTEM
```

### シードカラーからテーマを生成

```python
# シードカラーから Material Design 3 のカラースキームを自動生成
page.theme = ft.Theme(color_scheme_seed=ft.Colors.GREEN)
```

### 部分的なテーマのオーバーライド

特定のコンテナ配下のみ異なるテーマを適用できます。

```python
ft.Container(
    content=ft.Button("カスタムテーマボタン"),
    theme=ft.Theme(
        color_scheme=ft.ColorScheme(primary=ft.Colors.PINK)
    ),
)
```

### ネストされたテーマ

```python
def main(page: ft.Page):
    # ページ全体のテーマ
    page.theme = ft.Theme(color_scheme_seed=ft.Colors.YELLOW)
    
    page.add(
        # ページのテーマを継承
        ft.Container(
            content=ft.Button("ページテーマ"),
            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
            padding=20,
        ),
        
        # プライマリカラーのみオーバーライド
        ft.Container(
            theme=ft.Theme(
                color_scheme=ft.ColorScheme(primary=ft.Colors.PINK)
            ),
            content=ft.Button("ピンクのボタン"),
            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
            padding=20,
        ),
        
        # 常にダークテーマ
        ft.Container(
            theme=ft.Theme(color_scheme_seed=ft.Colors.INDIGO),
            theme_mode=ft.ThemeMode.DARK,
            content=ft.Button("ダークテーマボタン"),
            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
            padding=20,
        ),
    )
```

## 実装例

### 例1: ステータスタブ

```python
from views.theme import (
    get_primary_color,
    get_surface_color,
    get_surface_variant_color,
    get_on_primary_color,
    get_outline_color,
)

class StatusTabs(ft.Container):
    def __init__(self, statuses: list[str], active_status: str):
        tabs = []
        for status in statuses:
            is_active = status == active_status
            tabs.append(
                ft.Container(
                    content=ft.Text(
                        status,
                        color=get_on_primary_color() if is_active else None,
                    ),
                    bgcolor=get_surface_variant_color() if is_active else ft.Colors.TRANSPARENT,
                    padding=ft.padding.symmetric(horizontal=16, vertical=8),
                    border_radius=8,
                )
            )
        
        super().__init__(
            content=ft.Row(tabs, spacing=8),
            bgcolor=get_surface_color(),
            border=ft.border.only(
                bottom=ft.BorderSide(width=1, color=get_outline_color())
            ),
            padding=8,
        )
```

### 例2: エラーバナー

```python
from views.theme import get_error_color, get_surface_variant_color

def create_error_banner(message: str) -> ft.Container:
    return ft.Container(
        content=ft.Row([
            ft.Icon(ft.Icons.ERROR_OUTLINE, color=get_error_color()),
            ft.Text(message, color=get_error_color(), expand=True),
        ], spacing=8),
        bgcolor=get_surface_variant_color(),
        padding=12,
        border_radius=8,
    )
```

## ダークモード対応

### 現状

現在、`theme.py` には `LIGHT_COLORS` と `DARK_COLORS` の定義がありますが、色取得関数は常にライトテーマを返します。

```python
def get_on_surface_color() -> str:
    """サーフェス上のテキスト色を取得する"""
    return LIGHT_COLORS.on_surface  # 常にライトテーマ
```

### 将来の実装（TODO）

ダークモード対応のためには、以下の実装が必要です：

1. **テーマモード取得関数の追加**

```python
from settings.application_service import SettingsApplicationService

def get_current_theme_mode() -> ft.ThemeMode:
    """現在のテーマモードを取得する"""
    settings_service = SettingsApplicationService(...)
    settings = settings_service.get_settings()
    return settings.appearance.theme_mode
```

2. **動的な色取得**

```python
def get_on_surface_color() -> str:
    """サーフェス上のテキスト色を取得する"""
    theme_mode = get_current_theme_mode()
    if theme_mode == ft.ThemeMode.DARK:
        return DARK_COLORS.on_surface
    return LIGHT_COLORS.on_surface
```

3. **システムテーマの検出**

```python
def get_current_theme_mode() -> ft.ThemeMode:
    settings = get_settings()
    if settings.theme_mode == "system":
        # Flet の page.platform_brightness を使用
        return detect_system_theme()
    return settings.theme_mode
```

## まとめ

### ✅ やるべきこと

- すべての色定義に `theme.py` の関数を使用
- 新しいコンポーネントを作成する際は、最初から theme.py を使用
- 色のハードコードは絶対に避ける

### ❌ やってはいけないこと

- 色を直接 HEX コードで指定
- `ft.Colors.BLUE_400` などの Flet 定数を直接使用
- コンポーネント内で色を定義

### 参考リンク

- [Flet Color Scheme Documentation](https://docs.flet.dev/cookbook/colors)
- [Flet Theme Documentation](https://docs.flet.dev/types/theme)
- [Material Design 3 Color System](https://m3.material.io/styles/color/system/overview)
