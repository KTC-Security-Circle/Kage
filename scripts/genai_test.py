# ruff: noqa: T201

from langchain_openvino_genai import ChatOpenVINO, OpenVINOLLM, load_model
from pydantic import BaseModel, Field

model_name = "OpenVINO/Qwen3-8B-int4-cw-ov"
device = "CPU"

model_path = load_model(repo_id=model_name)

ov_llm = OpenVINOLLM.from_model_path(
    model_path=model_path,
    device=device,
)


class TranslationOutput(BaseModel):
    # think: str = Field(..., description="The model's reasoning about the translation.")
    before: str = Field(..., description="The original sentence in English.")
    after: str = Field(..., description="The translated sentence in Japanese.")


chat_model = ChatOpenVINO(llm=ov_llm, verbose=True)
structured_chat_model = chat_model.with_structured_output(TranslationOutput)
messages = [
    (
        "system",
        "You are a helpful translator. Translate the user sentence to Japanese.",
    ),
    ("human", "I love programming."),
]

print(structured_chat_model.invoke(messages))
# structured_chat_model.invoke(messages).pretty_print()
