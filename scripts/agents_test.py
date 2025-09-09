# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "kage",
# ]
#
# [tool.uv.sources]
# kage = { path = "../" }
# ///
# ruff: noqa: T201, E501
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_huggingface import ChatHuggingFace, HuggingFacePipeline

from logging_conf import setup_logger

setup_logger()

ov_config = {"PERFORMANCE_HINT": "LATENCY", "NUM_STREAMS": "1", "CACHE_DIR": ""}

ov_llm = HuggingFacePipeline.from_model_id(
    model_id="OpenVINO/Qwen3-8B-int4-cw-ov",
    task="text-generation",
    backend="openvino",
    model_kwargs={"device": "CPU", "ov_config": ov_config, "enable_thinking": False},
    pipeline_kwargs={"max_new_tokens": 32768},
)

user_message = "スターウォーズの世界観について教えて。"

# -- llm test --
template = """あなたは親切で簡潔なアシスタントです。ユーザーの質問や依頼に対し、過度に冗長にならず要点をわかりやすく日本語で返答してください。必要なら箇条書きも活用します。

ユーザー入力: {user_message}"""
prompt = PromptTemplate.from_template(template)
llm_chain = prompt | ov_llm.bind(skip_prompt=True)

# -- run invoke or stream --
# print(llm_chain.invoke({"user_message": "ウミガメのスープ問題について解説して、例を挙げてください。"}))
# for chunk in llm_chain.stream({"user_message": user_message}):
#     print(chunk, end="", flush=True)

# -- chat test --
SIMPLE_CHAT_SYSTEM_PROMPT = (
    "あなたは親切で簡潔なアシスタントです。ユーザーの質問や依頼に対し、"
    "過度に冗長にならず要点をわかりやすく日本語で返答してください。必要なら箇条書きも活用します。"
)

SIMPLE_CHAT_HUMAN_PROMPT = """ユーザー入力: {user_message}
"""
simple_chat_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", SIMPLE_CHAT_SYSTEM_PROMPT),
        ("human", SIMPLE_CHAT_HUMAN_PROMPT),
    ]
)
llm = ChatHuggingFace(llm=ov_llm)
chat_chain = simple_chat_prompt | llm.bind(skip_prompt=True)

# -- run invoke or stream --
# print(chat_chain.invoke({"user_message": user_message}))
# for chunk in chat_chain.stream({"user_message": user_message}):
#     print(chunk.content, end="", flush=True)


# -- structured output test --
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.messages import AIMessage, AIMessageChunk
from pydantic import BaseModel, Field
from dataclasses import dataclass

class ResponseModel(BaseModel):
    conclusion: str = Field(description="Conclusion of the response to the user. Keep it concise.")
    detail: str = Field(description="The body of the text to be returned to the user. Provide it appropriately according to the instructions.")

@dataclass
class ResponseModelWithThinking:
    thinking: str | None = None
    contents: ResponseModel | None = None
    response_text: str | None = None

parser = PydanticOutputParser(pydantic_object=ResponseModel)

def parse_think(ai_message: AIMessage) -> ResponseModelWithThinking:
    """AIMessageから<think>タグ以降のテキストを抽出し、ResponseModelとしてパースして返す関数

    Args:
        ai_message (AIMessage): LLMからのAIMessage

    Returns:
        ResponseModelWithThinking: <think>タグ以降のテキストをパースしたResponseModelWithThinkingインスタンス
    """
    # [AI GENERATED] <think>タグ以降のテキストを抽出
    import re
    # contentがstr型でなければstrに変換
    content = ai_message.content if hasattr(ai_message, "content") else str(ai_message)
    if not isinstance(content, str):
        # listやdictの場合は文字列化
        content = str(content)
    match = re.search(r"<think>(.*?)</think>(.*)", content, re.DOTALL)
    if match:
        # think>タグで囲まれた部分を抽出
        thinking_text = match.group(1).strip()
        # <think>タグ以降のコンテンツ部分のみ抽出
        response_text = match.group(2).strip()
        parser_content = parser.parse(response_text)
    else:
        # <think>タグがなければNoneをセット
        thinking_text = None
        parser_content = None
    # 全体をresponse_textとして保存
    response_text = content.strip()
    # PydanticOutputParserでResponseModelとしてパース
    return ResponseModelWithThinking(thinking=thinking_text, contents=parser_content, response_text=response_text)

parser_prompt = PromptTemplate(
    template="Answer the user query.\n{format_instructions}\n{user_message}\n",
    input_variables=["user_message"],
    partial_variables={"format_instructions": parser.get_format_instructions()},
)
parser_chain = parser_prompt | llm.bind(skip_prompt=True) | parse_think

# -- run invoke or stream --
res = parser_chain.invoke({"user_message": user_message})
print(f"Conclusion: {res.contents.conclusion if res.contents else 'N/A'}")
print(f"Detail: {res.contents.detail if res.contents else 'N/A'}")
print(f"Thinking: {res.thinking if res.thinking else 'N/A'}")
print(f"Raw Response: {res.response_text if res.response_text else 'N/A'}")

