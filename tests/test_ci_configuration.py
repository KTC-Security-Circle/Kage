"""CI設定のテストモジュール。

GitHub Actions ワークフローの設定が正しく構成されているかを確認するテストを含む。
"""

from pathlib import Path

import yaml


class TestCIConfiguration:
    """CI設定のテストクラス。"""

    def test_ruff_check_workflow_has_path_filters(self) -> None:
        """ruff_check.ymlワークフローがpath-ignoreフィルタを持つことを確認。"""
        ruff_workflow_path = Path(__file__).parent.parent / ".github" / "workflows" / "ruff_check.yml"

        with ruff_workflow_path.open(encoding="utf-8") as f:
            workflow_config = yaml.safe_load(f)

        # pull_request設定を確認（onキーがbooleanとして解釈される問題を回避）
        on_config = workflow_config.get("on") or workflow_config.get(True)
        assert on_config is not None, "ruff_check.ymlにon設定が見つかりません"

        pull_request_config = on_config["pull_request"]
        assert "paths-ignore" in pull_request_config, "ruff_check.ymlにpaths-ignoreが設定されていません"

        # 期待されるパス無視設定を確認
        expected_ignores = [
            "docs/**",
            "*.md",
            "README.md",
            "CONTRIBUTING.md",
            ".github/ISSUE_TEMPLATE/**",
            ".github/PULL_REQUEST_TEMPLATE.md",
            ".github/copilot-instructions.md",
            ".github/workflows/**",
            ".pre-commit-config.yaml",
            "pyproject.toml",
            ".vscode/**",
            ".gitignore",
            "uv.lock",
            ".python-version",
        ]

        paths_ignore = pull_request_config["paths-ignore"]
        for expected_ignore in expected_ignores:
            assert expected_ignore in paths_ignore, f"ruff_check.ymlのpaths-ignoreに{expected_ignore}が含まれていません"

    def test_pyright_check_workflow_has_path_filters(self) -> None:
        """pyright_check.ymlワークフローがpath-ignoreフィルタを持つことを確認。"""
        pyright_workflow_path = Path(__file__).parent.parent / ".github" / "workflows" / "pyright_check.yml"

        with pyright_workflow_path.open(encoding="utf-8") as f:
            workflow_config = yaml.safe_load(f)

        # pull_request設定を確認（onキーがbooleanとして解釈される問題を回避）
        on_config = workflow_config.get("on") or workflow_config.get(True)
        assert on_config is not None, "pyright_check.ymlにon設定が見つかりません"

        pull_request_config = on_config["pull_request"]
        assert "paths-ignore" in pull_request_config, "pyright_check.ymlにpaths-ignoreが設定されていません"

        # 期待されるパス無視設定を確認
        expected_ignores = [
            "docs/**",
            "*.md",
            "README.md",
            "CONTRIBUTING.md",
            ".github/ISSUE_TEMPLATE/**",
            ".github/PULL_REQUEST_TEMPLATE.md",
            ".github/copilot-instructions.md",
            ".github/workflows/**",
            ".pre-commit-config.yaml",
            "pyproject.toml",
            ".vscode/**",
            ".gitignore",
            "uv.lock",
            ".python-version",
        ]

        paths_ignore = pull_request_config["paths-ignore"]
        for expected_ignore in expected_ignores:
            assert expected_ignore in paths_ignore, (
                f"pyright_check.ymlのpaths-ignoreに{expected_ignore}が含まれていません"
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

    def test_ci_workflows_have_consistent_path_ignores(self) -> None:
        """CI実行ワークフローが一貫したpath-ignoreを持つことを確認。"""
        ci_workflows = ["ruff_check.yml", "pyright_check.yml"]
        workflows_dir = Path(__file__).parent.parent / ".github" / "workflows"

        path_ignores_by_workflow: dict[str, list[str]] = {}

        for workflow_name in ci_workflows:
            workflow_path = workflows_dir / workflow_name
            with workflow_path.open(encoding="utf-8") as f:
                workflow_config = yaml.safe_load(f)

            # pull_request設定を確認（onキーがbooleanとして解釈される問題を回避）
            on_config = workflow_config.get("on") or workflow_config.get(True)
            assert on_config is not None, f"{workflow_name}にon設定が見つかりません"

            pull_request_config = on_config["pull_request"]
            if "paths-ignore" in pull_request_config:
                path_ignores_by_workflow[workflow_name] = pull_request_config["paths-ignore"]

        # すべてのワークフローが同じpath-ignoreを持つことを確認
        if len(path_ignores_by_workflow) > 1:
            first_workflow = next(iter(path_ignores_by_workflow.keys()))
            first_ignores = set(path_ignores_by_workflow[first_workflow])

            for workflow_name, ignores in path_ignores_by_workflow.items():
                if workflow_name != first_workflow:
                    current_ignores = set(ignores)
                    assert first_ignores == current_ignores, (
                        f"ワークフロー {workflow_name} と {first_workflow} のpath-ignoreが一致しません"
                    )
