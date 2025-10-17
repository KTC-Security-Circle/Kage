"""logic 層のカバレッジを計測して閾値を強制するスクリプト。"""

from __future__ import annotations

import os
import subprocess
import sys

from loguru import logger

DEFAULT_THRESHOLD = 80
TARGET_THRESHOLD = 85


def _resolve_threshold(env_value: str | None) -> int:
    """環境変数からカバレッジ閾値を解決する。

    Args:
        env_value: 環境変数 LOGIC_COV_THRESHOLD の文字列表現。

    Returns:
        使用するカバレッジ閾値。
    """
    if env_value is None:
        return DEFAULT_THRESHOLD

    try:
        return int(env_value)
    except ValueError:
        message = "LOGIC_COV_THRESHOLD must be an integer. Fallback to default 85%."
        logger.warning(message)
        return DEFAULT_THRESHOLD


def main() -> int:
    """Pytest を実行して logic 配下のカバレッジを計測する。"""
    threshold = _resolve_threshold(os.getenv("LOGIC_COV_THRESHOLD"))
    if threshold < TARGET_THRESHOLD:
        logger.info("Using coverage threshold %s%% (target %s%%).", threshold, TARGET_THRESHOLD)
    else:
        logger.info("Using coverage threshold %s%%.", threshold)

    cmd = [
        "pytest",
        "tests/logic",
        "--cov=src/logic",
        "--cov-report=term-missing",
        "--cov-report=html",
        f"--cov-fail-under={threshold}",
    ]

    process = subprocess.run(cmd, check=False)  # noqa: S603
    return process.returncode


if __name__ == "__main__":
    sys.exit(main())
