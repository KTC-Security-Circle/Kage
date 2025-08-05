import uuid
from datetime import date

from models import Project, Tag, Task, TaskCreate, TaskStatus


def create_test_project(
    title: str = "テストプロジェクト",
    description: str = "テスト用のプロジェクトです",
) -> Project:
    """テスト用Projectインスタンスを作成

    Args:
        title: プロジェクトのタイトル
        description: プロジェクトの説明

    Returns:
        Project: テスト用Projectインスタンス
    """
    from models import ProjectStatus

    return Project(
        id=uuid.uuid4(),
        title=title,
        description=description,
        status=ProjectStatus.ACTIVE,
    )


def create_test_tag(name: str = "テストタグ") -> Tag:
    """テスト用Tagインスタンスを作成

    Args:
        name: タグの名前

    Returns:
        Tag: テスト用Tagインスタンス
    """
    return Tag(
        id=uuid.uuid4(),
        name=name,
    )


def create_test_task(
    title: str = "テストタスク",
    description: str = "テスト用のタスクです",
    status: TaskStatus = TaskStatus.INBOX,
    due_date: date | None = None,
    project_id: uuid.UUID | None = None,
    parent_id: uuid.UUID | None = None,
) -> Task:
    """テスト用Taskインスタンスを作成

    Args:
        title: タスクのタイトル
        description: タスクの説明
        status: タスクのステータス
        due_date: 締切日
        project_id: 所属プロジェクトID
        parent_id: 親タスクID

    Returns:
        Task: テスト用Taskインスタンス
    """
    return Task(
        id=uuid.uuid4(),
        title=title,
        description=description,
        status=status,
        due_date=due_date,
        project_id=project_id,
        parent_id=parent_id,
    )


def create_test_task_create(
    title: str = "テストタスク作成",
    description: str = "テスト用のタスク作成データです",
    status: TaskStatus = TaskStatus.INBOX,
    due_date: date | None = None,
    project_id: uuid.UUID | None = None,
    parent_id: uuid.UUID | None = None,
) -> TaskCreate:
    """テスト用TaskCreateインスタンスを作成

    Args:
        title: タスクのタイトル
        description: タスクの説明
        status: タスクのステータス
        due_date: 締切日
        project_id: 所属プロジェクトID
        parent_id: 親タスクID

    Returns:
        TaskCreate: テスト用TaskCreateインスタンス
    """
    return TaskCreate(
        title=title,
        description=description,
        status=status,
        due_date=due_date,
        project_id=project_id,
        parent_id=parent_id,
    )
