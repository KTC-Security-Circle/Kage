"""TaskTagRepositoryのテストケース

このモジュールは、TaskTagRepositoryクラスのタスクタグ関連の操作を
テストするためのテストケースを提供します。

テスト対象：
- get_by_task_id: タスクIDによる関連取得
- get_by_tag_id: タグIDによる関連取得
- get_by_task_and_tag: タスクとタグの組み合わせによる関連取得
- exists: 関連の存在チェック
- delete_by_task_and_tag: タスクとタグの組み合わせによる関連削除
- delete_by_task_id: タスクIDによる全関連削除
- delete_by_tag_id: タグIDによる全関連削除
"""

import uuid

import pytest
from sqlmodel import Session

from logic.repositories.task_tag import TaskTagRepository
from models import Tag, Task, TaskStatus, TaskTag, TaskTagCreate

# テスト用定数
EXPECTED_TAG_COUNT = 2


def create_test_task(title: str = "テストタスク") -> Task:
    """テスト用のTaskオブジェクトを作成する"""
    return Task(
        title=title,
        description="",
        status=TaskStatus.INBOX,
    )


def create_test_tag(name: str = "テストタグ") -> Tag:
    """テスト用のTagオブジェクトを作成する"""
    return Tag(name=name)


def create_test_task_tag(task_id: uuid.UUID, tag_id: uuid.UUID) -> TaskTag:
    """テスト用のTaskTagオブジェクトを作成する"""
    return TaskTag(task_id=task_id, tag_id=tag_id)


@pytest.fixture
def sample_task_tags(test_session: Session) -> dict[str, list]:
    """テスト用のサンプルタスクタグを作成してデータベースに保存

    Args:
        test_session: テスト用データベースセッション

    Returns:
        dict: 作成されたサンプルデータ（tasks, tags, task_tags）
    """
    # テスト用タスクを作成
    tasks = [
        create_test_task("タスク1"),
        create_test_task("タスク2"),
        create_test_task("タスク3"),
    ]

    # テスト用タグを作成
    tags = [
        create_test_tag("重要"),
        create_test_tag("緊急"),
        create_test_tag("仕事"),
    ]

    # データベースに保存
    for task in tasks:
        test_session.add(task)
    for tag in tags:
        test_session.add(tag)

    test_session.commit()

    # リフレッシュしてIDを取得
    for task in tasks:
        test_session.refresh(task)
    for tag in tags:
        test_session.refresh(tag)

    # TaskTag関連を作成
    task_tags = []
    if tasks[0].id and tags[0].id:
        task_tags.append(create_test_task_tag(tasks[0].id, tags[0].id))  # タスク1-重要
    if tasks[0].id and tags[1].id:
        task_tags.append(create_test_task_tag(tasks[0].id, tags[1].id))  # タスク1-緊急
    if tasks[1].id and tags[0].id:
        task_tags.append(create_test_task_tag(tasks[1].id, tags[0].id))  # タスク2-重要
    if tasks[2].id and tags[2].id:
        task_tags.append(create_test_task_tag(tasks[2].id, tags[2].id))  # タスク3-仕事

    # TaskTagをデータベースに保存
    for task_tag in task_tags:
        test_session.add(task_tag)

    test_session.commit()

    return {
        "tasks": tasks,
        "tags": tags,
        "task_tags": task_tags,
    }


class TestTaskTagRepositoryGetByTaskId:
    """get_by_task_idメソッドのテストクラス"""

    def test_get_by_task_id_returns_related_tags(
        self, task_tag_repository: TaskTagRepository, sample_task_tags: dict[str, list]
    ) -> None:
        """指定されたタスクIDの関連タグを取得できることをテスト"""
        # [AI GENERATED] タスク1のIDで関連を取得
        task1 = sample_task_tags["tasks"][0]
        assert task1.id is not None
        result = task_tag_repository.get_by_task_id(task1.id)

        # [AI GENERATED] タスク1は2つのタグ（重要、緊急）と関連している
        assert len(result) == EXPECTED_TAG_COUNT

        # [AI GENERATED] 全ての結果がタスク1に関連していることを確認
        for task_tag in result:
            assert task_tag.task_id == task1.id

    def test_get_by_task_id_returns_empty_list_for_no_relations(
        self, task_tag_repository: TaskTagRepository, sample_task_tags: dict[str, list]
    ) -> None:
        """関連のないタスクIDで空のリストを返すことをテスト"""
        # [AI GENERATED] 存在しないタスクIDで検索
        non_existent_task_id = uuid.uuid4()
        result = task_tag_repository.get_by_task_id(non_existent_task_id)

        # [AI GENERATED] 空のリストが返されることを確認
        assert result == []


class TestTaskTagRepositoryGetByTagId:
    """get_by_tag_idメソッドのテストクラス"""

    def test_get_by_tag_id_returns_related_tasks(
        self, task_tag_repository: TaskTagRepository, sample_task_tags: dict[str, list]
    ) -> None:
        """指定されたタグIDの関連タスクを取得できることをテスト"""
        # [AI GENERATED] "重要"タグのIDで関連を取得
        important_tag = sample_task_tags["tags"][0]  # "重要"タグ
        assert important_tag.id is not None
        result = task_tag_repository.get_by_tag_id(important_tag.id)

        # [AI GENERATED] "重要"タグは2つのタスク（タスク1、タスク2）と関連している
        assert len(result) == EXPECTED_TAG_COUNT

        # [AI GENERATED] 全ての結果が"重要"タグに関連していることを確認
        for task_tag in result:
            assert task_tag.tag_id == important_tag.id

    def test_get_by_tag_id_returns_empty_list_for_no_relations(
        self, task_tag_repository: TaskTagRepository, sample_task_tags: dict[str, list]
    ) -> None:
        """関連のないタグIDで空のリストを返すことをテスト"""
        # [AI GENERATED] 存在しないタグIDで検索
        non_existent_tag_id = uuid.uuid4()
        result = task_tag_repository.get_by_tag_id(non_existent_tag_id)

        # [AI GENERATED] 空のリストが返されることを確認
        assert result == []


class TestTaskTagRepositoryGetByTaskAndTag:
    """get_by_task_and_tagメソッドのテストクラス"""

    def test_get_by_task_and_tag_finds_existing_relation(
        self, task_tag_repository: TaskTagRepository, sample_task_tags: dict[str, list]
    ) -> None:
        """存在する関連を取得できることをテスト"""
        # [AI GENERATED] 存在する関連（タスク1-重要）を検索
        task1 = sample_task_tags["tasks"][0]
        important_tag = sample_task_tags["tags"][0]
        assert task1.id is not None
        assert important_tag.id is not None

        result = task_tag_repository.get_by_task_and_tag(task1.id, important_tag.id)

        # [AI GENERATED] 関連が取得されることを確認
        assert result is not None
        assert result.task_id == task1.id
        assert result.tag_id == important_tag.id

    def test_get_by_task_and_tag_returns_none_for_nonexistent_relation(
        self, task_tag_repository: TaskTagRepository, sample_task_tags: dict[str, list]
    ) -> None:
        """存在しない関連でNoneを返すことをテスト"""
        # [AI GENERATED] 存在しない関連（タスク2-緊急）を検索
        task2 = sample_task_tags["tasks"][1]
        urgent_tag = sample_task_tags["tags"][1]
        assert task2.id is not None
        assert urgent_tag.id is not None

        result = task_tag_repository.get_by_task_and_tag(task2.id, urgent_tag.id)

        # [AI GENERATED] Noneが返されることを確認
        assert result is None


class TestTaskTagRepositoryExists:
    """existsメソッドのテストクラス"""

    def test_exists_returns_true_for_existing_relation(
        self, task_tag_repository: TaskTagRepository, sample_task_tags: dict[str, list]
    ) -> None:
        """存在する関連でTrueを返すことをテスト"""
        # [AI GENERATED] 存在する関連（タスク1-重要）をチェック
        task1 = sample_task_tags["tasks"][0]
        important_tag = sample_task_tags["tags"][0]
        assert task1.id is not None
        assert important_tag.id is not None

        result = task_tag_repository.exists(task1.id, important_tag.id)

        # [AI GENERATED] Trueが返されることを確認
        assert result is True

    def test_exists_returns_false_for_nonexistent_relation(
        self, task_tag_repository: TaskTagRepository, sample_task_tags: dict[str, list]
    ) -> None:
        """存在しない関連でFalseを返すことをテスト"""
        # [AI GENERATED] 存在しない関連（タスク2-緊急）をチェック
        task2 = sample_task_tags["tasks"][1]
        urgent_tag = sample_task_tags["tags"][1]
        assert task2.id is not None
        assert urgent_tag.id is not None

        result = task_tag_repository.exists(task2.id, urgent_tag.id)

        # [AI GENERATED] Falseが返されることを確認
        assert result is False


class TestTaskTagRepositoryCreate:
    """createメソッドのテストクラス"""

    def test_create_task_tag_success(
        self, task_tag_repository: TaskTagRepository, sample_task_tags: dict[str, list]
    ) -> None:
        """TaskTag作成が成功することをテスト"""
        # [AI GENERATED] 新しい関連を作成（タスク2-緊急）
        task2 = sample_task_tags["tasks"][1]
        urgent_tag = sample_task_tags["tags"][1]
        assert task2.id is not None
        assert urgent_tag.id is not None

        task_tag_data = TaskTagCreate(task_id=task2.id, tag_id=urgent_tag.id)
        result = task_tag_repository.create(task_tag_data)

        # [AI GENERATED] 作成された関連の検証
        assert result is not None
        assert result.task_id == task2.id
        assert result.tag_id == urgent_tag.id

        # [AI GENERATED] データベースに保存されていることを確認
        assert task_tag_repository.exists(task2.id, urgent_tag.id) is True


class TestTaskTagRepositoryDeleteByTaskAndTag:
    """delete_by_task_and_tagメソッドのテストクラス"""

    def test_delete_by_task_and_tag_success(
        self, task_tag_repository: TaskTagRepository, sample_task_tags: dict[str, list]
    ) -> None:
        """TaskTag削除が成功することをテスト"""
        # [AI GENERATED] 存在する関連（タスク1-重要）を削除
        task1 = sample_task_tags["tasks"][0]
        important_tag = sample_task_tags["tags"][0]
        assert task1.id is not None
        assert important_tag.id is not None

        # [AI GENERATED] 削除前に存在することを確認
        assert task_tag_repository.exists(task1.id, important_tag.id) is True

        # [AI GENERATED] 関連を削除
        result = task_tag_repository.delete_by_task_and_tag(task1.id, important_tag.id)

        # [AI GENERATED] 削除が成功したことを確認
        assert result is True

        # [AI GENERATED] 削除後に存在しないことを確認
        assert task_tag_repository.exists(task1.id, important_tag.id) is False

    def test_delete_by_task_and_tag_returns_false_for_nonexistent_relation(
        self, task_tag_repository: TaskTagRepository, sample_task_tags: dict[str, list]
    ) -> None:
        """存在しない関連の削除でFalseを返すことをテスト"""
        # [AI GENERATED] 存在しない関連の削除を試行
        non_existent_task_id = uuid.uuid4()
        non_existent_tag_id = uuid.uuid4()

        result = task_tag_repository.delete_by_task_and_tag(non_existent_task_id, non_existent_tag_id)

        # [AI GENERATED] Falseが返されることを確認
        assert result is False


class TestTaskTagRepositoryDeleteByTaskId:
    """delete_by_task_idメソッドのテストクラス"""

    def test_delete_by_task_id_deletes_all_relations(
        self, task_tag_repository: TaskTagRepository, sample_task_tags: dict[str, list]
    ) -> None:
        """指定されたタスクIDの全関連を削除することをテスト"""
        # [AI GENERATED] タスク1の全関連を削除
        task1 = sample_task_tags["tasks"][0]
        assert task1.id is not None

        # [AI GENERATED] 削除前のタスク1の関連数を確認
        before_relations = task_tag_repository.get_by_task_id(task1.id)
        assert len(before_relations) == EXPECTED_TAG_COUNT  # タスク1は2つのタグと関連

        # [AI GENERATED] タスク1の全関連を削除
        deleted_count = task_tag_repository.delete_by_task_id(task1.id)

        # [AI GENERATED] 削除数が正しいことを確認
        assert deleted_count == EXPECTED_TAG_COUNT

        # [AI GENERATED] 削除後にタスク1の関連が存在しないことを確認
        after_relations = task_tag_repository.get_by_task_id(task1.id)
        assert len(after_relations) == 0

    def test_delete_by_task_id_returns_zero_for_no_relations(
        self, task_tag_repository: TaskTagRepository, sample_task_tags: dict[str, list]
    ) -> None:
        """関連のないタスクIDで削除数0を返すことをテスト"""
        # [AI GENERATED] 存在しないタスクIDで削除を試行
        non_existent_task_id = uuid.uuid4()
        deleted_count = task_tag_repository.delete_by_task_id(non_existent_task_id)

        # [AI GENERATED] 削除数が0であることを確認
        assert deleted_count == 0


class TestTaskTagRepositoryDeleteByTagId:
    """delete_by_tag_idメソッドのテストクラス"""

    def test_delete_by_tag_id_deletes_all_relations(
        self, task_tag_repository: TaskTagRepository, sample_task_tags: dict[str, list]
    ) -> None:
        """指定されたタグIDの全関連を削除することをテスト"""
        # [AI GENERATED] "重要"タグの全関連を削除
        important_tag = sample_task_tags["tags"][0]
        assert important_tag.id is not None

        # [AI GENERATED] 削除前の"重要"タグの関連数を確認
        before_relations = task_tag_repository.get_by_tag_id(important_tag.id)
        assert len(before_relations) == EXPECTED_TAG_COUNT  # "重要"タグは2つのタスクと関連

        # [AI GENERATED] "重要"タグの全関連を削除
        deleted_count = task_tag_repository.delete_by_tag_id(important_tag.id)

        # [AI GENERATED] 削除数が正しいことを確認
        assert deleted_count == EXPECTED_TAG_COUNT

        # [AI GENERATED] 削除後に"重要"タグの関連が存在しないことを確認
        after_relations = task_tag_repository.get_by_tag_id(important_tag.id)
        assert len(after_relations) == 0

    def test_delete_by_tag_id_returns_zero_for_no_relations(
        self, task_tag_repository: TaskTagRepository, sample_task_tags: dict[str, list]
    ) -> None:
        """関連のないタグIDで削除数0を返すことをテスト"""
        # [AI GENERATED] 存在しないタグIDで削除を試行
        non_existent_tag_id = uuid.uuid4()
        deleted_count = task_tag_repository.delete_by_tag_id(non_existent_tag_id)

        # [AI GENERATED] 削除数が0であることを確認
        assert deleted_count == 0


class TestTaskTagRepositoryUnsupportedMethods:
    """TaskTagRepositoryでサポートされていないメソッドのテストクラス"""

    def test_get_by_id_returns_none(self, task_tag_repository: TaskTagRepository) -> None:
        """get_by_idメソッドが常にNoneを返すことをテスト"""
        # [AI GENERATED] TaskTagは複合主キーのため、get_by_idはサポートされない
        random_id = uuid.uuid4()
        result = task_tag_repository.get_by_id(random_id)

        # [AI GENERATED] 常にNoneが返されることを確認
        assert result is None

    def test_update_returns_none(self, task_tag_repository: TaskTagRepository) -> None:
        """updateメソッドが常にNoneを返すことをテスト"""
        # [AI GENERATED] TaskTagは更新操作をサポートしない
        random_id = uuid.uuid4()
        update_data = TaskTagCreate(task_id=uuid.uuid4(), tag_id=uuid.uuid4())
        result = task_tag_repository.update(random_id, update_data)

        # [AI GENERATED] 常にNoneが返されることを確認
        assert result is None

    def test_delete_returns_false(self, task_tag_repository: TaskTagRepository) -> None:
        """deleteメソッドが常にFalseを返すことをテスト"""
        # [AI GENERATED] TaskTagは単一IDでの削除をサポートしない
        random_id = uuid.uuid4()
        result = task_tag_repository.delete(random_id)

        # [AI GENERATED] 常にFalseが返されることを確認
        assert result is False
