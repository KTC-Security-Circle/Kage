from dataclasses import dataclass

from pydantic import BaseModel, Field

from agents.base import BaseAgentResponse, BaseAgentState


class OneLinerState(BaseAgentState):
    """ワンライナーエージェントの状態.

    以前は `user_message` 単一文字列のみだったが、ホームダッシュボード向けの
    一言生成ではタスク統計など複数値を直接渡した方が責務分離されるため拡張。
    logic 層はコンテキスト値を State として渡すのみでプロンプト組立を行わない。
    """

    today_task_count: int
    overdue_task_count: int
    completed_task_count: int
    progress_summary: str
    user_name: str


class OneLinerOutput(BaseModel):
    """OneLinerAgent の出力モデル"""

    response: str = Field(description="ホーム画面に表示する短い励まし/促しメッセージ")


@dataclass
class OneLinerResult(BaseAgentResponse[OneLinerState]):
    """OneLinerAgent の最終応答モデル（dataclass）。"""

    response: str
