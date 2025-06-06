import flet as ft

from views.home.components import create_navigation_button, create_task_form, create_title
from views.home.logic import HomeLogic


def home_view(page: ft.Page) -> ft.Column:
    """ホーム画面のビューを作成する

    Args:
        page: Fletのページオブジェクト

    Returns:
        ft.Column: ホーム画面のルートコンポーネント
    """
    # コンポーネントの作成
    title = create_title()

    # フォームコンポーネントを作成（ロジックの初期化後にコールバックを設定）
    title_field, desc_field, add_button, msg = create_task_form(lambda _: None)

    # ロジックの初期化
    logic = HomeLogic(title_field, desc_field, msg)

    # ボタンのコールバックを設定
    add_button.on_click = logic.handle_add_task

    # ナビゲーションボタンの作成
    nav_button = create_navigation_button(page)

    # 画面レイアウトの構築
    return ft.Column(
        [
            title,
            title_field,
            desc_field,
            add_button,
            msg,
            nav_button,
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )
