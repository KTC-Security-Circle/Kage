# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "kage",
# ]
#
# [tool.uv.sources]
# kage = { path = "../" }
# ///
"""環境変数レジストリと初期設定YAMLをドキュメントへ反映するスクリプト。

[AI GENERATED] `ENV_VARS` 定義と `AppSettings` のデフォルトインスタンスを用いて
`docs/dev/configuration.md` のマーカー区間を自動更新する。

実行手順:
    # workspace ルートで実行
    uv run python -m src.scripts.generate_env_docs

差分:
    - <!-- BEGIN:ENV_VARS_TABLE --> ～ <!-- END:ENV_VARS_TABLE -->
    - <!-- BEGIN:DEFAULT_CONFIG_YAML --> ～ <!-- END:DEFAULT_CONFIG_YAML -->
"""

from __future__ import annotations

from pathlib import Path

from loguru import logger
from ruamel.yaml import YAML

from logging_conf import setup_logger
from settings.models import ENV_VARS, AppSettings

setup_logger()

DOC_PATH = Path("docs/dev/configuration.md")

ENV_TABLE_BEGIN = "<!-- BEGIN:ENV_VARS_TABLE -->"
ENV_TABLE_END = "<!-- END:ENV_VARS_TABLE -->"
CFG_BEGIN = "<!-- BEGIN:DEFAULT_CONFIG_YAML -->"
CFG_END = "<!-- END:DEFAULT_CONFIG_YAML -->"


def _render_env_table() -> str:
    """ENV_VARS から Markdown テーブルを生成する。

    Returns:
        str: テーブル本文 (ヘッダ含む)
    """
    headers = ["キー", "型", "カテゴリ", "デフォルト", "コメント"]
    lines = ["| " + " | ".join(headers) + " |", "|" + "|".join(["---"] * len(headers)) + "|"]
    lines.extend(
        "| {k} | {t} | {c} | {d} | {m} |".format(
            k=var.key,
            t=var.type,
            c=var.category,
            d=(var.default if var.default is not None else ""),
            m=(var.comment or ""),
        )
        for var in ENV_VARS
    )
    return "\n" + "\n".join(lines) + "\n"


def _render_default_yaml() -> str:
    """AppSettings のデフォルトインスタンスを YAML 文字列にする。"""
    settings = AppSettings()  # デフォルト値
    yaml = YAML()
    yaml.indent(mapping=2, sequence=4, offset=2)
    data = {
        "window": {"size": settings.window.size, "position": settings.window.position},
        "user": {"last_login_user": settings.user.last_login_user, "theme": settings.user.theme},
        "database": {"url": settings.database.url},
    }
    from io import StringIO

    buf = StringIO()
    yaml.dump(data, buf)
    return "\n```yaml\n" + buf.getvalue().rstrip() + "\n```\n"


def _replace_block(lines: list[str], begin: str, end: str, payload: str) -> list[str]:
    """マーカーで囲まれたブロックを置換する。

    Args:
        lines: 元ファイル行リスト
        begin: 開始マーカー
        end: 終了マーカー
        payload: 挿入する本文 (先頭末尾に改行を含めてもよい)

    Returns:
        list[str]: 置換後行
    """
    try:
        i_begin = next(idx for idx, line in enumerate(lines) if begin in line)
        i_end = next(idx for idx, line in enumerate(lines) if end in line)
    except StopIteration as exc:  # pragma: no cover - ドキュメント破損時のみ
        msg = "マーカーが見つかりません"
        raise SystemExit(msg) from exc
    # keep marker lines, replace inner region
    new_block = [lines[i_begin], payload, lines[i_end]]
    return lines[:i_begin] + new_block + lines[i_end + 1 :]


def generate() -> None:
    """ドキュメントを更新するメイン処理。"""
    text = DOC_PATH.read_text(encoding="utf-8")
    lines = text.splitlines()
    lines = _replace_block(lines, ENV_TABLE_BEGIN, ENV_TABLE_END, _render_env_table())
    lines = _replace_block(lines, CFG_BEGIN, CFG_END, _render_default_yaml())
    DOC_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":  # スクリプト実行入口
    generate()
    logger.info(f"ドキュメントを更新しました: {DOC_PATH}")
