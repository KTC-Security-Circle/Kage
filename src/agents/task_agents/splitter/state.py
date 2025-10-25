from __future__ import annotations

from typing import NotRequired

from pydantic import BaseModel, Field

from agents.base import BaseAgentState, ErrorAgentOutput


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
    candidate_output: NotRequired[TaskSplitterOutput]
    """一次分割結果。"""
    refined_output: NotRequired[TaskSplitterOutput]
    """整形済みの分割結果。"""
    error_output: NotRequired[ErrorAgentOutput]
    """エラー結果。"""


class TaskSplitterOutput(BaseModel):
    """Output model for task splitting operations containing divided task titles and descriptions.

    Attributes:
        task_titles (list[str]): List of titles for the split tasks.
        task_descriptions (list[str]): List of descriptions corresponding to each split task.
    """

    task_titles: list[str] = Field(description="分割されたタスクのタイトルのリスト")
    task_descriptions: list[str] = Field(description="分割されたタスクの説明のリスト")
