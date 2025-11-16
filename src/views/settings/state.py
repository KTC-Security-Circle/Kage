"""Settings View State Layer.

【責務】
    State層は設定画面の表示状態の保持を担う。
    Viewが必要とする全ての状態を一元管理し、整合性を保証する。

    - 表示状態の保持（loading, error_message）
    - 編集中の設定値の保持（current snapshot）
    - 保存済み設定値の保持（original snapshot）
    - 未保存変更フラグの自動計算

【責務外（他層の担当）】
    - データの取得・永続化 → SettingsService
    - UI要素の構築 → Presenter
    - イベントハンドリング → View
    - 設定値の検証 → validation.py

【設計上の特徴】
    - BaseViewStateを継承してBaseView契約に準拠
    - 不変スナップショットによる差分自動検知
    - 計算プロパティによる変更検知

【アーキテクチャ上の位置づけ】
    Controller → State.load_snapshot()
                    ↓
    View → State.current
        → State.has_unsaved_changes (自動計算)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from views.shared.base_view import BaseViewState

if TYPE_CHECKING:
    from agents.agent_conf import LLMProvider
    from settings.models import (
        EditableAgentRuntimeSettings,
        EditableUserSettings,
        EditableWindowSettings,
    )


@dataclass(frozen=True, slots=True)
class SettingsSnapshot:
    """設定値のスナップショット（不変）。

    現在の編集状態と保存済み状態の両方をこの型で保持し、
    差分比較により変更検知を行う。
    """

    appearance: EditableUserSettings
    window: EditableWindowSettings
    database_url: str
    agent_provider: LLMProvider
    agent: EditableAgentRuntimeSettings


@dataclass(slots=True)
class SettingsViewState(BaseViewState):
    """SettingsView の表示状態を管理するデータクラス。

    BaseViewStateを継承し、loading/error_messageを持つ。
    スナップショットパターンにより、未保存変更を自動検知する。
    """

    # 現在の編集中スナップショット
    current: SettingsSnapshot | None = None

    # 保存済みスナップショット（差分計算用）
    _original: SettingsSnapshot | None = None

    @property
    def has_unsaved_changes(self) -> bool:
        """未保存の変更があるかを自動計算する。

        Returns:
            変更がある場合True
        """
        if self.current is None or self._original is None:
            return False
        return self.current != self._original

    def load_snapshot(self, snapshot: SettingsSnapshot) -> None:
        """設定スナップショットをロードし、保存済みとしてマークする。

        Args:
            snapshot: ロードする設定スナップショット
        """
        # currentとoriginalに別々のインスタンスを保持
        # frozenなので全フィールドを明示的にコピーして新しいインスタンスを作成
        self.current = snapshot
        # originalには深いコピーを作成（Pydanticモデルもコピー）
        self._original = SettingsSnapshot(
            appearance=snapshot.appearance.model_copy(deep=True),
            window=snapshot.window.model_copy(deep=True),
            database_url=snapshot.database_url,
            agent_provider=snapshot.agent_provider,
            agent=snapshot.agent.model_copy(deep=True),
        )

    def update_current(self, snapshot: SettingsSnapshot) -> None:
        """現在の編集中スナップショットを更新する。

        Args:
            snapshot: 新しいスナップショット
        """
        self.current = snapshot

    def mark_as_saved(self) -> None:
        """現在の状態を保存済みとしてマークする。"""
        if self.current is not None:
            # 深いコピーを作成（Pydanticモデルもコピー）
            self._original = SettingsSnapshot(
                appearance=self.current.appearance.model_copy(deep=True),
                window=self.current.window.model_copy(deep=True),
                database_url=self.current.database_url,
                agent_provider=self.current.agent_provider,
                agent=self.current.agent.model_copy(deep=True),
            )

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
