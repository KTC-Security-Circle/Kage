from typing import cast

from pydantic import BaseModel, Field

from agents.agent_conf import LLMProvider
from agents.base import AgentError
from agents.task_agents.one_liner.agent import OneLinerAgent
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


def test_validate_output_success() -> None:
    class Dummy(BaseModel):
        response: str

    agent = OneLinerAgent(LLMProvider.FAKE)
    result = agent.validate_output({"response": "ok"}, Dummy)
    assert isinstance(result, Dummy)


def test_validate_output_forced_error() -> None:
    agent = OneLinerAgent(LLMProvider.FAKE, error_response=True)

    class Dummy(BaseModel):
        response: str

    result = agent.validate_output({"response": "ng"}, Dummy)
    assert isinstance(result, AgentError)


def test_validate_output_schema_error() -> None:
    class Dummy(BaseModel):
        response: int

    agent = OneLinerAgent(LLMProvider.FAKE)
    result = agent.validate_output({"response": "string"}, Dummy)
    assert isinstance(result, AgentError)
