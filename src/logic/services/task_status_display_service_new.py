"""タスクステータス表示サービス

TaskStatusの表示ラベルとUI表現を管理するドメインサービス。
View層からビジネスロジックを分離するために作成。
"""

from __future__ import annotations

from dataclasses import dataclass

from loguru import logger

from models import TaskStatus


@dataclass
class TaskStatusDisplay:
    """タスクステータス表示情報

    Attributes:
        status: タスクステータス
        label: 表示ラベル
        icon: 表示アイコン
        description: 説明文
        color: 表示色（Fletカラー）
    """

    status: TaskStatus
    label: str
    icon: str
    description: str
    color: str


class TaskStatusDisplayService:
    """タスクステータス表示サービス

    TaskStatusの表示に関するビジネスルールを管理するドメインサービス。
    表示ルールの変更に対して柔軟に対応できる構造を提供します。
    """

    @staticmethod
    def get_task_status_display(status: TaskStatus) -> TaskStatusDisplay:
        """タスクステータスの表示情報を取得

        Args:
            status: タスクステータス

        Returns:
            TaskStatusDisplay: 表示情報

        Raises:
            ValueError: 未対応のステータスが指定された場合
        """
        logger.debug(f"タスクステータス表示情報取得: {status}")

        # [AI GENERATED] ビジネスルール: タスクステータスと表示情報のマッピング
        display_mapping = {
            TaskStatus.INBOX: TaskStatusDisplay(
                status=TaskStatus.INBOX,
                label="📥 整理用",
                icon="📥",
                description="整理が必要な項目",
                color="BLUE_600",
            ),
            TaskStatus.NEXT_ACTION: TaskStatusDisplay(
                status=TaskStatus.NEXT_ACTION,
                label="🎯 次に取るべき行動",
                icon="🎯",
                description="具体的な次のアクション",
                color="GREEN_600",
            ),
            TaskStatus.WAITING_FOR: TaskStatusDisplay(
                status=TaskStatus.WAITING_FOR,
                label="⏳ 待機中",
                icon="⏳",
                description="他の人の対応待ち",
                color="ORANGE_600",
            ),
            TaskStatus.SOMEDAY_MAYBE: TaskStatusDisplay(
                status=TaskStatus.SOMEDAY_MAYBE,
                label="💭 いつかやる",
                icon="💭",
                description="将来やるかもしれない項目",
                color="PURPLE_600",
            ),
            TaskStatus.DELEGATED: TaskStatusDisplay(
                status=TaskStatus.DELEGATED,
                label="👥 委譲済み",
                icon="👥",
                description="他の人に委譲済み",
                color="INDIGO_600",
            ),
            TaskStatus.COMPLETED: TaskStatusDisplay(
                status=TaskStatus.COMPLETED,
                label="✅ 完了",
                icon="✅",
                description="完了したタスク",
                color="GREY_600",
            ),
            TaskStatus.CANCELLED: TaskStatusDisplay(
                status=TaskStatus.CANCELLED,
                label="❌ キャンセル",
                icon="❌",
                description="キャンセルされたタスク",
                color="RED_600",
            ),
        }

        if status not in display_mapping:
            msg = f"未対応のタスクステータス: {status}"
            logger.error(msg)
            raise ValueError(msg)

        display_info = display_mapping[status]
        logger.debug(f"表示情報取得結果: {status} -> {display_info.label}")
        return display_info

    @staticmethod
    def get_board_column_mapping() -> dict[str, list[TaskStatus]]:
        """タスクボードのカラムマッピングを取得

        Returns:
            カラム名とタスクステータスリストのマッピング
        """
        return {
            "CLOSED": [
                TaskStatus.NEXT_ACTION,  # [AI GENERATED] 作業リストとして表示
                TaskStatus.DELEGATED,  # [AI GENERATED] InProgress として表示
                TaskStatus.COMPLETED,  # [AI GENERATED] Done として表示
            ],
            "INBOX": [
                TaskStatus.INBOX,  # [AI GENERATED] 整理用
                TaskStatus.NEXT_ACTION,  # [AI GENERATED] 次に取るべき行動（重複表示）
            ],
        }

    @staticmethod
    def get_board_section_display(section_name: str, status: TaskStatus) -> str:
        """ボードセクションの表示ラベルを取得

        Args:
            section_name: セクション名（"CLOSED" または "INBOX"）
            status: タスクステータス

        Returns:
            表示ラベル

        Raises:
            ValueError: 未対応の組み合わせが指定された場合
        """
        # [AI GENERATED] ビジネスルール: セクション内でのステータス表示ラベル
        section_mapping = {
            "CLOSED": {
                TaskStatus.NEXT_ACTION: "📋 作業リスト",
                TaskStatus.DELEGATED: "🔄 InProgress",
                TaskStatus.COMPLETED: "✅ Done",
            },
            "INBOX": {
                TaskStatus.INBOX: "📥 整理用",
                TaskStatus.NEXT_ACTION: "🎯 次に取るべき行動",
            },
        }

        if section_name not in section_mapping:
            msg = f"未対応のセクション名: {section_name}"
            raise ValueError(msg)

        if status not in section_mapping[section_name]:
            msg = f"セクション '{section_name}' では未対応のステータス: {status}"
            raise ValueError(msg)

        return section_mapping[section_name][status]

    @staticmethod
    def get_all_status_displays() -> list[TaskStatusDisplay]:
        """全てのタスクステータスの表示情報を取得

        Returns:
            全タスクステータスの表示情報リスト
        """
        return [TaskStatusDisplayService.get_task_status_display(status) for status in TaskStatus]
