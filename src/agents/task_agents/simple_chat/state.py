from pydantic import BaseModel, Field

from agents.base import BaseAgentState


class SimpleChatState(BaseAgentState):  # type: ignore[misc]
    """シンプルチャットエージェントの状態.

    BaseAgentState は TypedDict なので追加キーを型注釈のみで定義。
    """

    user_message: str
    system_prompt: str | None


class SimpleChatOutput(BaseModel):
    """SimpleChatAgent の出力ツール (構造化出力想定に備え)."""

    reply: str = Field(description="ユーザー入力に対するアシスタントの応答テキスト")
