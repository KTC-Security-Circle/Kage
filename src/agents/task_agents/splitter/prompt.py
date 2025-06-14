from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

SPLITTER_AGENT_SYSTEM_PROMPT = """あなたは、タスクを小さなサブタスクに分割するのが得意なアシスタントです。
あなたの役割は、与えられたタスクをより小さく、管理しやすいサブタスクに分割することです。
"""

splitter_agent_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", SPLITTER_AGENT_SYSTEM_PROMPT),
        MessagesPlaceholder("human_msg"),
    ]
)
