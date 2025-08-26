"""一言コメント生成サービス

ホーム画面に表示するAIによる一言コメントを生成するビジネスロジックを提供します。
ダミー/ルールベース実装から始めて、後からLLM連携に差し替え可能な構成になっています。
"""

import os
import random
from typing import NoReturn

from loguru import logger

from logic.queries.one_liner_queries import OneLinerContext
from logic.services.base import MyBaseError, ServiceBase

# [AI GENERATED] 完了率の閾値定数
HIGH_COMPLETION_THRESHOLD = 0.8
MEDIUM_COMPLETION_THRESHOLD = 0.5


class OneLinerServiceError(MyBaseError):
    """一言コメント生成時のカスタム例外クラス

    Args:
        arg (str): エラーメッセージ
    """

    def __str__(self) -> str:
        return f"一言コメント生成エラー: {self.arg}"


class OneLinerService(ServiceBase[OneLinerServiceError]):
    """一言コメント生成サービス

    ホーム画面に表示するAIによる一言コメントを生成します。
    環境変数 KAGE_USE_LLM_ONE_LINER により、ダミー実装とLLM実装を切り替え可能です。
    """

    def __init__(self) -> None:
        """OneLinerServiceの初期化"""
        self._use_llm = os.getenv("KAGE_USE_LLM_ONE_LINER", "false").lower() == "true"
        logger.debug(f"OneLinerService initialized (LLM enabled: {self._use_llm})")

    def generate(self, context: OneLinerContext) -> str:
        """一言コメントを生成する

        Args:
            context (OneLinerContext): コンテキスト情報

        Returns:
            str: 生成された一言コメント

        Raises:
            OneLinerServiceError: 一言コメント生成に失敗した場合
        """
        try:
            if self._use_llm:
                return self._generate_with_llm(context)
            return self._generate_with_rules(context)
        except Exception as e:
            # [AI GENERATED] エラー時は安全な既定文言を返却
            logger.exception(f"一言コメント生成中にエラーが発生しました: {e}")
            return self._get_default_message()

    def _generate_with_rules(self, context: OneLinerContext) -> str:
        """ルールベースで一言コメントを生成する

        Args:
            context (OneLinerContext): コンテキスト情報

        Returns:
            str: 生成された一言コメント
        """
        logger.debug(f"Generating rule-based comment for context: {context}")

        # [AI GENERATED] コンテキストに基づいたルールベース生成
        total_tasks = context.today_task_count
        completed = context.completed_task_count
        overdue = context.overdue_task_count

        # 期限超過がある場合
        if overdue > 0:
            overdue_messages = [
                f"期限超過のタスクが{overdue}件あります。今日から頑張りましょう！",
                f"{overdue}件のタスクが期限を過ぎています。一つずつ片付けていきましょう。",
                "期限超過のタスクがありますが、焦らずに取り組んでいきましょう！",
            ]
            return random.choice(overdue_messages)  # noqa: S311

        # 完了率に基づくメッセージ
        if total_tasks > 0:
            completion_rate = completed / total_tasks
            if completion_rate >= HIGH_COMPLETION_THRESHOLD:
                high_completion_messages = [
                    "素晴らしい進捗です！この調子で続けていきましょう。",
                    "順調に進んでいますね。今日も頑張りましょう！",
                    "とても良いペースです。継続は力なりですね。",
                ]
                return random.choice(high_completion_messages)  # noqa: S311
            if completion_rate >= MEDIUM_COMPLETION_THRESHOLD:
                medium_completion_messages = [
                    "順調に進んでいます。このまま継続していきましょう。",
                    "良いペースですね。一歩ずつ前進しています。",
                    "着実に進歩しています。この調子で頑張りましょう。",
                ]
                return random.choice(medium_completion_messages)  # noqa: S311
            low_completion_messages = [
                "今日から新たなスタートです。一つずつ取り組んでいきましょう。",
                "まだ始まったばかりです。焦らずに進めていきましょう。",
                "小さな一歩から始めましょう。あなたならできます！",
            ]
            return random.choice(low_completion_messages)  # noqa: S311

        # デフォルトメッセージ（タスクがない場合など）
        default_messages = [
            "今日も一日、頑張っていきましょう！",
            "新しい一日の始まりです。素敵な一日になりますように。",
            "今日はどんな素晴らしいことが待っているでしょうか。",
            "穏やかな一日をお過ごしください。",
        ]
        return random.choice(default_messages)  # noqa: S311

    def _generate_with_llm(self, context: OneLinerContext) -> str:
        """LLMを使用して一言コメントを生成する

        Args:
            context (OneLinerContext): コンテキスト情報

        Returns:
            str: 生成された一言コメント

        Note:
            現在はプレースホルダー実装。将来LLM連携を実装予定。
        """
        logger.debug(f"Generating LLM-based comment for context: {context}")

        # [AI GENERATED] LLM実装は将来の拡張として、現在はルールベースにフォールバック
        logger.info("LLM implementation not yet available, falling back to rule-based generation")
        return self._generate_with_rules(context)

    def _get_default_message(self) -> str:
        """エラー時の既定メッセージを取得する

        Returns:
            str: 安全な既定メッセージ
        """
        return "今日も一日、お疲れさまです。"

    def _log_error_and_raise(self, msg: str) -> NoReturn:
        """エラーメッセージをログに記録し OneLinerServiceError を発生させる

        Args:
            msg (str): エラーメッセージ

        Raises:
            OneLinerServiceError: カスタム例外
        """
        super()._log_error_and_raise(msg, OneLinerServiceError)
