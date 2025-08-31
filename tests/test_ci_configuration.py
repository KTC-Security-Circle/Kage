"""CI設定のテストモジュール。

GitHub Actions ワークフローの設定が正しく構成されているかを確認するテストを含む。
"""

from pathlib import Path

import yaml


class TestCIConfiguration:
    """CI設定のテストクラス。"""

    def test_lint_workflow_has_path_filters(self) -> None:
        """lint.ymlワークフローがpathsフィルタを持つことを確認。"""
        lint_workflow_path = Path(__file__).parent.parent / ".github" / "workflows" / "lint.yml"

        with lint_workflow_path.open(encoding="utf-8") as f:
            workflow_config = yaml.safe_load(f)

        # pull_request設定を確認（onキーがbooleanとして解釈される問題を回避）
        on_config = workflow_config.get("on") or workflow_config.get(True)
        assert on_config is not None, "lint.ymlにon設定が見つかりません"

        pull_request_config = on_config["pull_request"]
        assert "paths" in pull_request_config, "lint.ymlにpathsが設定されていません"
        expected_paths = ["**.py"]
        for p in expected_paths:
            assert p in pull_request_config["paths"], f"lint.ymlのpathsに{p}が含まれていません"

    def test_format_check_workflow_has_path_filters(self) -> None:
        """format.ymlワークフローがpathsフィルタを持つことを確認。"""
        format_workflow_path = Path(__file__).parent.parent / ".github" / "workflows" / "format.yml"

        with format_workflow_path.open(encoding="utf-8") as f:
            workflow_config = yaml.safe_load(f)

        # pull_request設定を確認（onキーがbooleanとして解釈される問題を回避）
        on_config = workflow_config.get("on") or workflow_config.get(True)
        assert on_config is not None, "format.ymlにon設定が見つかりません"

        pull_request_config = on_config["pull_request"]
        assert "paths" in pull_request_config, "format.ymlにpathsが設定されていません"
        expected_paths = ["**.py"]
        for p in expected_paths:
            assert p in pull_request_config["paths"], f"format.ymlのpathsに{p}が含まれていません"

    def test_assign_label_workflow_has_no_path_filters(self) -> None:
        """assgin_label.ymlワークフローがpath-ignoreフィルタを持たないことを確認。

        ラベル付けはすべてのPRで実行されるべきため、パスフィルタは不要。
        """
        label_workflow_path = Path(__file__).parent.parent / ".github" / "workflows" / "assign_label.yml"

        with label_workflow_path.open(encoding="utf-8") as f:
            workflow_config = yaml.safe_load(f)

        # pull_request設定を確認（onキーがbooleanとして解釈される問題を回避）
        on_config = workflow_config.get("on") or workflow_config.get(True)
        assert on_config is not None, "assgin_label.ymlにon設定が見つかりません"

        pull_request_config = on_config["pull_request"]
        assert "paths-ignore" not in pull_request_config, (
            "assgin_label.ymlにpaths-ignoreが設定されていますが、これは不要です"
        )
        assert "paths" not in pull_request_config, "assgin_label.ymlにpathsが設定されていますが、これは不要です"

    def test_workflow_files_are_valid_yaml(self) -> None:
        """すべてのワークフローファイルが有効なYAMLであることを確認。"""
        workflows_dir = Path(__file__).parent.parent / ".github" / "workflows"

        for workflow_file in workflows_dir.glob("*.yml"):
            with workflow_file.open(encoding="utf-8") as f:
                try:
                    yaml.safe_load(f)
                except yaml.YAMLError as e:
                    msg = f"ワークフローファイル {workflow_file.name} が有効なYAMLではありません: {e}"
                    raise AssertionError(msg) from e
