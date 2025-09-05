from langchain_core.prompts import ChatPromptTemplate

SIMPLE_CHAT_SYSTEM_PROMPT = (
    "あなたは親切で簡潔なアシスタントです。ユーザーの質問や依頼に対し、"
    "過度に冗長にならず要点をわかりやすく日本語で返答してください。必要なら箇条書きも活用します。"
)

SIMPLE_CHAT_HUMAN_PROMPT = """ユーザー入力: {user_message}
"""

simple_chat_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "{system_prompt}"),
        ("human", SIMPLE_CHAT_HUMAN_PROMPT),
    ]
)
