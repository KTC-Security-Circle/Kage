"""TermRepositoryのテストケース

このモジュールは、TermRepositoryクラスの用語固有の操作を
テストするためのテストケースを提供します。

テスト対象：
- create: 用語作成
- get_by_key: キーによる取得
- search: 用語検索
- add_tag/remove_tag: タグ操作
- add_synonym/remove_synonym: 同義語操作
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from sqlmodel import Session

    from logic.repositories.term import TermRepository

from errors import AlreadyExistsError, NotFoundError
from logic.repositories.term import TermRepository
from models import Tag, Term, TermCreate, TermStatus


@pytest.fixture
def term_repository(test_session: Session) -> TermRepository:
    """TermRepositoryのフィクスチャ

    Args:
        test_session: テスト用データベースセッション

    Returns:
        TermRepository: 用語リポジトリのインスタンス
    """
    return TermRepository(test_session)


def create_test_term(
    key: str = "test_term",
    title: str = "テスト用語",
    description: str = "テスト用の用語説明",
    status: TermStatus = TermStatus.DRAFT,
) -> Term:
    """テスト用のTermオブジェクトを作成する

    Args:
        key: 用語のキー
        title: 用語のタイトル
        description: 用語の説明
        status: 用語のステータス

    Returns:
        作成されたTermオブジェクト
    """
    return Term(
        key=key,
        title=title,
        description=description,
        status=status,
    )


class TestTermRepositoryCreate:
    """createメソッドのテストクラス"""

    def test_create_term_success(self, term_repository: TermRepository) -> None:
        """用語を正常に作成できることをテスト"""
        term_data = TermCreate(
            key="LLM",
            title="大規模言語モデル",
            description="Large Language Modelの略称",
            status=TermStatus.APPROVED,
        )

        term = term_repository.create(term_data)

        assert term.id is not None
        assert term.key == "LLM"
        assert term.title == "大規模言語モデル"
        assert term.description == "Large Language Modelの略称"
        assert term.status == TermStatus.APPROVED

    def test_create_term_duplicate_key_raises_error(self, term_repository: TermRepository) -> None:
        """同じキーで用語を作成すると例外が発生することをテスト"""
        term_data = TermCreate(
            key="RAG",
            title="検索拡張生成",
            description="Retrieval Augmented Generationの略称",
        )

        term_repository.create(term_data)

        with pytest.raises(AlreadyExistsError):
            term_repository.create(term_data)


class TestTermRepositoryGetByKey:
    """get_by_keyメソッドのテストクラス"""

    def test_get_by_key_success(self, term_repository: TermRepository, test_session: Session) -> None:
        """キーで用語を取得できることをテスト"""
        term = create_test_term(key="AI", title="人工知能")
        test_session.add(term)
        test_session.commit()
        test_session.refresh(term)

        result = term_repository.get_by_key("AI")

        assert result.id == term.id
        assert result.key == "AI"
        assert result.title == "人工知能"

    def test_get_by_key_not_found_raises_error(self, term_repository: TermRepository) -> None:
        """存在しないキーで取得すると例外が発生することをテスト"""
        with pytest.raises(NotFoundError):
            term_repository.get_by_key("NOT_EXISTS")


class TestTermRepositorySearch:
    """searchメソッドのテストクラス"""

    def test_search_by_query(self, term_repository: TermRepository, test_session: Session) -> None:
        """クエリで用語を検索できることをテスト"""
        terms = [
            create_test_term(key="ML", title="機械学習", description="Machine Learning"),
            create_test_term(key="DL", title="深層学習", description="Deep Learning"),
            create_test_term(key="RL", title="強化学習", description="Reinforcement Learning"),
        ]

        for term in terms:
            test_session.add(term)
        test_session.commit()

        results = term_repository.search(query="学習")

        expected_count = 3
        assert len(results) == expected_count

    def test_search_by_status(self, term_repository: TermRepository, test_session: Session) -> None:
        """ステータスで用語をフィルタリングできることをテスト"""
        terms = [
            create_test_term(key="APPROVED1", title="承認済み1", status=TermStatus.APPROVED),
            create_test_term(key="DRAFT1", title="草案1", status=TermStatus.DRAFT),
            create_test_term(key="APPROVED2", title="承認済み2", status=TermStatus.APPROVED),
        ]

        for term in terms:
            test_session.add(term)
        test_session.commit()

        results = term_repository.search(status=TermStatus.APPROVED)

        expected_count = 2
        assert len(results) == expected_count


class TestTermRepositoryTagOperations:
    """タグ操作のテストクラス"""

    def test_add_tag_to_term(self, term_repository: TermRepository, test_session: Session) -> None:
        """用語にタグを追加できることをテスト"""
        term = create_test_term(key="TEST", title="テスト用語")
        tag = Tag(name="技術")

        test_session.add(term)
        test_session.add(tag)
        test_session.commit()
        test_session.refresh(term)
        test_session.refresh(tag)

        assert term.id is not None
        assert tag.id is not None

        result = term_repository.add_tag(term.id, tag.id)

        assert len(result.tags) == 1
        assert result.tags[0].name == "技術"

    def test_remove_tag_from_term(self, term_repository: TermRepository, test_session: Session) -> None:
        """用語からタグを削除できることをテスト"""
        term = create_test_term(key="TEST", title="テスト用語")
        tag = Tag(name="技術")

        test_session.add(term)
        test_session.add(tag)
        test_session.commit()
        test_session.refresh(term)
        test_session.refresh(tag)

        assert term.id is not None
        assert tag.id is not None

        term_repository.add_tag(term.id, tag.id)
        result = term_repository.remove_tag(term.id, tag.id)

        assert len(result.tags) == 0


class TestTermRepositorySynonymOperations:
    """同義語操作のテストクラス"""

    def test_add_synonym_to_term(self, term_repository: TermRepository, test_session: Session) -> None:
        """用語に同義語を追加できることをテスト"""
        term = create_test_term(key="AI", title="人工知能")

        test_session.add(term)
        test_session.commit()
        test_session.refresh(term)

        assert term.id is not None

        result = term_repository.add_synonym(term.id, "Artificial Intelligence")

        assert len(result.synonyms) == 1
        assert result.synonyms[0].text == "Artificial Intelligence"

    def test_remove_synonym_from_term(self, term_repository: TermRepository, test_session: Session) -> None:
        """用語から同義語を削除できることをテスト"""
        term = create_test_term(key="AI", title="人工知能")

        test_session.add(term)
        test_session.commit()
        test_session.refresh(term)

        assert term.id is not None

        result = term_repository.add_synonym(term.id, "Artificial Intelligence")
        synonym_id = result.synonyms[0].id

        assert synonym_id is not None

        result = term_repository.remove_synonym(term.id, synonym_id)

        assert len(result.synonyms) == 0
