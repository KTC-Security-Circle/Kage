"""ベースViewクラス

すべてのViewクラスの基底となるクラスを提供します。
共通機能とライフサイクル管理を担当します。
"""

from __future__ import annotations

from abc import ABC, abstractmethod

import flet as ft
from loguru import logger


class BaseView(ft.Container, ABC):
    """すべてのViewの基底クラス

    共通機能:
    - ライフサイクル管理（mount/unmount）
    - デフォルトスタイル設定
    - ログ出力の統一
    """

    def __init__(self, page: ft.Page, **kwargs) -> None:  # type: ignore[misc] # noqa: ANN003
        """BaseViewのコンストラクタ

        Args:
            page: Fletのページオブジェクト
            **kwargs: ft.Containerに渡す追加引数
        """
        super().__init__(**kwargs)
        self._page = page
        self._is_mounted = False
        self._view_name = self.__class__.__name__

        # デフォルトスタイルの設定
        self._setup_default_style()

        logger.info(f"{self._view_name} 初期化開始")

    def _setup_default_style(self) -> None:
        """デフォルトスタイルの設定"""
        self.padding = 20
        self.expand = True
        self.bgcolor = ft.Colors.GREY_50

    @abstractmethod
    def build_content(self) -> ft.Control:
        """コンテンツを構築

        サブクラスで実装必須。
        このメソッドでViewの具体的なUIを構築する。

        Returns:
            ft.Control: 構築されたコンテンツ
        """

    def mount(self) -> None:
        """コンポーネントのマウント処理

        初回のみ実行される初期化処理。
        build_content()を呼び出してコンテンツを構築する。
        """
        if not self._is_mounted:
            try:
                self.content = self.build_content()
                self._is_mounted = True
                logger.info(f"{self._view_name} マウント完了")
            except Exception as e:
                logger.error(f"{self._view_name} マウントエラー: {e}")
                # エラー時は簡単なエラー表示
                self.content = ft.Text(
                    f"ビューの読み込みに失敗しました: {e}",
                    color=ft.Colors.RED,
                )
                raise

    def unmount(self) -> None:
        """コンポーネントのアンマウント処理

        リソースのクリーンアップやイベントリスナーの解除を行う。
        """
        if self._is_mounted:
            self._is_mounted = False
            logger.info(f"{self._view_name} アンマウント完了")

    def refresh(self) -> None:
        """ビューの再読み込み

        データの更新やUIの再構築を行う。
        サブクラスでオーバーライドして具体的な更新処理を実装する。
        """
        logger.info(f"{self._view_name} リフレッシュ")
        if self._page:
            self.update()

    @property
    def is_mounted(self) -> bool:
        """マウント状態を取得

        Returns:
            bool: マウント済みの場合True
        """
        return self._is_mounted

    @property
    def page(self) -> ft.Page:
        """Fletページオブジェクトを取得

        Returns:
            ft.Page: Fletのページオブジェクト
        """
        return self._page

    @page.setter
    def page(self, value: ft.Page) -> None:
        """Fletページオブジェクトを設定

        Args:
            value: 設定するFletのページオブジェクト
        """
        self._page = value
