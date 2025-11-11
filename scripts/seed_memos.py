"""初期メモ投入スクリプト

アプリケーションのデータベースへ開発・検証用のメモを投入します。
既存ID重複は考慮せず常に新規作成します。必要に応じてDBを再作成してください。

使用方法 (PowerShell):
    uv run python scripts/seed_memos.py

将来拡張:
- 既存件数に応じたスキップ/重複チェック
- タグ/タスクの同時生成
"""

from __future__ import annotations

from dataclasses import dataclass

from loguru import logger

from logic.application.apps import ApplicationServices


@dataclass(slots=True)
class SeedMemo:
    title: str
    content: str


SEED_MEMOS: tuple[SeedMemo, ...] = (
    SeedMemo(
        title="Kage設計メモ",
        content="ビュー層整理: BaseView導入後の責務分離を確認する。",
    ),
    SeedMemo(
        title="LLM連携TODO",
        content="MemoToTaskAgentの初期プロンプト整備。設定キャッシュのinvalidate手順検証。",
    ),
    SeedMemo(
        title="タスク管理改善案",
        content="ステータス遷移: inbox→active→archive のルールを明文化。",
    ),
    SeedMemo(
        title="検索UX",
        content="全文検索より prefix / fuzzy の切替トグルを検討。",
    ),
)


def main() -> None:
    apps = ApplicationServices.create()
    created_ids: list[str] = []
    for seed in SEED_MEMOS:
        try:
            memo = apps.memo.create(title=seed.title, content=seed.content)
            created_ids.append(str(memo.id))
            logger.info(f"メモ作成: {memo.id} - {seed.title}")
        except Exception as exc:  # 開発用シードなので包括キャッチ
            logger.error(f"メモ作成失敗: {seed.title} ({type(exc).__name__}: {exc})")

    logger.info(f"投入完了 件数={len(created_ids)} IDs={created_ids}")


if __name__ == "__main__":  # pragma: no cover
    main()
