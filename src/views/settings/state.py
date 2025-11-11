"""Settings View State Layer.

【責務】
    State層は設定画面の表示状態の保持を担う。
    Viewが必要とする全ての状態を一元管理し、整合性を保証する。

    - 表示状態の保持（loading, error_message）
    - 編集中の設定値の保持（appearance, database, window）
    - 未保存変更フラグの管理（has_unsaved_changes）

【責務外（他層の担当）】
    - データの取得・永続化 → Controller/ApplicationService
    - UI要素の構築 → Presenter
    - イベントハンドリング → View
    - 設定値の検証 → Controller

【設計上の特徴】
    - BaseViewStateを継承してBaseView契約に準拠
    - 不変更新パターン（dataclasses.replace）

【アーキテクチャ上の位置づけ】
    Controller → State.set_xxx()
                    ↓
    View → State.xxx
        → State.has_unsaved_changes
"""

from __future__ import annotations

from dataclasses import dataclass, field

from settings.models import (
    EditableUserSettings,
    EditableWindowSettings,
)
from views.shared.base_view import BaseViewState


@dataclass(slots=True)
class SettingsViewState(BaseViewState):
    """SettingsView の表示状態を管理するデータクラス。

    BaseViewStateを継承し、loading/error_messageを持つ。
    編集中の設定値はEditableモデルで保持し、保存時にfrozenモデルへ変換する。
    """

    # 編集中の設定値
    appearance_settings: EditableUserSettings = field(default_factory=EditableUserSettings)
    window_settings: EditableWindowSettings = field(default_factory=EditableWindowSettings)
    database_url: str = ""

    # 未保存変更フラグ
    has_unsaved_changes: bool = False

    def mark_as_changed(self) -> None:
        """設定が変更されたことをマークする。"""
        self.has_unsaved_changes = True

    def mark_as_saved(self) -> None:
        """設定が保存されたことをマークする。"""
        self.has_unsaved_changes = False

    def start_loading(self) -> None:
        """ローディング状態を開始する。"""
        self.loading = True

    def stop_loading(self) -> None:
        """ローディング状態を終了する。"""
        self.loading = False

    def set_error(self, error_message: str | None) -> None:
        """エラーメッセージを設定する。

        Args:
            error_message: エラーメッセージ。エラーがない場合はNone
        """
        self.error_message = error_message
