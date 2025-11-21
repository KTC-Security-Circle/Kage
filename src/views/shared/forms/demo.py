"""フォームコンポーネントのテストとデモ

共通フォームコンポーネントの動作確認用デモ。
Task #14 の成果確認として実装。
"""

# pyright: reportAbstractUsage=false, reportAttributeAccessIssue=false

from __future__ import annotations

import flet as ft
from loguru import logger

from src.views.shared.forms import (
    BaseForm,
    FormValidator,
    TextFieldConfig,
    TextFormField,
    ValidationRule,
)


class DemoForm(BaseForm):
    """フォームコンポーネントのデモフォーム。

    基本的なフィールドとバリデーションの動作を確認。
    """

    def __init__(self) -> None:
        """デモフォームを初期化。"""
        super().__init__()
        self._setup_fields()

    def _setup_fields(self) -> None:
        """フィールドを設定。"""
        # タスクタイトル用フィールド
        task_title_field = TextFormField(
            name="title",
            label="タスクタイトル",
            config=TextFieldConfig(
                hint_text="やるべきことを入力してください",
                max_length=100,
            ),
            required=True,
            validators=[FormValidator.create_task_title_validator()],
        )

        # メモタイトル用フィールド
        memo_title_field = TextFormField(
            name="memo_title",
            label="メモタイトル",
            config=TextFieldConfig(
                hint_text="メモのタイトルを入力",
                max_length=200,
            ),
            required=True,
            validators=[FormValidator.create_memo_title_validator()],
        )

        # メモ内容用フィールド（複数行）
        memo_content_field = TextFormField(
            name="memo_content",
            label="メモ内容",
            config=TextFieldConfig(
                hint_text="メモの詳細を記述してください",
                multiline=True,
            ),
            required=False,
            validators=[ValidationRule.max_length(2000)],
        )

        # フィールドを追加
        self.add_field("title", task_title_field)
        self.add_field("memo_title", memo_title_field)
        self.add_field("memo_content", memo_content_field)

    def on_submit(self, data: dict[str, str]) -> None:
        """フォーム送信時の処理。

        Args:
            data: フォームデータ
        """
        logger.info("=== フォーム送信データ ===")
        for key, value in data.items():
            logger.info(f"{key}: {value}")
        logger.info("=" * 25)


def create_demo_app() -> ft.Control:
    """デモアプリケーションのUIを作成。

    Returns:
        デモアプリのルートコントロール
    """
    demo_form = DemoForm()

    # 送信ボタン
    submit_button = ft.ElevatedButton(
        "フォーム送信",
        on_click=lambda _: _handle_submit(demo_form),
    )

    # リセットボタン
    reset_button = ft.OutlinedButton(
        "リセット",
        on_click=lambda _: _handle_reset(demo_form),
    )

    return ft.Column(
        controls=[
            ft.Text("フォームコンポーネントデモ", style=ft.TextThemeStyle.HEADLINE_MEDIUM),
            ft.Divider(),
            *demo_form.build(),
            ft.Row(
                controls=[submit_button, reset_button],
                spacing=10,
            ),
        ],
        spacing=20,
        scroll=ft.ScrollMode.AUTO,
    )


def _handle_submit(form: DemoForm) -> None:
    """フォーム送信処理。

    Args:
        form: 送信するフォーム
    """
    if form.validate():
        data = form.get_data()
        form.on_submit(data)
    else:
        logger.warning("バリデーションエラーがあります")


def _handle_reset(form: DemoForm) -> None:
    """フォームリセット処理。

    Args:
        form: リセットするフォーム
    """
    form.reset()
    logger.info("フォームをリセットしました")


def main(page: ft.Page) -> None:
    """メイン関数。

    Args:
        page: Fletページ
    """
    page.title = "フォームコンポーネントデモ"
    page.theme_mode = ft.ThemeMode.SYSTEM
    page.scroll = ft.ScrollMode.AUTO

    # デモアプリを追加
    page.add(create_demo_app())


if __name__ == "__main__":
    ft.app(target=main)
