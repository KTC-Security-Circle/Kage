from typing import Callable

import flet as ft


def create_title() -> ft.Text:
    """タイトルコンポーネントを作成する

    Returns:
        ft.Text: タイトルコンポーネント
    """
    return ft.Text("ホームページ", size=30)


def create_task_form(
    on_add_click: Callable[[ft.ControlEvent], None],
) -> tuple[ft.TextField, ft.TextField, ft.ElevatedButton, ft.Text]:
    """タスク追加フォームを作成する

    Args:
        on_add_click: タスク追加ボタンクリック時のコールバック関数

    Returns:
        tuple: タイトル入力欄、説明入力欄、追加ボタン、メッセージ表示用テキスト
    """
    # タスク追加用のテキストフィールド
    title_field = ft.TextField(label="タスク名", width=300)
    desc_field = ft.TextField(label="説明", width=300)
    add_button = ft.ElevatedButton("タスク追加", on_click=on_add_click)
    msg = ft.Text("")

    return title_field, desc_field, add_button, msg


def create_navigation_button(page: ft.Page) -> ft.ElevatedButton:
    """タスク一覧画面への遷移ボタンを作成する

    Args:
        page: Fletのページオブジェクト

    Returns:
        ft.ElevatedButton: 遷移ボタン
    """
    return ft.ElevatedButton("タスク一覧へ", on_click=lambda _: page.go("/task"))
