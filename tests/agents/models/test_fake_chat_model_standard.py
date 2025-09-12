from langchain_core.language_models.chat_models import BaseChatModel
from langchain_tests.unit_tests import ChatModelUnitTests

from agents.utils import FakeListChatModelWithBindTools


class TestFakeChatModelStandard(ChatModelUnitTests):
    """LangChain標準ChatModel単体テスト適用.

    FakeListChatModelWithBindTools が LangChain の期待インターフェイスに
    どこまで準拠しているかを可視化する目的。標準テスト側は `self.chat_model_class` /
    `self.chat_model_params` を属性として直接参照するため fixture ではなく
    property で提供する。
    """

    @property  # type: ignore[override]
    def chat_model_class(self) -> type[BaseChatModel]:
        return FakeListChatModelWithBindTools

    @property  # type: ignore[override]
    def chat_model_params(self) -> dict[str, object]:
        # 標準テストが複数回インスタンス化する可能性があるので
        # responses は短くても2件以上与えて安全に。
        return {"responses": ['{"value":1}', '{"value":2}']}
