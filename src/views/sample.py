"""Sample data and utilities for views_new components.

このモジュールは、views_newアーキテクチャの各ビューで使用する
サンプルデータとユーティリティ関数を提供します。
開発・テスト・デモ用途で使用してください。
"""

import uuid
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from enum import Enum
from typing import Any


class SampleTermStatus(str, Enum):
    """用語のステータス（サンプル用）"""

    DRAFT = "draft"
    APPROVED = "approved"
    DEPRECATED = "deprecated"


class SampleMemoStatus(str, Enum):
    """メモのステータス（サンプル用）"""

    INBOX = "inbox"
    ACTIVE = "active"
    IDEA = "idea"
    ARCHIVE = "archive"


class SampleTaskStatus(str, Enum):
    """タスクのステータス（サンプル用）"""

    TODO = "todo"
    TODAYS = "todays"
    PROGRESS = "progress"
    WAITING = "waiting"
    COMPLETED = "completed"
    CANCELED = "canceled"
    OVERDUE = "overdue"


class SampleProjectStatus(str, Enum):
    """プロジェクトのステータス（サンプル用）"""

    ACTIVE = "active"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


@dataclass
class SampleTerm:
    """用語のサンプルデータクラス"""

    id: uuid.UUID = field(default_factory=uuid.uuid4)
    key: str = ""
    title: str = ""
    description: str = ""
    status: SampleTermStatus = SampleTermStatus.DRAFT
    source_url: str | None = None
    synonyms: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class SampleMemo:
    """メモのサンプルデータクラス"""

    id: uuid.UUID = field(default_factory=uuid.uuid4)
    title: str = ""
    content: str = ""
    status: SampleMemoStatus = SampleMemoStatus.INBOX
    tags: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    processed_at: datetime | None = None


@dataclass
class SampleTask:
    """タスクのサンプルデータクラス"""

    id: uuid.UUID = field(default_factory=uuid.uuid4)
    title: str = ""
    description: str = ""
    status: SampleTaskStatus = SampleTaskStatus.TODO
    priority: str = "medium"  # high, medium, low
    due_date: date | None = None
    completed_at: datetime | None = None
    project_id: uuid.UUID | None = None
    memo_id: uuid.UUID | None = None
    tags: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class SampleProject:
    """プロジェクトのサンプルデータクラス"""

    id: uuid.UUID = field(default_factory=uuid.uuid4)
    title: str = ""
    description: str = ""
    status: SampleProjectStatus = SampleProjectStatus.ACTIVE
    due_date: date | None = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class SampleTag:
    """タグのサンプルデータクラス"""

    id: uuid.UUID = field(default_factory=uuid.uuid4)
    name: str = ""
    description: str = ""
    color: str = "#2196F3"
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


class SampleDataProvider:
    """サンプルデータの提供クラス"""

    @staticmethod
    def create_sample_terms() -> list[SampleTerm]:
        """用語のサンプルデータを作成"""
        return [
            SampleTerm(
                key="GTD",
                title="Getting Things Done",
                description=(
                    "デビッド・アレン氏が考案した個人の生産性向上システム。"
                    "すべてのタスクや気になることを外部のシステムに記録し、"
                    "定期的にレビューすることで、心の平穏と生産性の向上を図る手法です。"
                ),
                status=SampleTermStatus.APPROVED,
                source_url="https://gettingthingsdone.com/",
                synonyms=["ジーティーディー", "GTDメソッド", "Getting Things Done手法"],
                tags=["生産性", "タスク管理", "ライフハック"],
            ),
            SampleTerm(
                key="API",
                title="Application Programming Interface",
                description=(
                    "アプリケーション同士が情報をやり取りするためのインターフェース。"
                    "ソフトウェアの機能を外部から利用できるように公開された仕様や手順のことです。"
                ),
                status=SampleTermStatus.APPROVED,
                synonyms=["エーピーアイ", "アプリケーションプログラミングインターフェース"],
                tags=["技術", "プログラミング", "システム連携"],
            ),
            SampleTerm(
                key="CI_CD",
                title="Continuous Integration / Continuous Deployment",
                description=(
                    "継続的インテグレーション・継続的デプロイメント。"
                    "コードの変更を自動的にテスト・ビルド・デプロイする開発手法で、"
                    "品質向上と開発速度の向上を実現します。"
                ),
                status=SampleTermStatus.DRAFT,
                synonyms=["シーアイシーディー", "継続的インテグレーション", "継続的デプロイメント"],
                tags=["技術", "開発手法", "自動化"],
            ),
            SampleTerm(
                key="MVP",
                title="Minimum Viable Product",
                description=(
                    "最小限の機能を持つ製品。"
                    "最小限のコストで最大限の学習効果を得るために作られる初期バージョンの製品です。"
                ),
                status=SampleTermStatus.APPROVED,
                synonyms=["エムブイピー", "最小限の実用可能製品"],
                tags=["プロダクト開発", "リーンスタートアップ", "ビジネス"],
            ),
            SampleTerm(
                key="LEGACY_TERM",
                title="レガシーなシステム",
                description="古い技術で作られたシステム。保守が困難で更新が必要。",
                status=SampleTermStatus.DEPRECATED,
                synonyms=["古いシステム", "旧システム"],
                tags=["システム", "技術債務"],
            ),
        ]

    @staticmethod
    def create_sample_memos() -> list[SampleMemo]:
        """メモのサンプルデータを作成"""
        base_time = datetime.now()
        return [
            SampleMemo(
                title="会議で出たアイデア",
                content="新機能の提案について話し合った。UIの改善とパフォーマンス最適化が必要。",
                status=SampleMemoStatus.INBOX,
                tags=["会議", "アイデア", "UI"],
                created_at=base_time - timedelta(hours=2),
            ),
            SampleMemo(
                title="技術記事メモ",
                content="Fletフレームワークの新機能について調査。Material Design 3対応が進んでいる。",
                status=SampleMemoStatus.ACTIVE,
                tags=["技術", "調査", "Flet"],
                created_at=base_time - timedelta(days=1),
                processed_at=base_time - timedelta(hours=12),
            ),
            SampleMemo(
                title="読書メモ",
                content="「Clean Code」から学んだポイント。関数は小さく、単一責任にする。",
                status=SampleMemoStatus.IDEA,
                tags=["読書", "プログラミング", "学習"],
                created_at=base_time - timedelta(days=3),
                processed_at=base_time - timedelta(days=2),
            ),
            SampleMemo(
                title="完了したタスクの振り返り",
                content="プロジェクトX完了。学んだことと改善点をまとめる。",
                status=SampleMemoStatus.ARCHIVE,
                tags=["振り返り", "プロジェクト"],
                created_at=base_time - timedelta(days=7),
                processed_at=base_time - timedelta(days=5),
            ),
        ]

    @staticmethod
    def create_sample_tasks() -> list[SampleTask]:
        """タスクのサンプルデータを作成"""
        base_time = datetime.now()
        today = datetime.now().date()
        return [
            SampleTask(
                title="TermsView バグ修正",
                description="SQLAlchemyエラーの修正とサンプルデータの実装",
                status=SampleTaskStatus.PROGRESS,
                priority="high",
                due_date=today,
                tags=["バグ修正", "開発", "緊急"],
            ),
            SampleTask(
                title="UIコンポーネントの色修正",
                description="SURFACE_VARIANTをSECONDARY_CONTAINERに置換",
                status=SampleTaskStatus.COMPLETED,
                priority="medium",
                due_date=today - timedelta(days=1),
                completed_at=base_time - timedelta(hours=3),
                tags=["UI", "修正"],
            ),
            SampleTask(
                title="ドキュメント更新",
                description="views_newアーキテクチャの説明書を作成",
                status=SampleTaskStatus.TODO,
                priority="low",
                due_date=today + timedelta(days=3),
                tags=["ドキュメント", "説明書"],
            ),
            SampleTask(
                title="週次レビュー準備",
                description="今週の成果とKPIをまとめる",
                status=SampleTaskStatus.TODAYS,
                priority="medium",
                due_date=today,
                tags=["レビュー", "KPI"],
            ),
            SampleTask(
                title="テストコード追加",
                description="新機能のユニットテストを書く",
                status=SampleTaskStatus.WAITING,
                priority="medium",
                due_date=today + timedelta(days=2),
                tags=["テスト", "品質保証"],
            ),
        ]

    @staticmethod
    def create_sample_projects() -> list[SampleProject]:
        """プロジェクトのサンプルデータを作成"""
        today = datetime.now().date()
        return [
            SampleProject(
                title="Kageアプリケーション開発",
                description="LLMを活用したタスク管理アプリケーションの開発プロジェクト",
                status=SampleProjectStatus.ACTIVE,
                due_date=today + timedelta(days=30),
            ),
            SampleProject(
                title="UI/UX改善プロジェクト",
                description="ユーザビリティ向上のための画面設計見直し",
                status=SampleProjectStatus.ACTIVE,
                due_date=today + timedelta(days=14),
            ),
            SampleProject(
                title="パフォーマンス最適化",
                description="アプリケーション全体の動作速度改善",
                status=SampleProjectStatus.ON_HOLD,
                due_date=today + timedelta(days=45),
            ),
            SampleProject(
                title="バージョン1.0リリース",
                description="最初の安定版リリースに向けた準備",
                status=SampleProjectStatus.COMPLETED,
                due_date=today - timedelta(days=5),
            ),
        ]

    @staticmethod
    def create_sample_tags() -> list[SampleTag]:
        """タグのサンプルデータを作成"""
        return [
            SampleTag(name="開発", description="開発関連のタスク", color="#2196F3"),
            SampleTag(name="バグ修正", description="バグの修正作業", color="#F44336"),
            SampleTag(name="UI", description="ユーザーインターフェース", color="#9C27B0"),
            SampleTag(name="技術", description="技術的な内容", color="#4CAF50"),
            SampleTag(name="会議", description="会議関連", color="#FF9800"),
            SampleTag(name="学習", description="学習・調査", color="#795548"),
            SampleTag(name="ドキュメント", description="文書作成", color="#607D8B"),
            SampleTag(name="テスト", description="テスト関連", color="#009688"),
            SampleTag(name="緊急", description="緊急対応が必要", color="#E91E63"),
            SampleTag(name="アイデア", description="新しいアイデア", color="#FFEB3B"),
        ]

    @staticmethod
    def get_sample_statistics() -> dict[str, Any]:
        """サンプル統計データを取得"""
        return {
            "total_tasks": 12,
            "completed_tasks": 8,
            "active_tasks": 4,
            "total_projects": 4,
            "active_projects": 2,
            "pending_memos": 3,
            "total_terms": 5,
            "approved_terms": 3,
            "draft_terms": 1,
            "deprecated_terms": 1,
        }

    @staticmethod
    def get_sample_weekly_data() -> dict[str, Any]:
        """週次レビュー用のサンプルデータを取得"""
        return {
            "tasks_completed": 8,
            "tasks_created": 5,
            "productivity_score": 85,
            "focus_time_hours": 32,
            "meeting_hours": 8,
            "completion_rate": 0.73,
            "goal_achievement": 0.80,
            "weekly_goals": [
                "TermsViewの実装完了",
                "UIバグ修正",
                "ドキュメント整備",
            ],
            "achievements": [
                "アプリケーション基本機能完成",
                "ルーティングシステム構築",
                "コンポーネント設計完了",
            ],
            "challenges": [
                "SQLAlchemyモデル連携",
                "Flet非推奨API対応",
                "パフォーマンス最適化",
            ],
            "next_week_focus": [
                "データベース連携強化",
                "エラーハンドリング改善",
                "ユーザビリティ向上",
            ],
        }

    @staticmethod
    def generate_daily_review() -> dict[str, Any]:
        """デイリーレビューメッセージとアクションを生成"""
        tasks = SampleDataProvider.create_sample_tasks()
        memos = SampleDataProvider.create_sample_memos()

        # タスクの状況分析
        todays_tasks = [t for t in tasks if t.status == SampleTaskStatus.TODAYS]
        todo_tasks = [t for t in tasks if t.status == SampleTaskStatus.TODO]
        progress_tasks = [t for t in tasks if t.status == SampleTaskStatus.PROGRESS]
        overdue_tasks = [t for t in tasks if t.status == SampleTaskStatus.OVERDUE]
        completed_tasks = [t for t in tasks if t.status == SampleTaskStatus.COMPLETED]

        # メモの状況分析
        inbox_memos = [m for m in memos if m.status == SampleMemoStatus.INBOX]

        # 状況別メッセージの辞書
        review_scenarios = [
            {
                "condition": bool(overdue_tasks),
                "data": {
                    "icon": "error",
                    "color": "amber",
                    "message": f"{len(overdue_tasks)}件の期限超過タスクがあります。優先的に対処しましょう。",
                    "action_text": "期限超過のタスクを確認",
                    "action_route": "/tasks",
                    "priority": "high",
                },
            },
            {
                "condition": not todays_tasks and bool(todo_tasks),
                "data": {
                    "icon": "coffee",
                    "color": "blue",
                    "message": (
                        f"今日のタスクがまだ設定されていません。{len(todo_tasks)}件のTODOから選んで始めましょう！"
                    ),
                    "action_text": "タスクを設定する",
                    "action_route": "/tasks",
                    "priority": "medium",
                },
            },
            {
                "condition": bool(todays_tasks) and not progress_tasks,
                "data": {
                    "icon": "play_arrow",
                    "color": "green",
                    "message": (f"{len(todays_tasks)}件のタスクが待っています。さあ、最初の一歩を踏み出しましょう！"),
                    "action_text": "タスクを開始する",
                    "action_route": "/tasks",
                    "priority": "medium",
                },
            },
            {
                "condition": bool(progress_tasks),
                "data": {
                    "icon": "trending_up",
                    "color": "primary",
                    "message": (
                        f"{len(progress_tasks)}件のタスクが進行中です。良いペースです、その調子で続けましょう！"
                    ),
                    "action_text": "進行中のタスクを見る",
                    "action_route": "/tasks",
                    "priority": "normal",
                },
            },
            {
                "condition": bool(inbox_memos),
                "data": {
                    "icon": "lightbulb",
                    "color": "purple",
                    "message": (f"{len(inbox_memos)}件のInboxメモがあります。AIにタスクを生成させて整理しましょう。"),
                    "action_text": "メモを整理する",
                    "action_route": "/memos",
                    "priority": "medium",
                },
            },
            {
                "condition": bool(completed_tasks) and not todays_tasks,
                "data": {
                    "icon": "check_circle",
                    "color": "green",
                    "message": (
                        "素晴らしい！全てのタスクが完了しています。新しいメモを書いて次の目標を設定しましょう。"
                    ),
                    "action_text": "新しいメモを作成",
                    "action_route": "/memos",
                    "priority": "low",
                },
            },
        ]

        # 条件に合致する最初のシナリオを選択
        for scenario in review_scenarios:
            if scenario["condition"]:
                return scenario["data"]

        # デフォルトメッセージ
        return {
            "icon": "wb_sunny",
            "color": "primary",
            "message": ("今日も良い一日にしましょう。まずはメモを書いて、やるべきことを整理しませんか？"),
            "action_text": "メモを作成する",
            "action_route": "/memos",
            "priority": "low",
        }


# Utility functions for easy access
def get_sample_terms() -> list[SampleTerm]:
    """用語サンプルデータの簡単なアクセス関数"""
    return SampleDataProvider.create_sample_terms()


def get_sample_memos() -> list[SampleMemo]:
    """メモサンプルデータの簡単なアクセス関数"""
    return SampleDataProvider.create_sample_memos()


def get_sample_tasks() -> list[SampleTask]:
    """タスクサンプルデータの簡単なアクセス関数"""
    return SampleDataProvider.create_sample_tasks()


def get_sample_projects() -> list[SampleProject]:
    """プロジェクトサンプルデータの簡単なアクセス関数"""
    return SampleDataProvider.create_sample_projects()


def get_sample_tags() -> list[SampleTag]:
    """タグサンプルデータの簡単なアクセス関数"""
    return SampleDataProvider.create_sample_tags()


def get_sample_statistics() -> dict[str, Any]:
    """統計サンプルデータの簡単なアクセス関数"""
    return SampleDataProvider.get_sample_statistics()


def get_sample_weekly_data() -> dict[str, Any]:
    """週次データサンプルの簡単なアクセス関数"""
    return SampleDataProvider.get_sample_weekly_data()


def get_daily_review() -> dict[str, Any]:
    """デイリーレビューデータの簡単なアクセス関数"""
    return SampleDataProvider.generate_daily_review()


# Mock database operations for demo purposes
class MockTermService:
    """用語サービスのモック実装"""

    @staticmethod
    def get_all_terms() -> list[SampleTerm]:
        """全ての用語を取得"""
        return get_sample_terms()

    @staticmethod
    def get_terms_by_status(status: SampleTermStatus) -> list[SampleTerm]:
        """ステータス別に用語を取得"""
        all_terms = get_sample_terms()
        return [term for term in all_terms if term.status == status]

    @staticmethod
    def search_terms(query: str) -> list[SampleTerm]:
        """用語を検索"""
        all_terms = get_sample_terms()
        query_lower = query.lower()
        return [
            term
            for term in all_terms
            if (
                query_lower in term.title.lower()
                or query_lower in term.key.lower()
                or query_lower in term.description.lower()
                or any(query_lower in synonym.lower() for synonym in term.synonyms)
            )
        ]


class MockMemoService:
    """メモサービスのモック実装"""

    @staticmethod
    def get_all_memos() -> list[SampleMemo]:
        """全てのメモを取得"""
        return get_sample_memos()

    @staticmethod
    def get_memos_by_status(status: SampleMemoStatus) -> list[SampleMemo]:
        """ステータス別にメモを取得"""
        all_memos = get_sample_memos()
        return [memo for memo in all_memos if memo.status == status]


class MockTaskService:
    """タスクサービスのモック実装"""

    @staticmethod
    def get_all_tasks() -> list[SampleTask]:
        """全てのタスクを取得"""
        return get_sample_tasks()

    @staticmethod
    def get_tasks_by_status(status: SampleTaskStatus) -> list[SampleTask]:
        """ステータス別にタスクを取得"""
        all_tasks = get_sample_tasks()
        return [task for task in all_tasks if task.status == status]


class MockProjectService:
    """プロジェクトサービスのモック実装"""

    @staticmethod
    def get_all_projects() -> list[SampleProject]:
        """全てのプロジェクトを取得"""
        return get_sample_projects()

    @staticmethod
    def get_projects_by_status(status: SampleProjectStatus) -> list[SampleProject]:
        """ステータス別にプロジェクトを取得"""
        all_projects = get_sample_projects()
        return [project for project in all_projects if project.status == status]

    @staticmethod
    def get_project_tasks(project_id: uuid.UUID) -> list[SampleTask]:
        """プロジェクトに関連するタスクを取得"""
        all_tasks = get_sample_tasks()
        return [task for task in all_tasks if task.project_id == project_id]

    @staticmethod
    def calculate_project_progress(project_id: uuid.UUID) -> dict[str, int]:
        """プロジェクトの進捗を計算"""
        project_tasks = MockProjectService.get_project_tasks(project_id)
        total_tasks = len(project_tasks)
        completed_tasks = len([task for task in project_tasks if task.status == SampleTaskStatus.COMPLETED])

        return {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "progress_percentage": int(completed_tasks / total_tasks * 100) if total_tasks > 0 else 0,
        }


def get_projects_for_ui() -> list[dict[str, str]]:
    """UI表示用のプロジェクトデータを辞書形式で取得

    既存のSampleProjectデータクラスをUI表示用の辞書形式に変換する。
    実際の実装では、Repository/ApplicationServiceを通じてデータを取得すべき。

    Returns:
        UI表示用のプロジェクトデータのリスト
    """
    projects = get_sample_projects()
    project_dicts = []

    # ステータスマッピング（英語→日本語）
    status_mapping = {
        SampleProjectStatus.ACTIVE: "進行中",
        SampleProjectStatus.ON_HOLD: "保留",
        SampleProjectStatus.COMPLETED: "完了",
        SampleProjectStatus.CANCELLED: "キャンセル",
    }

    for project in projects:
        # プロジェクトに関する進捗を計算
        progress_data = MockProjectService.calculate_project_progress(project.id)

        project_dict = {
            "id": str(project.id),
            "name": project.title,
            "description": project.description,
            "status": status_mapping.get(project.status, "不明"),
            "tasks_count": str(progress_data["total_tasks"]),
            "completed_tasks": str(progress_data["completed_tasks"]),
            "created_at": project.created_at.strftime("%Y-%m-%d"),
            "start_date": project.created_at.strftime("%Y-%m-%d"),  # サンプルでは作成日を開始日として使用
            "end_date": project.due_date.strftime("%Y-%m-%d") if project.due_date else "",
            "priority": "normal",  # サンプルデータでは標準優先度
        }
        project_dicts.append(project_dict)

    return project_dicts


def get_enhanced_projects_sample_data() -> list[dict[str, str]]:
    """拡張されたプロジェクトサンプルデータを取得

    現在のUI実装に合わせて、より詳細なサンプルデータを提供する。
    実際の実装では削除し、上記のget_projects_for_ui()を使用すべき。

    Returns:
        拡張されたプロジェクトサンプルデータ
    """
    return [
        {
            "id": "1",
            "name": "ウェブサイトリニューアル",
            "description": "会社ウェブサイトの全面リニューアルプロジェクト。モダンなデザインとレスポンシブ対応を実装。",
            "status": "進行中",
            "tasks_count": "12",
            "completed_tasks": "8",
            "created_at": "2024-01-15",
            "start_date": "2024-01-15",
            "end_date": "2024-03-15",
            "priority": "high",
        },
        {
            "id": "2",
            "name": "モバイルアプリ開発",
            "description": "iOS/Android向けの新しいモバイルアプリケーション。React Nativeを使用した開発。",
            "status": "進行中",
            "tasks_count": "8",
            "completed_tasks": "3",
            "created_at": "2024-02-01",
            "start_date": "2024-02-01",
            "end_date": "2024-05-01",
            "priority": "high",
        },
        {
            "id": "3",
            "name": "データベース最適化",
            "description": "既存システムのパフォーマンス改善とクエリ最適化。インデックス追加とスロークエリ対応。",
            "status": "完了",
            "tasks_count": "5",
            "completed_tasks": "5",
            "created_at": "2024-01-01",
            "start_date": "2024-01-01",
            "end_date": "2024-01-31",
            "priority": "medium",
        },
        {
            "id": "4",
            "name": "APIドキュメント作成",
            "description": "開発者向けAPIドキュメントの整備。OpenAPI仕様書とサンプルコードの作成。",
            "status": "保留",
            "tasks_count": "4",
            "completed_tasks": "1",
            "created_at": "2024-01-20",
            "start_date": "2024-01-20",
            "end_date": "2024-04-20",
            "priority": "low",
        },
        {
            "id": "5",
            "name": "レガシーシステム移行",
            "description": "旧システムから新システムへの移行プロジェクト。データ移行とシステム統合。",
            "status": "キャンセル",
            "tasks_count": "15",
            "completed_tasks": "2",
            "created_at": "2024-01-05",
            "start_date": "2024-01-05",
            "end_date": "2024-06-30",
            "priority": "medium",
        },
    ]
