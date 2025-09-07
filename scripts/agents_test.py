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
    model_kwargs={"device": "CPU", "ov_config": ov_config},
    # pipeline_kwargs={"max_new_tokens": 10},
)

user_message = "ウミガメのスープ問題について解説して、例を挙げてください。"

# -- llm test --
template = """あなたは親切で簡潔なアシスタントです。ユーザーの質問や依頼に対し、過度に冗長にならず要点をわかりやすく日本語で返答してください。必要なら箇条書きも活用します。

ユーザー入力: {user_message}"""
prompt = PromptTemplate.from_template(template)
llm_chain = prompt | ov_llm

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
chat_chain = simple_chat_prompt | llm

# -- run invoke or stream --
print(chat_chain.invoke({"user_message": user_message}))
# for chunk in chat_chain.stream({"user_message": user_message}):
#     print(chunk.content, end="", flush=True)
