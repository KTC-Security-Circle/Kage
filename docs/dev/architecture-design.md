# アーキテクチャ設計ガイド - クリーンアーキテクチャと GTD 基盤

## はじめに

このドキュメントでは、Kage アプリケーションで採用している**クリーンアーキテクチャ**に基づく設計思想について、Python 初学者向けに分かりやすく説明します。本プロジェクトは、GTD（Getting Things Done）手法をベースとしたタスク管理システムとして、保守性・拡張性・テスタビリティを重視した設計になっています。

## プロジェクト概要

### 技術スタック（2025 年 8 月現在）

- **UI フレームワーク**: Flet 0.27.6
- **ORM**: SQLModel 0.0.24
- **AI/Agent**: LangChain 0.3.26 + LangGraph 0.4.9
- **パッケージ管理**: uv 0.7.3
- **開発ツール**: Ruff, Pyright, pytest
- **データベース**: SQLite（Alembic 対応）

### GTD 基盤の実装

Kage は以下の GTD 核心概念を実装しています：

- **Inbox**: すべてのタスクの受け皿
- **Next Action**: 次に取る具体的なアクション
- **Waiting For**: 他者の対応待ち項目
- **Someday/Maybe**: いつかやるかもしれない項目
- **Projects**: 複数のアクションを伴う成果
- **Delegated**: 委譲されたタスク

## なぜアーキテクチャが重要なのか？

### 悪い例：すべてを一つのファイルに書く場合

```python
# ❌ 悪い例：すべてが混在している
import flet as ft
from sqlmodel import Session, create_engine, SQLModel, Field
import uuid
from datetime import datetime

# データベース、UI、ビジネスロジックがすべて混在
class Task(SQLModel, table=True):
    id: uuid.UUID = Field(primary_key=True)
    title: str
    completed: bool = False

def main():
    engine = create_engine("sqlite:///tasks.db")

    def on_add_task(e):
        # UIからデータを取得
        title = title_field.value

        # バリデーション（ビジネスロジック）
        if not title:
            show_error("タイトルを入力してください")
            return

        if len(title) > 100:
            show_error("タイトルは100文字以内で入力してください")
            return

        # データベースに直接保存（データアクセス）
        with Session(engine) as session:
            task = Task(id=uuid.uuid4(), title=title)
            session.add(task)
            session.commit()

        # UIを更新（プレゼンテーション）
        refresh_task_list()

    # UIコンポーネント作成
    title_field = ft.TextField(label="タスクタイトル")
    # ...
```

この書き方の問題点：

- **単一責任原則違反**: 一つの関数で多くの責任を負っている
- **テストが困難**: データベース、UI、ビジネスロジックが密結合
- **修正時の影響が大きい**: 一箇所の変更が他の部分に波及しやすい
- **コードの再利用ができない**: 特定の UI に依存したロジック
- **拡張が困難**: 新機能追加時に既存コードに大きな影響

### 良い例：クリーンアーキテクチャに基づく責任分離

```python
# ✅ 良い例：責任が明確に分離されている

# models/task.py - データ構造とGTDの実装
from enum import Enum
from sqlmodel import SQLModel, Field
import uuid

class TaskStatus(str, Enum):
    """GTDシステムに基づくタスクステータス"""
    INBOX = "inbox"
    NEXT_ACTION = "next_action"
    WAITING_FOR = "waiting_for"
    SOMEDAY_MAYBE = "someday_maybe"
    DELEGATED = "delegated"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class TaskBase(SQLModel):
    """タスクの基本モデル"""
    title: str = Field(index=True)
    description: str = Field(default="")
    status: TaskStatus = Field(default=TaskStatus.INBOX, index=True)

class TaskCreate(TaskBase):
    """新規作成時に使用（IDは不要）"""
    pass

class TaskRead(TaskBase):
    """読み取り時に使用（IDが必要）"""
    id: uuid.UUID

# logic/services/task_service.py - ビジネスロジック
class TaskService:
    def __init__(self, repository: TaskRepository):
        self.repository = repository

    def create_task(self, command: TaskCreate) -> TaskRead:
        """GTDルールに従ってタスクを作成"""
        if not command.title.strip():
            raise TaskServiceCreateError("タスクのタイトルは必須です")

        return self.repository.create(command)

# logic/application/task_application_service.py - アプリケーションサービス
class TaskApplicationService:
    """View層からSession管理を分離"""

    def create_task(self, command: CreateTaskCommand) -> TaskRead:
        with SqlModelUnitOfWork() as uow:
            service_factory = create_service_factory(uow.session)
            task_service = service_factory.create_task_service()
            return task_service.create_task(command.to_create_model())

# views/tasks/view.py - UI表示
class TaskView(BaseView):
    def __init__(self, page: ft.Page, app_services: ApplicationServices):
        super().__init__(page, app_services)
        self.task_app_service = app_services.task

    def on_add_task(self, e):
        """UIからアプリケーションサービスを呼び出すだけ"""
        try:
            command = CreateTaskCommand(title=self.title_field.value)
            task = self.task_app_service.create_task(command)
            self.refresh_task_list()
        except TaskServiceCreateError as e:
            self.show_error(str(e))
```

## クリーンアーキテクチャとレイヤー構造

本プロジェクトは、ロバート・C・マーティンのクリーンアーキテクチャ原則に基づき、関心事の分離を徹底したレイヤードアーキテクチャを採用しています。

```text
┌─────────────────────────────────┐
│           Views Layer           │ 🎨 UIとユーザーインタラクション
│         (src/views/)            │
└──────────────┬──────────────────┘
               │ Commands/Events
┌──────────────▼──────────────────┐
│       Application Layer         │ 🔄 セッション管理とワークフロー調整
│      (src/logic/application/)   │
└──────────────┬──────────────────┘
               │ Business Logic
┌──────────────▼──────────────────┐
│        Services Layer           │ 🧠 ビジネスルールとGTDロジック
│       (src/logic/services/)     │
└────────┬──────────┬─────────────┘
         │          │
┌────────▼────┐ ┌──▼─────────────┐
│   Models    │ │     Agents     │ 🤖 LLM/AI自動化
│ (src/models)│ │ (src/agents/)  │
└─────────────┘ └────────────────┘
         │
┌────────▼──────────────────┐
│    Infrastructure        │ 💾 データ永続化とリポジトリ
│ (src/logic/repositories/) │
└───────────────────────────┘
```

### 各層の責務

- **Views Layer**: Flet を使用した UI 表示、ユーザー入力処理、Application Service の呼び出し
- **Application Layer**: トランザクション境界管理、複数サービスの調整、セッション管理
- **Services Layer**: GTD ビジネスルール、ドメインロジック、バリデーション
- **Models Layer**: エンティティ定義、データ構造、型安全性
- **Agents Layer**: LangChain/LangGraph による AI 自動化、複雑なタスクの委譲
- **Infrastructure Layer**: データアクセス、リポジトリパターン、外部システム連携

## モデル層（Model Layer）の詳細設計

### 1. GTD ベースのデータ構造定義

モデル層では、GTD 手法に基づいたタスク管理の概念をデータ構造として表現します。

```python
# models/task.py - 実際のプロジェクト実装例
from enum import Enum
from datetime import date
from sqlmodel import Field, SQLModel
import uuid

class TaskStatus(str, Enum):
    """GTDシステムに基づくタスクステータス"""
    INBOX = "inbox"                # 受信箱（未分類）
    NEXT_ACTION = "next_action"    # 次のアクション
    WAITING_FOR = "waiting_for"    # 他者の対応待ち
    SOMEDAY_MAYBE = "someday_maybe" # いつかやるかもしれない
    DELEGATED = "delegated"        # 委譲済み
    COMPLETED = "completed"        # 完了
    CANCELLED = "cancelled"        # キャンセル

class TaskBase(SQLModel):
    """タスクの基本属性を定義"""
    project_id: uuid.UUID | None = Field(default=None, foreign_key="project.id", index=True)
    parent_id: uuid.UUID | None = Field(default=None, foreign_key="task.id", index=True)
    title: str = Field(index=True)  # 検索用インデックス
    description: str = Field(default="")
    status: TaskStatus = Field(default=TaskStatus.INBOX, index=True)  # ステータス検索用
    due_date: date | None = Field(default=None)  # 締切日
```

### 2. CQRS 対応の型安全なモデル設計

Command Query Responsibility Segregation (CQRS) パターンに基づき、用途別にモデルを分離：

```python
# 作成用モデル（IDは不要）
class TaskCreate(TaskBase):
    """新規タスク作成時に使用"""
    pass

# 読み取り用モデル（IDが必要）
class TaskRead(TaskBase):
    """タスク取得・表示時に使用"""
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

# 更新用モデル（変更フィールドのみ）
class TaskUpdate(SQLModel):
    """タスク更新時に使用（部分更新対応）"""
    title: str | None = None
    description: str | None = None
    status: TaskStatus | None = None
    due_date: date | None = None

# データベーステーブル定義
class Task(TaskBase, table=True):
    """実際のデータベーステーブル"""
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
```

### 3. 関連エンティティとの連携

```python
# models/project.py - プロジェクト管理
class Project(SQLModel, table=True):
    """GTDのプロジェクト概念を実装"""
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(index=True)
    description: str = Field(default="")
    status: ProjectStatus = Field(default=ProjectStatus.ACTIVE)

# models/tag.py - タグシステム
class Tag(SQLModel, table=True):
    """コンテキストとタグ管理"""
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(unique=True, index=True)
    color: str = Field(default="#808080")

# models/task_tag.py - 多対多関係
class TaskTag(SQLModel, table=True):
    """タスクとタグの関係テーブル"""
    task_id: uuid.UUID = Field(foreign_key="task.id", primary_key=True)
    tag_id: uuid.UUID = Field(foreign_key="tag.id", primary_key=True)
```

### なぜ複数のモデルを作るのか？

#### 理由 1: 型安全性の確保

```python
# ❌ 悪い例：単一モデルでの曖昧な使用
def create_task(task: Task) -> Task:  # IDが含まれてしまう可能性
    pass

# ✅ 良い例：意図が明確
def create_task(task_data: TaskCreate) -> TaskRead:  # IDは不要、戻り値はIDを含む
    pass
```

#### 理由 2: セキュリティとバリデーション

```python
# API経由での不正なID指定を防止
@app.post("/api/tasks")
def create_task_endpoint(task: TaskCreate):  # IDフィールドが存在しない
    return task_service.create_task(task)
```

#### 理由 3: 部分更新の最適化

```python
# 必要な項目のみを更新
def update_task_status(task_id: uuid.UUID, status: TaskStatus) -> TaskRead:
    update_data = TaskUpdate(status=status)  # titleやdescriptionは変更しない
    return repository.update(task_id, update_data)
```

## サービス層（Services Layer）の詳細設計

### 1. GTD ビジネスルールの実装

サービス層は「GTD の原則とアプリケーションの仕様」を実装します。

```python
# logic/services/task_service.py - 実際のプロジェクト実装
class TaskService(ServiceBase):
    """タスクのビジネスロジックを管理"""

    def __init__(self, task_repo: TaskRepository, project_repo: ProjectRepository):
        self.task_repo = task_repo
        self.project_repo = project_repo

    def create_task(self, task_data: TaskCreate) -> TaskRead:
        """GTDルールに従ってタスクを作成"""
        # ビジネスルール1: タイトルは必須
        if not task_data.title.strip():
            raise TaskServiceCreateError("タスクのタイトルは必須です")

        # ビジネスルール2: プロジェクトの存在確認
        if task_data.project_id:
            project = self.project_repo.get_by_id(task_data.project_id)
            if not project:
                raise TaskServiceCreateError("指定されたプロジェクトが存在しません")

        # ビジネスルール3: 新規タスクは自動的にInboxに配置（GTD原則）
        if not task_data.status:
            task_data.status = TaskStatus.INBOX

        return self.task_repo.create(task_data)

    def move_to_next_action(self, task_id: uuid.UUID) -> TaskRead:
        """タスクをNext Actionに移動（GTDワークフロー）"""
        task = self.task_repo.get_by_id(task_id)
        if not task:
            raise TaskServiceError("タスクが見つかりません")

        # GTDルール: Inboxからのみ Next Action に移動可能
        if task.status != TaskStatus.INBOX:
            raise TaskServiceError("InboxのタスクのみNext Actionに移動できます")

        update_data = TaskUpdate(status=TaskStatus.NEXT_ACTION)
        return self.task_repo.update(task_id, update_data)
```

### 2. 複雑な GTD ワークフローの実装

```python
class TaskService(ServiceBase):
    def process_inbox_item(self, task_id: uuid.UUID, decision: InboxDecision) -> TaskRead:
        """Inboxアイテムの処理（GTDの核心プロセス）"""
        task = self.task_repo.get_by_id(task_id)

        match decision.action:
            case InboxAction.DELETE:
                # 不要なタスクを削除
                self.task_repo.delete(task_id)
                return None

            case InboxAction.DELEGATE:
                # タスクを委譲
                update_data = TaskUpdate(
                    status=TaskStatus.DELEGATED,
                    description=f"Delegated to: {decision.delegate_to}"
                )
                return self.task_repo.update(task_id, update_data)

            case InboxAction.DO_NOW:
                # 2分以内で完了可能なタスクはすぐに実行
                update_data = TaskUpdate(status=TaskStatus.COMPLETED)
                return self.task_repo.update(task_id, update_data)

            case InboxAction.SCHEDULE:
                # 特定の日時に実行するタスク
                update_data = TaskUpdate(
                    status=TaskStatus.NEXT_ACTION,
                    due_date=decision.scheduled_date
                )
                return self.task_repo.update(task_id, update_data)

            case InboxAction.SOMEDAY_MAYBE:
                # いつかやるかもしれないタスク
                update_data = TaskUpdate(status=TaskStatus.SOMEDAY_MAYBE)
                return self.task_repo.update(task_id, update_data)

    def get_next_actions_by_context(self, context_tags: list[str]) -> list[TaskRead]:
        """コンテキスト別のNext Action取得（GTD実践）"""
        return self.task_repo.get_by_status_and_tags(
            TaskStatus.NEXT_ACTION,
            context_tags
        )
```

### 3. Repository パターンによるデータアクセス分離

```python
# logic/repositories/task.py - 実際のプロジェクト実装
class TaskRepository(BaseRepository[Task, TaskCreate, TaskUpdate]):
    """タスクのデータアクセスを担当"""

    def get_by_status_and_tags(self, status: TaskStatus, tag_names: list[str]) -> list[Task]:
        """ステータスとタグでタスクを検索（GTD実践用）"""
        stmt = (
            select(Task)
            .where(Task.status == status)
            .join(TaskTag)
            .join(Tag)
            .where(Tag.name.in_(tag_names))
        )
        return self.session.exec(stmt).all()

    def get_overdue_tasks(self) -> list[Task]:
        """期限切れタスクの取得"""
        today = date.today()
        stmt = select(Task).where(
            and_(
                Task.due_date < today,
                Task.status.in_([TaskStatus.NEXT_ACTION, TaskStatus.WAITING_FOR])
            )
        )
        return self.session.exec(stmt).all()

    def get_tasks_by_project(self, project_id: uuid.UUID) -> list[Task]:
        """プロジェクト別タスク取得"""
        stmt = select(Task).where(Task.project_id == project_id)
        return self.session.exec(stmt).all()
```

## アプリケーション層（Application Layer）の設計

アプリケーション層は、ビューからビジネスロジックを完全に分離し、トランザクション境界とセッション管理を担当します。

### 1. Application Service パターン

```python
# logic/application/task_application_service.py - 実際のプロジェクト実装
class TaskApplicationService(BaseApplicationService):
    """View層からSession管理を分離し、ビジネスロジックを調整"""

    def create_task(self, command: CreateTaskCommand) -> TaskRead:
        """タスク作成のワークフロー調整"""
        with SqlModelUnitOfWork() as uow:
            # サービスファクトリでDIコンテナから取得
            service_factory = create_service_factory(uow.session)
            task_service = service_factory.create_task_service()

            # ビジネスロジックの実行
            task = task_service.create_task(command.to_create_model())

            # トランザクションコミットは UnitOfWork が管理
            return task

    def process_gtd_inbox_review(self, decisions: list[InboxDecision]) -> list[TaskRead]:
        """GTD Inbox Review の一括処理"""
        results = []

        # 単一トランザクションで複数タスクを処理
        with SqlModelUnitOfWork() as uow:
            service_factory = create_service_factory(uow.session)
            task_service = service_factory.create_task_service()

            for decision in decisions:
                try:
                    result = task_service.process_inbox_item(
                        decision.task_id,
                        decision
                    )
                    results.append(result)
                    logger.info(f"Processed task {decision.task_id}: {decision.action}")
                except TaskServiceError as e:
                    # エラーが発生した場合、全体をロールバック
                    logger.error(f"Failed to process {decision.task_id}: {e}")
                    raise

        return results
```

### 2. Command/Query パターンの実装

```python
# logic/commands/task_commands.py - コマンドパターン
@dataclass
class CreateTaskCommand:
    """タスク作成コマンド"""
    title: str
    description: str = ""
    project_id: uuid.UUID | None = None
    due_date: date | None = None

    def to_create_model(self) -> TaskCreate:
        """ドメインモデルに変換"""
        return TaskCreate(
            title=self.title,
            description=self.description,
            project_id=self.project_id,
            due_date=self.due_date
        )

# logic/queries/task_queries.py - クエリパターン
@dataclass
class GetTasksByStatusQuery:
    """ステータス別タスク取得クエリ"""
    status: TaskStatus
    limit: int = 100
    offset: int = 0

class TaskQuery:
    """タスククエリサービス"""

    def get_tasks_by_status(self, query: GetTasksByStatusQuery) -> list[TaskRead]:
        with SqlModelUnitOfWork() as uow:
            repo = TaskRepository(Task, uow.session)
            tasks = repo.get_by_status(query.status, query.limit, query.offset)
            return [TaskRead.model_validate(task) for task in tasks]
```

### 3. 依存性注入とファクトリパターン

```python
# logic/application/apps.py - Application Services DIコンテナ
class ApplicationServices:
    """Application ServiceのDIコンテナ（遅延生成・スレッドセーフ）
    
    - Viewや呼び出し側は各プロパティまたはget_service()でサービスを取得できます
    - 各サービスはステートレスなため、本コンテナで遅延生成・キャッシュして再利用します
    """
    
    @classmethod
    def create(
        cls,
        *,
        unit_of_work_factory: type[UnitOfWork] = SqlModelUnitOfWork,
    ) -> ApplicationServices:
        """Application Servicesコンテナのファクトリメソッド"""
        return cls(
            _unit_of_work_factory=unit_of_work_factory,
            _services={},
            _lock=Lock(),
        )
    
    def get_service(self, service_type: type[_S]) -> _S:
        """サービスを取得（遅延生成・キャッシュ）"""
        # キャッシュから取得または新規生成
        if service_type not in self._services:
            with self._lock:
                instance = self._build_service_instance(service_type)
                self._services[service_type] = instance
        return self._services[service_type]
    
    # 便利なプロパティアクセス
    @property
    def task(self) -> TaskApplicationService:
        """Taskサービスを取得"""
        return self.get_service(TaskApplicationService)
    
    @property
    def memo(self) -> MemoApplicationService:
        """Memoサービスを取得"""
        return self.get_service(MemoApplicationService)

# logic/factory.py - ファクトリパターン（Service層用）
class ServiceFactory:
    """サービスファクトリ（Session注入）"""

    def __init__(self, repository_factory: RepositoryFactory):
        self.repository_factory = repository_factory

    def get_service(self, service_type: type[ServiceType]) -> ServiceType:
        """サービスインスタンスを取得する"""
        return self._register_service(service_type)

# 使用例
def get_application_services() -> ApplicationServices:
    """View層で使用するDIコンテナ取得"""
    return ApplicationServices.create()
```

### 4. Unit of Work パターンによるトランザクション管理

```python
# logic/unit_of_work.py - トランザクション境界管理
class SqlModelUnitOfWork:
    """SQLModel用のUnit of Workパターン実装"""

    def __init__(self):
        self.session = Session(get_engine())

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.session.commit()  # 正常終了時はコミット
        else:
            self.session.rollback()  # 例外発生時はロールバック
        self.session.close()

    def commit(self):
        """明示的なコミット"""
        self.session.commit()

    def rollback(self):
        """明示的なロールバック"""
        self.session.rollback()
```

## Agent 層（Agent Layer）と AI 統合

Agent 層は、LangChain/LangGraph を使用して LLM ベースの自動化と複雑な判断を実装します。

### 1. GTD 自動化エージェント

```python
# agents/gtd_processor.py - GTD処理の自動化
class GTDProcessorAgent:
    """GTD処理を自動化するエージェント"""

    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(model="gemini-pro")
        self.task_service_tool = TaskServiceTool()  # Services層のツール化

    def auto_categorize_inbox_item(self, task_description: str) -> InboxDecision:
        """Inboxアイテムの自動分類"""
        prompt = f"""
        以下のタスクをGTDの原則に従って分類してください：

        タスク: {task_description}

        分類選択肢:
        1. DELETE - 不要なタスク
        2. DO_NOW - 2分以内で完了可能
        3. DELEGATE - 他者に委譲すべき
        4. SCHEDULE - 特定日時に実行
        5. SOMEDAY_MAYBE - いつかやるかもしれない

        理由と共に回答してください。
        """

        response = self.llm.invoke(prompt)
        return self._parse_categorization_response(response.content)

# agents/task_automation.py - タスク自動化
class TaskAutomationAgent:
    """タスクの自動処理エージェント"""

    def suggest_next_actions(self, context: str, available_time: int) -> list[TaskRead]:
        """現在のコンテキストと利用可能時間に基づく推奨アクション"""
        # LangGraphで複雑なワークフローを実装
        workflow = StateGraph(TaskSuggestionState)

        workflow.add_node("analyze_context", self._analyze_context)
        workflow.add_node("filter_by_time", self._filter_by_available_time)
        workflow.add_node("prioritize_tasks", self._prioritize_tasks)

        workflow.add_edge("analyze_context", "filter_by_time")
        workflow.add_edge("filter_by_time", "prioritize_tasks")

        app = workflow.compile()

        initial_state = TaskSuggestionState(
            context=context,
            available_time=available_time
        )

        result = app.invoke(initial_state)
        return result["suggested_tasks"]
```

### 2. LangGraph による複雑なワークフロー

```python
# agents/workflows/weekly_review.py - 週次レビューの自動化
class WeeklyReviewWorkflow:
    """GTD週次レビューの自動化ワークフロー"""

    def create_review_workflow(self) -> StateGraph:
        """週次レビューのワークフローを構築"""
        workflow = StateGraph(WeeklyReviewState)

        # ノード定義
        workflow.add_node("collect_completed_tasks", self._collect_completed_tasks)
        workflow.add_node("review_project_progress", self._review_project_progress)
        workflow.add_node("update_someday_maybe", self._update_someday_maybe)
        workflow.add_node("plan_next_week", self._plan_next_week)
        workflow.add_node("generate_review_report", self._generate_review_report)

        # エッジ定義（実行順序）
        workflow.add_edge(START, "collect_completed_tasks")
        workflow.add_edge("collect_completed_tasks", "review_project_progress")
        workflow.add_edge("review_project_progress", "update_someday_maybe")
        workflow.add_edge("update_someday_maybe", "plan_next_week")
        workflow.add_edge("plan_next_week", "generate_review_report")
        workflow.add_edge("generate_review_report", END)

        return workflow.compile()

    def _collect_completed_tasks(self, state: WeeklyReviewState) -> dict:
        """今週完了したタスクを収集"""
        task_service = self.app_services.task
        completed_tasks = task_service.get_completed_tasks_this_week()

        return {
            "completed_tasks": completed_tasks,
            "completion_stats": self._calculate_completion_stats(completed_tasks)
        }
```

### 3. Agent-Service 連携パターン

```python
# agents/tools/task_service_tool.py - Services層のツール化
class TaskServiceTool(BaseTool):
    """TaskServiceをLangChainツールとして公開"""

    name = "task_service"
    description = "GTDタスク管理システムとの連携"

    def _run(self, action: str, **kwargs) -> str:
        """エージェントからサービス層を呼び出し"""
        app_services = ApplicationServices.create()
        task_app_service = app_services.task

        match action:
            case "create_task":
                command = CreateTaskCommand(**kwargs)
                task = task_app_service.create_task(command)
                return f"タスクを作成しました: {task.title}"

            case "get_next_actions":
                context = kwargs.get("context", [])
                tasks = task_app_service.get_next_actions_by_context(context)
                return f"Next Actions: {[task.title for task in tasks]}"

            case "complete_task":
                task_id = kwargs["task_id"]
                task = task_app_service.complete_task(task_id)
                return f"タスクを完了しました: {task.title}"
```

- **責務**: LLM を活用した自律的な問題解決、GTD ワークフローの自動化、複数サービスの連携
- **実装**: `LangChain 0.3.26`と`LangGraph 0.4.9`を使用した状態管理型ワークフロー
- **連携**: Services 層をツール化してエージェントから利用
- **詳細**: [Agent 層 設計ガイド](agents_guide.md)を参照してください

## 設計の利点

### 1. 単一責任の原則

- 各クラスが一つの責任のみを持つ
- 修正時の影響範囲が限定される

### 2. テストしやすさ

````python
# ビジネスロジックを単独でテスト可能
## Views層（View Layer）- Flet UI

Views層は、Fletを使用してクロスプラットフォーム対応のモダンなUIを提供します。

### 1. ビューの階層構造

```python
# views/base.py - ベースビュークラス
class BaseView(ABC):
    """全ビューの基底クラス"""

    def __init__(self, page: ft.Page, app_services: ApplicationServices):
        self.page = page
        self.app_services = app_services
        self._content: ft.Control | None = None

    @abstractmethod
    def build(self) -> ft.Control:
        """ビューのUIを構築"""
        pass

    @property
    def content(self) -> ft.Control:
        """ビューのコンテンツを取得（遅延構築）"""
        if self._content is None:
            self._content = self.build()
        return self._content

    def refresh(self) -> None:
        """ビューを再構築"""
        self._content = None
        self.page.update()

# views/main_view.py - メインビュー
class MainView(BaseView):
    """アプリケーションのメインビュー"""

    def __init__(self, page: ft.Page, app_services: ApplicationServices):
        super().__init__(page, app_services)
        self.task_list_view = TaskListView(page, app_services)
        self.inbox_view = InboxView(page, app_services)
        self.project_view = ProjectView(page, app_services)

    def build(self) -> ft.Control:
        """メインレイアウトを構築"""
        return ft.Container(
            content=ft.Row([
                # サイドバー
                ft.Container(
                    content=self._build_sidebar(),
                    width=200,
                    bgcolor=ft.Colors.SURFACE_VARIANT
                ),
                # メインコンテンツエリア
                ft.Container(
                    content=self._build_main_content(),
                    expand=True
                )
            ]),
            expand=True
        )

    def _build_sidebar(self) -> ft.Control:
        """サイドバーメニューを構築"""
        return ft.Column([
            ft.TextButton("📥 Inbox", on_click=self._on_inbox_click),
            ft.TextButton("⚡ Next Actions", on_click=self._on_next_actions_click),
            ft.TextButton("📋 Projects", on_click=self._on_projects_click),
            ft.TextButton("🔍 Contexts", on_click=self._on_contexts_click),
            ft.TextButton("⏰ Scheduled", on_click=self._on_scheduled_click),
            ft.TextButton("🤔 Someday/Maybe", on_click=self._on_someday_click),
        ])
````

### 2. GTD 特化コンポーネント

```python
# views/components/task_component.py - タスクコンポーネント
class TaskComponent(ft.UserControl):
    """GTDタスクを表示するコンポーネント"""

    def __init__(self, task: TaskRead, on_complete: Callable[[str], None] = None):
        super().__init__()
        self.task = task
        self.on_complete = on_complete

    def build(self) -> ft.Control:
        """タスクカードのUIを構築"""
        # GTD分類による色分け
        status_color = self._get_status_color(self.task.status)

        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Checkbox(
                            value=self.task.status == TaskStatus.DONE,
                            on_change=self._on_checkbox_change
                        ),
                        ft.Text(
                            self.task.title,
                            style=ft.TextStyle(
                                decoration=ft.TextDecoration.LINE_THROUGH
                                if self.task.status == TaskStatus.DONE
                                else None
                            ),
                            expand=True
                        ),
                        self._build_status_chip()
                    ]),
                    if self.task.description:
                        ft.Text(
                            self.task.description,
                            size=12,
                            color=ft.Colors.ON_SURFACE_VARIANT
                        ),
                    self._build_metadata_row()
                ]),
                padding=ft.padding.all(16)
            ),
            surface_tint_color=status_color
        )

    def _get_status_color(self, status: TaskStatus) -> str:
        """GTDステータスに応じた色を取得"""
        color_map = {
            TaskStatus.INBOX: ft.Colors.ORANGE,
            TaskStatus.NEXT_ACTION: ft.Colors.GREEN,
            TaskStatus.WAITING: ft.Colors.YELLOW,
            TaskStatus.SCHEDULED: ft.Colors.BLUE,
            TaskStatus.SOMEDAY_MAYBE: ft.Colors.PURPLE,
            TaskStatus.DONE: ft.Colors.GREY,
        }
        return color_map.get(status, ft.Colors.SURFACE)

# views/components/quick_capture.py - クイックキャプチャー
class QuickCaptureComponent(ft.UserControl):
    """GTDクイックキャプチャー（Inbox追加）"""

    def __init__(self, task_service: TaskApplicationService):
        super().__init__()
        self.task_service = task_service
        self.text_field = ft.TextField(
            label="何をしますか？",
            hint_text="思いついたことを何でも入力してください",
            on_submit=self._on_submit,
            expand=True
        )

    def build(self) -> ft.Control:
        return ft.Row([
            self.text_field,
            ft.IconButton(
                icon=ft.icons.ADD,
                tooltip="Inboxに追加",
                on_click=self._on_submit
            )
        ])

    def _on_submit(self, e=None):
        """Inboxアイテムを作成"""
        if not self.text_field.value:
            return

        try:
            command = CreateTaskCommand(
                title=self.text_field.value,
                status=TaskStatus.INBOX
            )
            self.task_service.create_task(command)

            # 成功フィードバック
            self.page.show_snack_bar(
                ft.SnackBar(content=ft.Text("Inboxに追加しました"))
            )
            self.text_field.value = ""
            self.text_field.update()

        except Exception as e:
            logger.exception("Inboxアイテム作成エラー")
            self.page.show_snack_bar(
                ft.SnackBar(
                    content=ft.Text(f"エラー: {str(e)}"),
                    bgcolor=ft.Colors.ERROR
                )
            )
```

### 3. ルーティングとナビゲーション

```python
# router.py - ビュールーティング
class ViewRouter:
    """ビュー間のナビゲーション管理"""

    def __init__(self, page: ft.Page, app_services: ApplicationServices):
        self.page = page
        self.app_services = app_services
        self.views: dict[str, BaseView] = {}
        self.current_view: str = "main"

    def navigate_to(self, view_name: str, **kwargs) -> None:
        """指定されたビューに遷移"""
        if view_name not in self.views:
            self.views[view_name] = self._create_view(view_name)

        view = self.views[view_name]
        self.page.clean()
        self.page.add(view.content)
        self.current_view = view_name
        self.page.update()

    def _create_view(self, view_name: str) -> BaseView:
        """ビューのファクトリメソッド"""
        view_factories = {
            "main": lambda: MainView(self.page, self.app_services),
            "inbox": lambda: InboxView(self.page, self.app_services),
            "projects": lambda: ProjectView(self.page, self.app_services),
            "contexts": lambda: ContextView(self.page, self.app_services),
        }

        factory = view_factories.get(view_name)
        if not factory:
            raise ValueError(f"Unknown view: {view_name}")

        return factory()
```

- **責務**: ユーザーインターフェース、ユーザー体験、GTD 特化 UI、リアルタイム更新
- **実装**: `Flet 0.27.6`を使用したクロスプラットフォーム対応 UI
- **パターン**: MVP パターン、コンポーネントベース設計、ルーティング
- **詳細**: [Views 層 設計ガイド](views_guide.md)を参照してください

## テスト戦略

### 1. 単体テストの構造

```python
# tests/logic/services/test_task_service.py - サービス層テスト
class TestTaskService:
    """TaskService のテスト"""

    def test_create_task_with_valid_data(self):
        """正常なタスク作成のテスト"""
        repository = MockTaskRepository()
        service = TaskService(repository)

        task_data = TaskCreate(
            title="新しいタスク",
            description="説明"
        )

        result = service.create_task(task_data)

        assert result.title == "新しいタスク"
        assert result.status == TaskStatus.INBOX
        assert len(repository.tasks) == 1

    def test_create_task_with_empty_title(self):
        """タイトルが空の場合のテスト"""
        repository = MockTaskRepository()
        service = TaskService(repository)

        with pytest.raises(ValueError, match="タスクのタイトルは必須です"):
            service.create_new_task("")
```

### 2. 統合テストの実装

```python
# tests/integration/test_gtd_workflow.py - GTDワークフロー統合テスト
class TestGTDWorkflow:
    """GTDワークフロー全体のテスト"""

    @pytest.fixture
    def app_services(self):
        """テスト用Application Servicesを作成"""
        return ApplicationServices.create(
            unit_of_work_factory=TestUnitOfWork
        )

    def test_inbox_to_next_action_workflow(self, app_services):
        """Inbox → Next Action の完全なワークフロー"""
        task_app_service = app_services.task

        # 1. Inboxアイテム作成
        command = CreateTaskCommand(
            title="重要な会議の準備",
            status=TaskStatus.INBOX
        )
        inbox_task = task_app_service.create_task(command)

        # 2. GTD処理（分類）
        decision = InboxDecision(
            task_id=inbox_task.id,
            action=InboxAction.MAKE_NEXT_ACTION,
            context_id=None,
            scheduled_date=None
        )

        # 3. Next Actionに変換
        next_action = task_app_service.process_inbox_item(decision)

        # 4. 検証
        assert next_action.status == TaskStatus.NEXT_ACTION
        assert next_action.title == "重要な会議の準備"
```

- **責務**: 品質保証、リグレッション防止、仕様の文書化
- **実装**: `pytest`を使用した包括的テストスイート
- **カバレッジ**: 単体テスト、統合テスト、エンドツーエンドテスト

## 実際の使用例

```python
# main.py - アプリケーションエントリーポイント
def main(page: ft.Page):
    """Fletアプリケーションのメイン関数"""
    # 依存関係の組み立て
    app_services = ApplicationServices.create()
    router = ViewRouter(page, app_services)

    # GTD特化のページ設定
    page.title = "Kage - GTD Task Manager"
    page.theme_mode = ft.ThemeMode.SYSTEM
    page.padding = 0

    # メインビューを表示
    router.navigate_to("main")

if __name__ == "__main__":
    ft.app(target=main)
```

### UI 層では、Application Service を呼び出すだけ

```python
# views/components/task_form.py - タスク作成フォーム
def on_add_task(self, e):
    """タスク追加ボタンのイベントハンドラ"""
    # バリデーション
    if not self.title_field.value:
        self._show_error("タスクのタイトルを入力してください")
        return

    try:
        # Application Serviceを呼び出し
        command = CreateTaskCommand(
            title=self.title_field.value,
            description=self.description_field.value,
            status=TaskStatus.INBOX
        )

        task_app_service = self.app_services.task
        new_task = task_app_service.create_task(command)

        # UI更新
        self._clear_form()
        self._refresh_task_list()
        self._show_success(f"タスク「{new_task.title}」を作成しました")

    except Exception as e:
        logger.exception("タスク作成エラー")
        self._show_error(f"エラーが発生しました: {str(e)}")
```

## まとめ

この設計パターンを採用することで：

- **理解しやすい**: 各層の責任が明確で、GTD の概念と一致
- **修正しやすい**: 影響範囲が限定され、変更の波及を抑制
- **テストしやすい**: 各層を独立してテスト可能
- **拡張しやすい**: AI 機能やエージェント追加が容易
- **再利用しやすい**: コア機能は他のインターフェースでも利用可能

最初は複雑に感じるかもしれませんが、GTD ワークフローの複雑さを管理し、LLM との統合を行う上で、この設計の価値を実感できるはずです。

## 参考資料

- [Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Getting Things Done (GTD)](https://gettingthingsdone.com/)
- [Repository Pattern](https://docs.microsoft.com/en-us/dotnet/architecture/microservices/microservice-ddd-cqrs-patterns/infrastructure-persistence-layer-design)
- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)
- [Flet Documentation](https://flet.dev/)
- [LangChain Documentation](https://python.langchain.com/)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
