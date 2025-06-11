# アーキテクチャ設計ガイド - モデル層とロジック層

## はじめに

このドキュメントでは、SigotoDekiruKun アプリケーションで採用している**モデル層**と**ロジック層**の設計思想について、Python 初学者向けに分かりやすく説明します。

## なぜアーキテクチャが重要なのか？

### 悪い例：すべてを一つのファイルに書く場合

```python
# ❌ 悪い例：すべてが混在している
import flet as ft
from sqlmodel import Session, create_engine

def main():
    # データベース接続、UI作成、ビジネスロジックがすべて混在
    engine = create_engine("sqlite:///tasks.db")

    def on_add_task(e):
        # UIからデータを取得
        title = title_field.value

        # バリデーション
        if not title:
            show_error("タイトルを入力してください")
            return

        # データベースに保存
        with Session(engine) as session:
            task = Task(title=title)
            session.add(task)
            session.commit()

        # UIを更新
        refresh_task_list()

    # UIコンポーネント作成
    title_field = ft.TextField(label="タスクタイトル")
    # ...
```

この書き方の問題点：

- 一つの関数で多くの責任を負っている
- テストが困難
- 修正時に他の部分に影響が出やすい
- コードの再利用ができない

### 良い例：責任を分離した場合

```python
# ✅ 良い例：責任が分離されている

# models/task.py - データ構造の定義
class Task(SQLModel):
    title: str
    completed: bool = False

# logic/task.py - ビジネスロジック
class TaskService:
    def create_task(self, title: str) -> TaskRead:
        # バリデーションとタスク作成のロジック
        pass

# ui/task_view.py - UI表示
class TaskView:
    def __init__(self, task_service: TaskService):
        self.task_service = task_service

    def on_add_task(self, e):
        # UIからサービス層を呼び出すだけ
        self.task_service.create_task(title)
```

## レイヤー構造の概要

```plain text
┌─────────────────┐
│   UI Layer      │ ← ユーザーインターフェース（Flet）
│   (Presentation)│
├─────────────────┤
│  Logic Layer    │ ← ビジネスロジック・サービス
│  (Business)     │
├─────────────────┤
│  Model Layer    │ ← データ構造・データベース
│  (Data)         │
└─────────────────┘
```

## モデル層（Model Layer）の役割

### 1. データ構造の定義

モデル層は「データがどのような形をしているか」を定義します。

```python
# models/task.py
class TaskBase(SQLModel):
    """タスクの基本的な属性を定義"""
    title: str = Field(index=True)  # タスクのタイトル
    description: str = Field(default="")  # 説明
    completed: bool = Field(default=False)  # 完了状態
    created_at: datetime = Field(default_factory=datetime.now)  # 作成日時
```

### 2. 異なる用途に応じたモデルの提供

```python
class TaskCreate(TaskBase):
    """新規作成時に使用（IDは不要）"""
    pass

class TaskRead(TaskBase):
    """読み取り時に使用（IDが必要）"""
    id: int

class TaskUpdate(SQLModel):
    """更新時に使用（変更する項目のみ）"""
    title: str | None = None
    description: str | None = None
    completed: bool | None = None
```

### なぜ複数のモデルを作るの？

#### 理由 1: 用途に応じた制約

- 新規作成時には ID は不要（データベースが自動生成）
- 読み取り時には ID が必要（どのタスクかを特定するため）
- 更新時には変更する項目のみを受け取る

#### 理由 2: セキュリティ

- API で受け取るデータと内部で使うデータを分離
- 不正なデータの侵入を防ぐ

### 3. データの整合性保証

- タスク作成時のクラスと分離することで、IDチェックを行う関数を定義がいらなくなる

## ロジック層（Logic Layer）の役割

### 1. ビジネスルールの実装

ロジック層は「アプリケーションの仕様」を実装します。

```python
class TaskService:
    def create_new_task(self, title: str, description: str = "") -> TaskRead:
        """新しいタスクを作成"""
        # ビジネスルール：タイトルは必須
        if not title.strip():
            raise ValueError("タスクのタイトルは必須です")

        # データベースへの保存（リポジトリ層に委譲）
        created_task = self.repository.create_task(
            TaskCreate(title=title, description=description)
        )

        # 読み取り用モデルに変換して返す
        return TaskRead.model_validate(created_task)
```

### 2. 複雑な操作の組み合わせ

```python
def toggle_task_status(self, task_id: int) -> TaskRead | None:
    """タスクの完了状態を切り替え"""
    # 1. タスクを取得
    task = self.repository.get_task_by_id(task_id)
    if not task:
        return None

    # 2. 状態を反転
    task.completed = not task.completed

    # 3. 更新して保存
    updated_task = self.repository.update_task(task, TaskUpdate())

    # 4. 結果を返す
    return TaskRead.model_validate(updated_task)
```

### 3. Repository パターンの採用

データベースアクセスを Repository クラスに分離：

```python
class TaskRepository:
    """データベースアクセスを担当"""

    def create_task(self, task_data: TaskCreate) -> Task:
        """データベースにタスクを保存"""
        db_task = Task.model_validate(task_data)
        with Session(self.engine) as session:
            session.add(db_task)
            session.commit()
            session.refresh(db_task)
        return db_task

    def get_tasks_by_completed(self) -> list[Task]:
        """完了済みタスクを取得"""
        stmt = select(Task).where(Task.completed is True)
        return self._get_tasks_by_stmt(stmt)
```

### なぜ Repository パターンを使うの？

#### 理由 1: データベースの種類を変更しやすい

- SQLite から PostgreSQL に変更する場合
- Repository の実装だけを変更すればよい

#### 理由 2: テストしやすい

```python
# テスト用のモックRepositoryを作成可能
class MockTaskRepository:
    def __init__(self):
        self.tasks = []

    def create_task(self, task_data: TaskCreate) -> Task:
        # メモリ上でタスクを管理
        task = Task(**task_data.model_dump(), id=len(self.tasks) + 1)
        self.tasks.append(task)
        return task
```

## UI 補助クラスの設計

UI に関連する処理も分離：

```python
class TaskUIHelper:
    """UI表示のための補助機能"""

    @staticmethod
    def format_task_title(task: TaskRead) -> str:
        """タスクタイトルを表示用にフォーマット"""
        if task.completed:
            return f"✓ {task.title}"  # 完了済み
        return f"○ {task.title}"     # 未完了

    @staticmethod
    def validate_task_input(title: str, description: str = "") -> tuple[bool, str]:
        """入力値の検証"""
        if not title or not title.strip():
            return False, "タスクのタイトルを入力してください"

        if len(title.strip()) > TASK_TITLE_MAX_LENGTH:
            return False, "タスクのタイトルは100文字以内で入力してください"

        return True, ""
```

## 設計の利点

### 1. 単一責任の原則

- 各クラスが一つの責任のみを持つ
- 修正時の影響範囲が限定される

### 2. テストしやすさ

```python
# ビジネスロジックを単独でテスト可能
def test_create_task_with_empty_title():
    repository = MockTaskRepository()
    service = TaskService(repository)

    with pytest.raises(ValueError, match="タスクのタイトルは必須です"):
        service.create_new_task("")
```

### 3. 再利用性

- サービス層は CLI アプリや Web アプリでも使用可能
- モデルは他のプロジェクトでも流用可能

### 4. 保守性

- 機能追加時に適切な場所にコードを配置
- バグ修正時に影響範囲を特定しやすい

## 実際の使用例

```python
# main.py
def main():
    # 依存関係の組み立て
    repository = TaskRepository()
    service = TaskService(repository)
    ui_helper = TaskUIHelper()

    # UI層では、サービス層を呼び出すだけ
    def on_add_task(e):
        is_valid, error_msg = ui_helper.validate_task_input(title_field.value)
        if not is_valid:
            show_error(error_msg)
            return

        try:
            new_task = service.create_new_task(title_field.value, description_field.value)
            refresh_task_list()
        except ValueError as e:
            show_error(str(e))
```

## まとめ

この設計パターンを採用することで：

- **理解しやすい**: 各クラスの責任が明確
- **修正しやすい**: 影響範囲が限定される
- **テストしやすい**: 各層を独立してテスト可能
- **拡張しやすい**: 新機能を適切な場所に配置
- **再利用しやすい**: 他のプロジェクトでも流用可能

最初は複雑に感じるかもしれませんが、アプリケーションが大きくなるにつれて、この設計の価値を実感できるはずです。

## 参考資料

- [Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Repository Pattern](https://docs.microsoft.com/en-us/dotnet/architecture/microservices/microservice-ddd-cqrs-patterns/infrastructure-persistence-layer-design)
- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)
