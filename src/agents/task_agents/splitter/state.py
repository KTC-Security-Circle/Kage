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
    """
    Output model for task splitting operations containing divided task titles and descriptions.

    Attributes:
        task_titles (list[str]): List of titles for the split tasks.
        task_descriptions (list[str]): List of descriptions corresponding to each split task.
    """
    task_titles: list[str] = Field(description="分割されたタスクのタイトルのリスト")
    task_descriptions: list[str] = Field(description="分割されたタスクの説明のリスト")
