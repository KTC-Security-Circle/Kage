# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "kage",
# ]
#
# [tool.uv.sources]
# kage = { path = "../", editable = true }
# ///
"""UI 検証用のサンプルデータ投入スクリプト。

アプリケーション層 (`ApplicationServices`) を経由して、主要エンティティに
多めのデータを生成します。各ステータスやビューが網羅されるように
プロジェクト/タスク/メモ/タグ/社内用語を作成・更新します。

使用方法:
    # データ投入のみ
    uv run python scripts/seed_sample_data.py

    # マイグレーション実行後にデータ投入 (推奨)
    uv run poe sample-data
    # または
    uv run poe sample-data

データベースを初期化した直後、または UI をまとめて確認したいタイミングで実行してください。
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import TYPE_CHECKING, TypeVar

from loguru import logger

from errors import NotFoundError
from logic.application.apps import ApplicationServices
from logic.unit_of_work import SqlModelUnitOfWork
from models import (
    MemoStatus,
    MemoUpdate,
    ProjectStatus,
    ProjectUpdate,
    TagUpdate,
    Task,
    TaskStatus,
    TaskUpdate,
    TermStatus,
    TermUpdate,
)

if TYPE_CHECKING:
    import uuid
    from collections.abc import Callable

_T = TypeVar("_T")


@dataclass(slots=True)
class TagSeed:
    """タグ投入用の定義。"""

    key: str
    name: str
    description: str
    color: str


@dataclass(slots=True)
class ProjectSeed:
    """プロジェクト投入用の定義。"""

    key: str
    title: str
    description: str
    status: ProjectStatus
    due_in_days: int | None


@dataclass(slots=True)
class MemoSeed:
    """メモ投入用の定義。"""

    key: str
    title: str
    content: str
    status: MemoStatus


@dataclass(slots=True)
class TaskSeed:
    """タスク投入用の定義。"""

    key: str
    title: str
    description: str
    status: TaskStatus
    project_key: str | None = None
    memo_key: str | None = None
    due_in_days: int | None = None
    completed_offset_days: int | None = None
    created_offset_days: int | None = None


@dataclass(slots=True)
class TermSeed:
    """社内用語投入用の定義。"""

    key: str
    title: str
    description: str
    status: TermStatus
    source_url: str | None = None


TAG_SEEDS: tuple[TagSeed, ...] = (
    TagSeed(
        key="urgent",
        name="至急対応",
        description="期限が迫っているアクション用タグ。",
        color="#EF5350",
    ),
    TagSeed(
        key="design",
        name="UIデザイン",
        description="UI/UX 改善タスクの整理。",
        color="#7E57C2",
    ),
    TagSeed(
        key="automation",
        name="自動化",
        description="バッチ・自動実行関連のメモやタスク。",
        color="#26A69A",
    ),
    TagSeed(
        key="research",
        name="リサーチ",
        description="LLM/PoC 調査結果を示すタグ。",
        color="#42A5F5",
    ),
    TagSeed(
        key="qa",
        name="QA",
        description="動作確認や検証フィードバック。",
        color="#FFCA28",
    ),
    TagSeed(
        key="ops",
        name="運用",
        description="監視や運用改善で利用。",
        color="#8D6E63",
    ),
)

PROJECT_SEEDS: tuple[ProjectSeed, ...] = (
    ProjectSeed(
        key="desktop_revamp",
        title="デスクトップUI刷新",
        description="Flet UI のリファイン、レイアウトとテーマを整理する。",
        status=ProjectStatus.ACTIVE,
        due_in_days=21,
    ),
    ProjectSeed(
        key="agent_tooling",
        title="LLMエージェント統合",
        description="Memo→Task 自動変換やプロンプト整備を段階的に導入。",
        status=ProjectStatus.ON_HOLD,
        due_in_days=45,
    ),
    ProjectSeed(
        key="data_pipeline",
        title="データ同期パイプライン安定化",
        description="デスクトップ/CLI/モバイル間のイベント同期をチューニング。",
        status=ProjectStatus.COMPLETED,
        due_in_days=-7,
    ),
    ProjectSeed(
        key="ops_cleanup",
        title="運用ガバナンス改善",
        description="告知テンプレートと監視体制の改善案を統合予定だった計画。",
        status=ProjectStatus.CANCELLED,
        due_in_days=None,
    ),
)

MEMO_SEEDS: tuple[MemoSeed, ...] = (
    MemoSeed(
        key="ux_feedback",
        title="UXレビュー: カード密度",
        content="カードとタブ周りの余白を 8px 単位に合わせる。",
        status=MemoStatus.INBOX,
    ),
    MemoSeed(
        key="llm_prompt",
        title="LLM プロンプト再構築",
        content="モデル切替時に必要な設定値を環境変数に寄せる。",
        status=MemoStatus.ACTIVE,
    ),
    MemoSeed(
        key="automation_notes",
        title="自動化まわりの課題",
        content="poethepoet の新しいジョブ DAG の案。失敗時のリトライを加えたい。",
        status=MemoStatus.IDEA,
    ),
    MemoSeed(
        key="retro_notes",
        title="直近リリースのふりかえり",
        content="alert 連携に時間がかかった原因はモック不足。次回は contract test を追加。",
        status=MemoStatus.ARCHIVE,
    ),
    MemoSeed(
        key="quick_fixes",
        title="QAからのクイック修正依頼",
        content="ショートカットキー案内の更新とトグルアニメーション glitch。",
        status=MemoStatus.INBOX,
    ),
    MemoSeed(
        key="ops_watch",
        title="監視項目アップデート",
        content="リリース後 30 分のトラッキングに集中したい。ログ粒度を揃える。",
        status=MemoStatus.ACTIVE,
    ),
    MemoSeed(
        key="draft_story",
        title="ストーリーボード草案",
        content="Home > Task > Memo の回遊を 3 枚で説明する。",
        status=MemoStatus.IDEA,
    ),
    MemoSeed(
        key="user_research",
        title="ヒアリング要点: タスク一覧",
        content="今日やるべきタスクカードと進捗タスクを一目で見たい。",
        status=MemoStatus.ACTIVE,
    ),
    MemoSeed(
        key="weekly_support_inbox",
        title="週次レビュー: サポート依頼の整理",
        content="サポート部門から届いた定性フィードバック。次週の優先度づけが必要。",
        status=MemoStatus.INBOX,
    ),
    MemoSeed(
        key="weekly_focus_brain_dump",
        title="フォーカスブロック候補のメモ",
        content="集中セッションで片づけたい細かな改善アイデアをラフに列挙。",
        status=MemoStatus.IDEA,
    ),
)

TASK_SEEDS: tuple[TaskSeed, ...] = (
    TaskSeed(
        key="dashboard_cards",
        title="ホームカードのレイアウト調整",
        description="グリッド間隔とテーマ色を UI ガイドラインに合わせる。",
        status=TaskStatus.TODO,
        project_key="desktop_revamp",
        memo_key="ux_feedback",
        due_in_days=3,
    ),
    TaskSeed(
        key="today_sync",
        title="Today セクションの残タスク表示",
        description="今日締切のタスクのみを集計し KPI を表示する。",
        status=TaskStatus.TODAYS,
        project_key="desktop_revamp",
        memo_key="user_research",
        due_in_days=0,
    ),
    TaskSeed(
        key="command_palette",
        title="コマンドパレットのショートカット表示",
        description="Ctrl+K で呼び出した際に最近アクセスしたビューを優先表示。",
        status=TaskStatus.PROGRESS,
        project_key="desktop_revamp",
        memo_key="ux_feedback",
        due_in_days=5,
        created_offset_days=18,
    ),
    TaskSeed(
        key="automation_cron",
        title="メモ→タスク変換ジョブの夜間実行",
        description="失敗時は Slack Webhook へ通知、再実行ポリシーも設定。",
        status=TaskStatus.WAITING,
        project_key="agent_tooling",
        memo_key="automation_notes",
        due_in_days=14,
        created_offset_days=35,
    ),
    TaskSeed(
        key="overdue_docs",
        title="タスクステータス説明の翻訳仕上げ",
        description="UI copy とドキュメントの表現差異を埋める。",
        status=TaskStatus.OVERDUE,
        project_key="agent_tooling",
        memo_key="user_research",
        due_in_days=-4,
    ),
    TaskSeed(
        key="draft_storyboard",
        title="ストーリーボードのドラフト整理",
        description="3 ページ構成の rough を残す。",
        status=TaskStatus.DRAFT,
        memo_key="draft_story",
    ),
    TaskSeed(
        key="completed_batch",
        title="同期バッチのロールアウト計画",
        description="起動時にステータスが反映されるよう migration を調整する。",
        status=TaskStatus.COMPLETED,
        project_key="data_pipeline",
        memo_key="automation_notes",
        due_in_days=-2,
        completed_offset_days=1,
    ),
    TaskSeed(
        key="canceled_vendor",
        title="旧モニタリング製品の棚卸し",
        description="ライセンス更新を停止し、代替案レビューは中止済み。",
        status=TaskStatus.CANCELED,
        project_key="ops_cleanup",
    ),
    TaskSeed(
        key="qa_matrix",
        title="QA カバレッジマトリクス共有",
        description="優先ビューと主要タスクを表にまとめる。",
        status=TaskStatus.TODO,
        memo_key="quick_fixes",
        due_in_days=7,
        created_offset_days=16,
    ),
    TaskSeed(
        key="idea_spikes",
        title="バッチ DAG の spike",
        description="poethepoet の `graph` コマンドでジョブ依存関係を可視化。",
        status=TaskStatus.TODAYS,
        memo_key="automation_notes",
        due_in_days=1,
    ),
    TaskSeed(
        key="handoff_doc",
        title="LLM エージェントのハンドオフドキュメント",
        description="Prompt 設計と API 利用例を 2 ページで共有。",
        status=TaskStatus.PROGRESS,
        project_key="agent_tooling",
        memo_key="llm_prompt",
        due_in_days=9,
    ),
    TaskSeed(
        key="retro_actions",
        title="リリースふりかえりアクション",
        description="契約テスト導入とログ粒度整備をタスク化する。",
        status=TaskStatus.COMPLETED,
        memo_key="retro_notes",
        due_in_days=-10,
        completed_offset_days=2,
    ),
    TaskSeed(
        key="weekly_playbook",
        title="週次レビューガイドのアップデート",
        description="AI提案のテンプレートとチェックリストを見直して最新化する。",
        status=TaskStatus.COMPLETED,
        project_key="desktop_revamp",
        memo_key="ux_feedback",
        due_in_days=-1,
        completed_offset_days=3,
    ),
    TaskSeed(
        key="ops_dashboard",
        title="運用ダッシュボードの整理",
        description="エラー種別別のトレンドチャートを差し込み。",
        status=TaskStatus.WAITING,
        project_key="ops_cleanup",
        memo_key="ops_watch",
        due_in_days=6,
        created_offset_days=21,
    ),
    TaskSeed(
        key="urgent_patch",
        title="ショートカット案内のホットフィックス",
        description="Cmd/Alt 表記を環境依存で切り替える。",
        status=TaskStatus.OVERDUE,
        memo_key="quick_fixes",
        due_in_days=-1,
    ),
)


TERM_SEEDS: tuple[TermSeed, ...] = (
    TermSeed(
        key="gtd_inbox",
        title="GTD Inbox",
        description="処理前のインプットを保管する受信箱。最初の整理対象としてGuided Inboxで参照。",
        status=TermStatus.APPROVED,
        source_url="https://gettingthingsdone.com/",
    ),
    TermSeed(
        key="focus_block",
        title="フォーカスブロック",
        description="開発者がUI改善や検証に集中する30〜60分の予約枠。Todayビューで共有される。",
        status=TermStatus.DRAFT,
    ),
    TermSeed(
        key="llm_agent_handshake",
        title="LLMエージェントハンドシェイク",
        description="エージェント起動時の初期待ち合わせ。プロンプトやAPI設定を同期する手順。",
        status=TermStatus.APPROVED,
    ),
    TermSeed(
        key="ops_window",
        title="運用ウォッチウィンドウ",
        description="リリース直後30分のモニタリング期間。ops タグに紐づくアクションの優先度が上がる。",
        status=TermStatus.APPROVED,
    ),
    TermSeed(
        key="snapshot_dialog",
        title="スナップショットダイアログ",
        description="ユーザー調査で利用していた簡易モーダル。現在はDeprecated扱いで利用停止予定。",
        status=TermStatus.DEPRECATED,
    ),
)


def _safe_list(getter: Callable[[], list[_T]]) -> list[_T]:
    """NotFoundError を握りつぶしつつリスト取得するヘルパー。

    Args:
        getter: ApplicationService の一覧取得 callable。

    Returns:
        取得できたエンティティのリスト。失敗時は空配列。
    """
    try:
        return getter()
    except NotFoundError:
        return []


def _resolve_reference(mapping: dict[str, uuid.UUID], key: str | None, label: str) -> uuid.UUID | None:
    """キーから ID を引く。

    Args:
        mapping: シードキーと ID の対応辞書。
        key: 解決したいキー。None の場合は参照しない。
        label: ログ出力用のエンティティ名。

    Returns:
        見つかった uuid。未定義なら None。
    """
    if key is None:
        return None

    entity_id = mapping.get(key)
    if entity_id is None:
        logger.warning(f"{label} キー '{key}' はまだ作成されていません。")
    return entity_id


def _calculate_due_date(offset_days: int | None) -> date | None:
    """今日からの相対日数を date に変換する。

    Args:
        offset_days: 今日からの差分日数。None の場合は未設定。

    Returns:
        date オブジェクトまたは None。
    """
    if offset_days is None:
        return None
    return datetime.now().date() + timedelta(days=offset_days)


def _calculate_completed_at(offset_days: int | None) -> datetime | None:
    """完了日時を現在からのオフセットで作成する。

    Args:
        offset_days: 現在から遡る日数。None の場合は未設定。

    Returns:
        datetime オブジェクトまたは None。
    """
    if offset_days is None:
        return None
    return datetime.now() - timedelta(days=offset_days)


def _apply_task_created_offsets(apps: ApplicationServices, offset_mapping: dict["uuid.UUID", int]) -> None:
    """Task.created_at を過去日にずらして停滞タスクを用意する。

    Args:
        apps: ApplicationServices ファサード。
        offset_mapping: タスクIDと過去に遡る日数の対応。
    """
    valid_offsets = {task_id: days for task_id, days in offset_mapping.items() if days > 0}
    if not valid_offsets:
        return

    updated_count = 0
    for task_id, days in valid_offsets.items():
        task = apps.task.get_task(task_id)
        if task is None:
            logger.warning(f"created_at を更新できませんでした: task_id={task_id}")
            continue
        target_created_at = datetime.now() - timedelta(days=days)
        update_data = TaskUpdate(
            created_at=target_created_at,
            updated_at=target_created_at if task.updated_at is None or task.updated_at < target_created_at else task.updated_at,
        )
        apps.task.update(task_id, update_data)
        updated_count += 1
    logger.info("停滞タスク用の created_at を {} 件更新しました。", updated_count)


def seed_tags(apps: ApplicationServices) -> dict[str, uuid.UUID]:
    """タグを作成/更新して ID マップを返す。

    Args:
        apps: ApplicationServices ファサード。

    Returns:
        key を uuid に解決するマッピング。
    """
    existing = {tag.name: tag for tag in _safe_list(apps.tag.get_all_tags)}
    results: dict[str, uuid.UUID] = {}

    for seed in TAG_SEEDS:
        tag = existing.get(seed.name)
        if tag is None:
            tag = apps.tag.create(name=seed.name, description=seed.description, color=seed.color)
            logger.info(f"[TAG] 作成: {seed.name}")
        else:
            tag = apps.tag.update(
                tag.id,
                TagUpdate(name=seed.name, description=seed.description, color=seed.color),
            )
            logger.info(f"[TAG] 更新: {seed.name}")
        results[seed.key] = tag.id
    return results


def seed_projects(apps: ApplicationServices) -> dict[str, uuid.UUID]:
    """プロジェクトを作成/更新して ID マップを返す。

    Args:
        apps: ApplicationServices ファサード。

    Returns:
        key を uuid に解決するマッピング。
    """
    existing = {project.title: project for project in _safe_list(apps.project.get_all_projects)}
    results: dict[str, uuid.UUID] = {}

    for seed in PROJECT_SEEDS:
        project = existing.get(seed.title)
        due_date = _calculate_due_date(seed.due_in_days)
        if project is None:
            project = apps.project.create(
                title=seed.title,
                description=seed.description,
                status=seed.status,
            )
            logger.info(f"[PROJECT] 作成: {seed.title}")
        else:
            logger.info(f"[PROJECT] 更新: {seed.title}")
            project = apps.project.update(
                project.id,
                ProjectUpdate(
                    title=seed.title,
                    description=seed.description,
                    status=seed.status,
                    due_date=due_date,
                ),
            )
        results[seed.key] = project.id
    return results


def seed_memos(apps: ApplicationServices) -> dict[str, uuid.UUID]:
    """メモを作成/更新して ID マップを返す。

    Args:
        apps: ApplicationServices ファサード。

    Returns:
        key を uuid に解決するマッピング。
    """
    existing = {memo.title: memo for memo in _safe_list(apps.memo.get_all_memos)}
    results: dict[str, uuid.UUID] = {}

    for seed in MEMO_SEEDS:
        memo = existing.get(seed.title)
        if memo is None:
            memo = apps.memo.create(title=seed.title, content=seed.content, status=seed.status)
            logger.info(f"[MEMO] 作成: {seed.title}")
        else:
            logger.info(f"[MEMO] 更新: {seed.title}")
            memo = apps.memo.update(
                memo.id,
                MemoUpdate(title=seed.title, content=seed.content, status=seed.status),
            )
        results[seed.key] = memo.id
    return results


def seed_tasks(
    apps: ApplicationServices,
    project_ids: dict[str, uuid.UUID],
    memo_ids: dict[str, uuid.UUID],
) -> dict[str, uuid.UUID]:
    """タスクを作成/更新し、参照されたプロジェクトとメモに紐づける。

    Args:
        apps: ApplicationServices ファサード。
        project_ids: プロジェクトキーと uuid の対応。
        memo_ids: メモキーと uuid の対応。

    Returns:
        タスクキーを uuid に解決するマッピング。
    """
    existing = {task.title: task for task in _safe_list(apps.task.get_all_tasks)}
    results: dict[str, uuid.UUID] = {}
    created_offsets: dict[uuid.UUID, int] = {}

    for seed in TASK_SEEDS:
        task = existing.get(seed.title)
        due_date = _calculate_due_date(seed.due_in_days)
        completed_at = _calculate_completed_at(seed.completed_offset_days)
        project_id = _resolve_reference(project_ids, seed.project_key, "プロジェクト")
        memo_id = _resolve_reference(memo_ids, seed.memo_key, "メモ")

        if task is None:
            task = apps.task.create(
                title=seed.title,
                description=seed.description,
                status=seed.status,
                due_date=due_date,
                completed_at=completed_at,
                project_id=project_id,
                memo_id=memo_id,
            )
            logger.info(f"[TASK] 作成: {seed.title}")
        else:
            update_payload = TaskUpdate(
                title=seed.title,
                description=seed.description,
                status=seed.status,
                due_date=due_date,
                completed_at=completed_at,
                project_id=project_id,
                memo_id=memo_id,
            )
            task = apps.task.update(task.id, update_payload)
            logger.info(f"[TASK] 更新: {seed.title}")

        if seed.created_offset_days:
            created_offsets[task.id] = seed.created_offset_days
        results[seed.key] = task.id

    _apply_task_created_offsets(created_offsets)
    return results


def seed_terms(apps: ApplicationServices) -> dict[str, uuid.UUID]:
    """社内用語を作成/更新して ID マップを返す。

    Args:
        apps: ApplicationServices ファサード。

    Returns:
        key を uuid に解決するマッピング。
    """
    existing = {term.key: term for term in _safe_list(apps.terminology.get_all)}
    results: dict[str, uuid.UUID] = {}

    for seed in TERM_SEEDS:
        term = existing.get(seed.key)
        if term is None:
            term = apps.terminology.create(
                key=seed.key,
                title=seed.title,
                description=seed.description,
                status=seed.status,
                source_url=seed.source_url,
            )
            logger.info(f"[TERM] 作成: {seed.title}")
        else:
            term = apps.terminology.update(
                term.id,
                TermUpdate(
                    key=seed.key,
                    title=seed.title,
                    description=seed.description,
                    status=seed.status,
                    source_url=seed.source_url,
                ),
            )
            logger.info(f"[TERM] 更新: {seed.title}")
        results[seed.key] = term.id
    return results


def main() -> None:
    """サンプルデータ投入を実行する。"""
    from logging_conf import setup_logger

    setup_logger()
    logger.info("サンプルデータ投入を開始します。")
    apps = ApplicationServices.create()

    tag_ids = seed_tags(apps)
    project_ids = seed_projects(apps)
    memo_ids = seed_memos(apps)
    task_ids = seed_tasks(apps, project_ids, memo_ids)
    term_ids = seed_terms(apps)

    logger.info(
        "投入完了 Tags={} Projects={} Memos={} Tasks={} Terms={}",
        len(tag_ids),
        len(project_ids),
        len(memo_ids),
        len(task_ids),
        len(term_ids),
    )


if __name__ == "__main__":  # pragma: no cover
    main()
