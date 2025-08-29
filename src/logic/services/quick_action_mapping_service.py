"""クイックアクションマッピングサービス

QuickActionCommandとTaskStatusのマッピングロジックを提供するドメインサービス。
View層からビジネスロジックを分離するために作成。
"""

from __future__ import annotations

from loguru import logger

from models import QuickActionCommand, TaskStatus


class QuickActionMappingService:
    """クイックアクションマッピングサービス

    QuickActionCommandとTaskStatusのマッピングルールを管理するドメインサービス。
    ビジネスルールの変更に対して柔軟に対応できる構造を提供します。
    """

    @staticmethod
    def map_quick_action_to_task_status(action: QuickActionCommand) -> TaskStatus:
        """QuickActionCommandをTaskStatusにマッピング

        Args:
            action: クイックアクションコマンド

        Returns:
            TaskStatus: 対応するタスクステータス

        Raises:
            ValueError: 未対応のアクションが指定された場合
        """
        logger.info(f"クイックアクションマッピング: {action}")

        # [AI GENERATED] ビジネスルール: クイックアクションとタスクステータスのマッピング
        mapping = {
            QuickActionCommand.DO_NOW: TaskStatus.NEXT_ACTION,
            QuickActionCommand.DO_NEXT: TaskStatus.NEXT_ACTION,
            QuickActionCommand.DO_SOMEDAY: TaskStatus.SOMEDAY_MAYBE,
            QuickActionCommand.REFERENCE: TaskStatus.INBOX,
        }

        if action not in mapping:
            msg = f"未対応のクイックアクション: {action}"
            logger.error(msg)
            raise ValueError(msg)

        mapped_status = mapping[action]
        logger.info(f"マッピング結果: {action} -> {mapped_status}")
        return mapped_status

    @staticmethod
    def get_available_quick_actions() -> list[QuickActionCommand]:
        """利用可能なクイックアクションのリストを取得

        Returns:
            利用可能なQuickActionCommandのリスト
        """
        return [
            QuickActionCommand.DO_NOW,
            QuickActionCommand.DO_NEXT,
            QuickActionCommand.DO_SOMEDAY,
            QuickActionCommand.REFERENCE,
        ]

    @staticmethod
    def get_quick_action_description(action: QuickActionCommand) -> str:
        """クイックアクションの説明を取得

        Args:
            action: クイックアクションコマンド

        Returns:
            アクションの説明文

        Raises:
            ValueError: 未対応のアクションが指定された場合
        """
        descriptions = {
            QuickActionCommand.DO_NOW: "今すぐ実行すべきタスク",
            QuickActionCommand.DO_NEXT: "次に取るべき行動",
            QuickActionCommand.DO_SOMEDAY: "いつかやるかもしれないタスク",
            QuickActionCommand.REFERENCE: "参考資料や整理が必要な項目",
        }

        if action not in descriptions:
            msg = f"未対応のクイックアクション: {action}"
            raise ValueError(msg)

        return descriptions[action]
