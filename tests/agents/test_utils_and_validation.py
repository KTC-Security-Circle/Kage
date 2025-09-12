from typing import cast

from pydantic import BaseModel, Field

from agents.agent_conf import LLMProvider
from agents.base import BaseAgent, ErrorAgentOutput
from agents.utils import get_model


class _DummyOutput(BaseModel):
    value: int = Field(description="dummy")


def test_get_model_fake_custom_responses() -> None:
    class RespModel(BaseModel):
        value: int

    fake_resps: list[BaseModel] = [RespModel(value=1), RespModel(value=2)]
    # cast to satisfy invariant list typing requirement (mypy friendliness)
    model = get_model(LLMProvider.FAKE, fake_responses=cast("list[BaseModel]", fake_resps))
    # structured output path check
    bound = model.with_structured_output(RespModel)
    out = bound.invoke("x")
    assert isinstance(out, RespModel)


def test_validate_output_success(simple_chat_agent: BaseAgent) -> None:
    class Dummy(BaseModel):
        response: str

    result = simple_chat_agent.validate_output({"response": "ok"}, Dummy)
    assert isinstance(result, Dummy)


def test_validate_output_forced_error(thread_id: str) -> None:
    from agents.task_agents.simple_chat.agent import SimpleChatAgent

    agent = SimpleChatAgent(LLMProvider.FAKE, error_response=True)

    class Dummy(BaseModel):
        response: str

    result = agent.validate_output({"response": "ng"}, Dummy)
    assert isinstance(result, ErrorAgentOutput)


def test_validate_output_schema_error(simple_chat_agent: BaseAgent) -> None:
    class Dummy(BaseModel):
        response: int

    result = simple_chat_agent.validate_output({"response": "string"}, Dummy)
    assert isinstance(result, ErrorAgentOutput)
