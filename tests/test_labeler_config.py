"""labeler設定のテストクラス."""

from pathlib import Path

import yaml


class TestLabelerConfig:
    """Labeler設定のテストクラス."""

    def test_labeler_config_is_valid_yaml(self) -> None:
        """labeler設定ファイルが有効なYAMLであることを確認."""
        labeler_config_path = Path(__file__).parent.parent / ".github" / "labeler_branch.yml"

        # ファイルが存在することを確認
        assert labeler_config_path.exists(), "labeler設定ファイルが存在しません"

        # YAML形式として読み込み可能かを確認
        with labeler_config_path.open(encoding="utf-8") as f:
            config = yaml.safe_load(f)

        assert isinstance(config, dict), "labeler設定は辞書形式である必要があります"
        assert len(config) > 0, "labeler設定は空ではいけません"

    def test_labeler_config_has_required_labels(self) -> None:
        """必要なラベルが設定されていることを確認."""
        labeler_config_path = Path(__file__).parent.parent / ".github" / "labeler_branch.yml"

        with labeler_config_path.open(encoding="utf-8") as f:
            config = yaml.safe_load(f)

        # 必須のラベルが存在することを確認
        required_labels = ["enhancement", "fix", "bug", "docs", "dependencies", "tests"]
        for label in required_labels:
            assert label in config, f"ラベル '{label}' が設定されていません"

    def test_labeler_config_enhancement_includes_feature_and_enhancement_branches(
        self,
    ) -> None:
        """enhancementラベルがfeatureとenhancementブランチに対応していることを確認."""
        labeler_config_path = Path(__file__).parent.parent / ".github" / "labeler_branch.yml"

        with labeler_config_path.open(encoding="utf-8") as f:
            config = yaml.safe_load(f)

        enhancement_config = config.get("enhancement", [])
        assert len(enhancement_config) > 0, "enhancementラベルの設定が空です"

        # ブランチベースの設定を確認
        branch_config = None
        for item in enhancement_config:
            if "head-branch" in item:
                branch_config = item["head-branch"]
                break

        assert branch_config is not None, "enhancementラベルのブランチ設定が見つかりません"
        assert "^feature" in branch_config, "enhancementラベルに^featureパターンが含まれていません"
        assert "^enhancement" in branch_config, "enhancementラベルに^enhancementパターンが含まれていません"

    def test_labeler_config_docs_includes_markdown_files(self) -> None:
        """docsラベルがMarkdownファイルに対応していることを確認."""
        labeler_config_path = Path(__file__).parent.parent / ".github" / "labeler_branch.yml"

        with labeler_config_path.open(encoding="utf-8") as f:
            config = yaml.safe_load(f)

        docs_config = config.get("docs", [])
        assert len(docs_config) > 0, "docsラベルの設定が空です"

        # ファイルベースの設定を確認
        file_config = None
        for item in docs_config:
            if "changed-files" in item:
                file_config = item["changed-files"]
                break

        assert file_config is not None, "docsラベルのファイル設定が見つかりません"

        # any-glob-to-any-fileパターンを確認
        glob_patterns = None
        for item in file_config:
            if "any-glob-to-any-file" in item:
                glob_patterns = item["any-glob-to-any-file"]
                break

        assert glob_patterns is not None, "docsラベルのglob設定が見つかりません"
        assert "*.md" in glob_patterns, "docsラベルに*.mdパターンが含まれていません"
        assert "docs/**/*" in glob_patterns, "docsラベルにdocs/**/*パターンが含まれていません"
