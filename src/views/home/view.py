import flet as ft

from models.task import create_task


def home_view(page: ft.Page) -> ft.Column:
    # タスク追加用のテキストフィールド
    title_field = ft.TextField(label="タスク名", width=300)
    desc_field = ft.TextField(label="説明", width=300)
    msg = ft.Text("")

    def on_add_click(_: ft.ControlEvent) -> None:
        # 入力値でタスクを追加
        if not title_field.value:
            msg.value = "タスク名を入力してください"
            msg.update()
            return
        create_task(title_field.value, desc_field.value)
        msg.value = "タスクを追加しました"
        msg.update()
        title_field.value = ""
        desc_field.value = ""
        title_field.update()
        desc_field.update()

    return ft.Column(
        [
            ft.Text("ホームページ", size=30),
            title_field,
            desc_field,
            ft.ElevatedButton("タスク追加", on_click=on_add_click),
            msg,
            ft.ElevatedButton("タスク一覧へ", on_click=lambda _: page.go("/task")),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )
