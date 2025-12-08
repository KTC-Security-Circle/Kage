"""HuggingFaceAgentModels の保存時のバリデーションテスト。

Issue #279 の修正を検証する。
EditableHuggingFaceAgentModels から HuggingFaceAgentModels への変換時に
one_liner が None でないことを確認する。
"""

from pathlib import Path

from settings.manager import ConfigManager
from settings.models import AppSettings


def test_huggingface_model_default_not_none(tmp_path: Path) -> None:
    """EditableHuggingFaceAgentModels の one_liner デフォルト値が None でないことを確認。"""
    from agents.agent_conf import HuggingFaceModel
    from settings.models import EditableHuggingFaceAgentModels

    editable = EditableHuggingFaceAgentModels()
    assert editable.one_liner is not None
    assert editable.one_liner == HuggingFaceModel.QWEN_3_8B_INT4


def test_config_save_with_huggingface_settings(tmp_path: Path) -> None:
    """HuggingFace モデル設定を含む設定の保存と再読み込みが成功することを確認。

    Issue #279: EditableHuggingFaceAgentModels.one_liner が None の場合、
    frozen モデルへの変換時に validation error が発生する問題の回帰テスト。
    """
    from agents.agent_conf import LLMProvider

    cfg_path = tmp_path / "app_config.yaml"
    mgr = ConfigManager(cfg_path, AppSettings)

    # HuggingFace モデルを含む設定を編集して保存
    with mgr.edit() as editable:
        editable.agents.provider = LLMProvider.OPENVINO
        # one_liner はデフォルト値のまま（明示的に設定しない）

    # 再読み込みして保存された値を確認
    mgr2 = ConfigManager(cfg_path, AppSettings)
    assert mgr2.settings.agents.provider == LLMProvider.OPENVINO
    assert mgr2.settings.agents.huggingface.one_liner is not None


def test_config_save_after_provider_change(tmp_path: Path) -> None:
    """プロバイダ変更後の設定保存が成功することを確認。

    UI でプロバイダを変更した後に保存するシナリオをシミュレート。
    """
    from agents.agent_conf import HuggingFaceModel, LLMProvider

    cfg_path = tmp_path / "app_config.yaml"
    mgr = ConfigManager(cfg_path, AppSettings)

    # 初期状態: FAKE プロバイダ
    assert mgr.settings.agents.provider == LLMProvider.FAKE

    # OPENVINO プロバイダに変更して保存
    with mgr.edit() as editable:
        editable.agents.provider = LLMProvider.OPENVINO

    # 再度編集コンテキストに入って保存（Issue #279 で失敗していたシナリオ）
    with mgr.edit() as editable:
        # 何も変更せずに保存を試みる
        pass

    # 保存が成功し、設定が保持されていることを確認
    mgr3 = ConfigManager(cfg_path, AppSettings)
    assert mgr3.settings.agents.provider == LLMProvider.OPENVINO
    assert mgr3.settings.agents.huggingface.one_liner == HuggingFaceModel.QWEN_3_8B_INT4
