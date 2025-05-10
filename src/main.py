import flet as ft
from flet.core.types import OptionalControlEventCallable


def main(page: ft.Page) -> None:
    counter = ft.Text("0", size=50, data=0)

    def increment_click(_: OptionalControlEventCallable) -> None:
        counter.data += 1
        counter.value = str(counter.data)
        counter.update()

    page.floating_action_button = ft.FloatingActionButton(
        icon=ft.Icons.ADD,
        on_click=increment_click,
    )
    page.add(
        ft.SafeArea(
            ft.Container(
                counter, alignment=ft.alignment.center,
            ),
            expand=True,
        ),
    )


ft.app(main)
