"""ウェルカムメッセージコンポーネント."""

from __future__ import annotations

import flet as ft

from logic.application import OneLinerApplicationService
from logic.factory import get_application_service_container


class WelcomeMessage(ft.Container):
    """AIからのアドバイスを表示するウェルカムメッセージコンポーネント."""

    def __init__(self, page: ft.Page) -> None:
        """WelcomeMessageの初期化

        Args:
            page: Fletのページオブジェクト
        """
        super().__init__()
        self._page = page
        self.alignment = ft.alignment.center

        # 初期状態はプログレスリングを表示
        self.content = ft.ProgressRing()

        # AIからのメッセージを非同期で取得
        self._load_ai_message()

    def _load_ai_message(self) -> None:
        """AIからのメッセージを非同期で取得し、表示を更新."""
        import threading

        def fetch_message() -> None:
            """[AI GENERATED] AIサービスからメッセージを取得する処理"""
            try:
                service_factory = get_application_service_container()
                service = service_factory.get_service(OneLinerApplicationService)
                ai_text = service.generate_one_liner()

                # UIスレッドでメッセージを更新
                self._update_message(ai_text)
            except Exception:
                # エラー時はデフォルトメッセージを表示
                self._update_message("今日も一日頑張りましょう！")

        # バックグラウンドスレッドでAIメッセージを取得
        thread = threading.Thread(target=fetch_message)
        thread.daemon = True
        thread.start()

    def _update_message(self, message: str) -> None:
        """メッセージを更新してUIを再描画.

        Args:
            message: 表示するメッセージ
        """
        self.content = ft.Text(
            message,
            size=18,
            # color=ft.Colors.GREY_700,
        )
        # ページを更新してUIに反映
        if self._page:
            self._page.update()
