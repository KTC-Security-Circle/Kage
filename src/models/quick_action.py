"""クイックアクションコマンドの定義"""

from enum import Enum


class QuickActionCommand(Enum):
    """クイックアクションコマンド

    ユーザーが選択できるクイックアクションのコマンドを定義します。
    View層とLogic層の境界で使用される共通の値オブジェクトです。
    """

    DO_NOW = "do_now"
    DO_NEXT = "do_next"
    DO_SOMEDAY = "do_someday"
    REFERENCE = "reference"
