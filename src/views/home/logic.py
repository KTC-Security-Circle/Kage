import flet as ft

from models.task import create_task


class HomeLogic:
    """ホーム画面のロジックを管理するクラス"""

    def __init__(self, title_field: ft.TextField, desc_field: ft.TextField, msg: ft.Text) -> None:
        """初期化

        Args:
            title_field: タイトル入力欄
            desc_field: 説明入力欄
            msg: メッセージ表示用テキスト
        """
        self.title_field = title_field
        self.desc_field = desc_field
        self.msg = msg

    def handle_add_task(self, _: ft.ControlEvent) -> None:
        """タスク追加ボタンのクリックイベントハンドラ

        Args:
            _: Fletのイベントオブジェクト(使用しない)
        """
        # 入力値でタスクを追加
        if not self.title_field.value:
            self.msg.value = "タスク名を入力してください"
            self.msg.update()
            return

        # タスク作成処理を呼び出し
        create_task(self.title_field.value, self.desc_field.value)

        # 成功メッセージを表示
        self.msg.value = "タスクを追加しました"
        self.msg.update()

        # 入力欄をクリア
        self.title_field.value = ""
        self.desc_field.value = ""
        self.title_field.update()
        self.desc_field.update()
