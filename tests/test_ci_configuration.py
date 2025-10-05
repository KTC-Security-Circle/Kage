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

    def test_lint_workflow_supports_all_branches(self) -> None:
        """lint.ymlワークフローがすべてのブランチのPRに対応していることを確認。"""
        lint_workflow_path = Path(__file__).parent.parent / ".github" / "workflows" / "lint.yml"

        with lint_workflow_path.open(encoding="utf-8") as f:
            workflow_config = yaml.safe_load(f)

        on_config = workflow_config.get("on") or workflow_config.get(True)
        assert on_config is not None, "lint.ymlにon設定が見つかりません"

        pull_request_config = on_config["pull_request"]
        assert "branches" not in pull_request_config, (
            "lint.ymlのpull_requestトリガーにbranchesが設定されていますが、すべてのブランチで実行されるべきです"
        )

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

    def test_format_workflow_supports_all_branches(self) -> None:
        """format.ymlワークフローがすべてのブランチのPRに対応していることを確認。"""
        format_workflow_path = Path(__file__).parent.parent / ".github" / "workflows" / "format.yml"

        with format_workflow_path.open(encoding="utf-8") as f:
            workflow_config = yaml.safe_load(f)

        on_config = workflow_config.get("on") or workflow_config.get(True)
        assert on_config is not None, "format.ymlにon設定が見つかりません"

        pull_request_config = on_config["pull_request"]
        assert "branches" not in pull_request_config, (
            "format.ymlのpull_requestトリガーにbranchesが設定されていますが、すべてのブランチで実行されるべきです"
        )

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

    def test_assign_label_workflow_supports_all_branches_and_issues(self) -> None:
        """assign_label.ymlワークフローがすべてのブランチのPRとissueに対応していることを確認。

        ラベル付けは対象ブランチに関係なくすべてのPRとissueで実行されるべき。
        """
        label_workflow_path = Path(__file__).parent.parent / ".github" / "workflows" / "assign_label.yml"

        with label_workflow_path.open(encoding="utf-8") as f:
            workflow_config = yaml.safe_load(f)

        on_config = workflow_config.get("on") or workflow_config.get(True)
        assert on_config is not None, "assgin_label.ymlにon設定が見つかりません"

        # PRとissue両方のトリガーが設定されていることを確認
        assert "pull_request" in on_config, "assign_label.ymlにpull_requestトリガーが設定されていません"
        assert "issues" in on_config, "assign_label.ymlにissuesトリガーが設定されていません"

        # PRトリガーにブランチ制限がないことを確認
        pull_request_config = on_config["pull_request"]
        assert "branches" not in pull_request_config, (
            "assign_label.ymlのpull_requestトリガーにbranchesが設定されていますが、すべてのブランチで実行されるべきです"
        )

    def test_test_workflow_supports_all_branches(self) -> None:
        """test.ymlワークフローがすべてのブランチのPRに対応していることを確認。"""
        test_workflow_path = Path(__file__).parent.parent / ".github" / "workflows" / "test.yml"

        with test_workflow_path.open(encoding="utf-8") as f:
            workflow_config = yaml.safe_load(f)

        on_config = workflow_config.get("on") or workflow_config.get(True)
        assert on_config is not None, "test.ymlにon設定が見つかりません"

        pull_request_config = on_config["pull_request"]
        assert "branches" not in pull_request_config, (
            "test.ymlのpull_requestトリガーにbranchesが設定されていますが、すべてのブランチで実行されるべきです"
        )

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
