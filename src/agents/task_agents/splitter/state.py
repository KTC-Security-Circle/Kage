from typing import Annotated, TypedDict

from pydantic import BaseModel, Field

from agents.base import BaseAgentState


class TaskSplitterState(BaseAgentState):
    """タスク分割エージェントの状態を表すクラス.

    Attributes:
        final_response (str): 最終的な応答を表す文字列。
        task_title (str): タスクのタイトル。
        task_description (str): タスクの説明を表す文字列。
    """

    task_title: str
    """タスクのタイトル"""
    task_description: str
    """タスクの説明を表す文字列"""


class TaskSplitterOutput(BaseModel):
    """response to the user."""

    task_titles: list[str] = Field(description="分割されたタスクのタイトルのリスト")
    task_descriptions: list[str] = Field(description="分割されたタスクの説明のリスト")


# TaskSplitterOutput の TypedDict 定義
class TaskSplitterOutputDict(TypedDict):
    """response to the user."""

    task_titles: Annotated[list[str], ..., "分割されたタスクのタイトルのリスト"]
    task_descriptions: Annotated[list[str], ..., "分割されたタスクの説明のリスト"]
