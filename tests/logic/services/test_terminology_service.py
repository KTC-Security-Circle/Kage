"""TerminologyServiceのテストケース

このモジュールは、TerminologyServiceクラスの
インポート/エクスポートおよびfor_agents API機能を
テストするためのテストケースを提供します。

テスト対象：
- import_from_csv/export_to_csv: CSV形式でのインポート/エクスポート
- import_from_json/export_to_json: JSON形式でのインポート/エクスポート
- for_agents_top_k: エージェント用のtop-k抽出
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from pathlib import Path

    from sqlmodel import Session

from logic.repositories import RepositoryFactory
from logic.services.terminology_service import TerminologyService
from models import Tag, Term, TermCreate, TermStatus


@pytest.fixture
def terminology_service(test_session: Session) -> TerminologyService:
    """TerminologyServiceのフィクスチャ

    Args:
        test_session: テスト用データベースセッション

    Returns:
        TerminologyService: 用語管理サービスのインスタンス
    """
    repo_factory = RepositoryFactory(test_session)
    return TerminologyService.build_service(repo_factory)


@pytest.fixture
def sample_terms(test_session: Session, terminology_service: TerminologyService) -> list[Term]:
    """テスト用のサンプル用語を作成

    Args:
        test_session: テスト用データベースセッション
        terminology_service: 用語管理サービス

    Returns:
        list[Term]: 作成されたサンプル用語のリスト
    """
    terms_data = [
        TermCreate(
            key="AI",
            title="人工知能",
            description="Artificial Intelligenceの略称",
            status=TermStatus.APPROVED,
        ),
        TermCreate(
            key="ML",
            title="機械学習",
            description="Machine Learningの略称",
            status=TermStatus.APPROVED,
        ),
        TermCreate(
            key="DL",
            title="深層学習",
            description="Deep Learningの略称",
            status=TermStatus.DRAFT,
        ),
    ]

    terms = []
    for term_data in terms_data:
        term = terminology_service.term_repo.create(term_data)
        assert term.id is not None
        terms.append(term)

    # 同義語追加
    terminology_service.term_repo.add_synonym(terms[0].id, "Artificial Intelligence")
    terminology_service.term_repo.add_synonym(terms[1].id, "Machine Learning")

    return terms


class TestTerminologyServiceImportExport:
    """インポート/エクスポート機能のテストクラス"""

    def test_export_import_csv_roundtrip(
        self,
        terminology_service: TerminologyService,
        sample_terms: list[Term],
        tmp_path: Path,
    ) -> None:
        """CSV形式でのエクスポート→インポートの往復テスト"""
        csv_file = tmp_path / "terms.csv"

        # エクスポート
        export_count = terminology_service.export_to_csv(csv_file)
        expected_export_count = 3
        assert export_count == expected_export_count
        assert csv_file.exists()

        # 既存データを削除
        for term in sample_terms:
            assert term.id is not None
            terminology_service.term_repo.delete(term.id)

        # インポート
        result = terminology_service.import_from_csv(csv_file)
        assert result.success_count == expected_export_count
        assert result.failed_count == 0

        # データ検証
        imported_terms = terminology_service.term_repo.get_all(with_details=True)
        assert len(imported_terms) == expected_export_count

        # キーでソート
        imported_terms.sort(key=lambda t: t.key)

        assert imported_terms[0].key == "AI"
        assert imported_terms[0].title == "人工知能"
        assert len(imported_terms[0].synonyms) == 1

    def test_export_import_json_roundtrip(
        self,
        terminology_service: TerminologyService,
        sample_terms: list[Term],
        tmp_path: Path,
    ) -> None:
        """JSON形式でのエクスポート→インポートの往復テスト"""
        json_file = tmp_path / "terms.json"

        # エクスポート
        export_count = terminology_service.export_to_json(json_file)
        expected_export_count = 3
        assert export_count == expected_export_count
        assert json_file.exists()

        # JSONファイルの検証
        with json_file.open(encoding="utf-8") as f:
            data = json.load(f)
        assert len(data) == expected_export_count
        assert data[0]["key"] == "AI"

        # 既存データを削除
        for term in sample_terms:
            assert term.id is not None
            terminology_service.term_repo.delete(term.id)

        # インポート
        result = terminology_service.import_from_json(json_file)
        assert result.success_count == expected_export_count
        assert result.failed_count == 0

        # データ検証
        imported_terms = terminology_service.term_repo.get_all(with_details=True)
        assert len(imported_terms) == expected_export_count


class TestTerminologyServiceForAgents:
    """for_agents API機能のテストクラス"""

    def test_for_agents_top_k_basic(
        self,
        terminology_service: TerminologyService,
        sample_terms: list[Term],
        test_session: Session,
    ) -> None:
        """基本的なtop-k抽出のテスト"""
        results = terminology_service.for_agents_top_k(k=2)

        expected_count = 2
        assert len(results) == expected_count

        # 承認済み用語が優先されることを確認
        assert all(r.key in ["AI", "ML"] for r in results)

    def test_for_agents_top_k_with_query(
        self,
        terminology_service: TerminologyService,
        sample_terms: list[Term],
    ) -> None:
        """クエリ指定でのtop-k抽出のテスト"""
        results = terminology_service.for_agents_top_k(query="学習", k=5)

        # "学習"を含む用語が優先されることを確認
        assert any(r.key in ["ML", "DL"] for r in results)

    def test_for_agents_top_k_with_tags(
        self,
        terminology_service: TerminologyService,
        sample_terms: list[Term],
        test_session: Session,
    ) -> None:
        """タグフィルタ指定でのtop-k抽出のテスト"""
        # タグを作成して付与
        tag = Tag(name="技術")
        test_session.add(tag)
        test_session.commit()
        test_session.refresh(tag)

        assert sample_terms[0].id is not None
        assert tag.id is not None

        terminology_service.term_repo.add_tag(sample_terms[0].id, tag.id)

        # タグでフィルタリング
        results = terminology_service.for_agents_top_k(tags=[tag.id], k=5)

        # タグが付与された用語のみが含まれることを確認
        assert len(results) >= 1
        assert any(r.key == "AI" for r in results)

    def test_for_agents_top_k_exclude_tags(
        self,
        terminology_service: TerminologyService,
        sample_terms: list[Term],
        test_session: Session,
    ) -> None:
        """タグ除外指定でのtop-k抽出のテスト"""
        # タグを作成して付与
        tag = Tag(name="除外")
        test_session.add(tag)
        test_session.commit()
        test_session.refresh(tag)

        assert sample_terms[0].id is not None
        assert tag.id is not None

        terminology_service.term_repo.add_tag(sample_terms[0].id, tag.id)

        # タグで除外
        results = terminology_service.for_agents_top_k(exclude_tags=[tag.id], k=5)

        # 除外タグが付与された用語が含まれないことを確認
        assert all(r.key != "AI" for r in results)

    def test_for_agents_top_k_includes_synonyms(
        self,
        terminology_service: TerminologyService,
        sample_terms: list[Term],
    ) -> None:
        """同義語が含まれることのテスト"""
        results = terminology_service.for_agents_top_k(k=5)

        # 同義語が含まれることを確認
        ai_term = next((r for r in results if r.key == "AI"), None)
        assert ai_term is not None
        assert "Artificial Intelligence" in ai_term.synonyms

    def test_for_agents_top_k_to_prompt_text(
        self,
        terminology_service: TerminologyService,
        sample_terms: list[Term],
    ) -> None:
        """プロンプトテキスト生成のテスト"""
        results = terminology_service.for_agents_top_k(k=1)

        assert len(results) >= 1

        prompt_text = results[0].to_prompt_text()

        # プロンプトテキストに必要な情報が含まれることを確認
        assert results[0].key in prompt_text
        assert results[0].title in prompt_text


class TestTerminologyServiceLargeDataset:
    """大規模データセットのテスト"""

    def test_import_export_100_terms(
        self,
        terminology_service: TerminologyService,
        tmp_path: Path,
    ) -> None:
        """100件の用語のインポート/エクスポート往復テスト"""
        json_file = tmp_path / "large_terms.json"

        # 100件の用語データを生成
        large_dataset = [
            {
                "key": f"TERM_{i:03d}",
                "title": f"用語{i}",
                "description": f"用語{i}の説明",
                "status": "approved" if i % 2 == 0 else "draft",
                "source_url": f"https://example.com/term{i}",
                "synonyms": [f"synonym{i}_1", f"synonym{i}_2"],
                "tags": [f"tag{i % 5}"],
            }
            for i in range(1, 101)
        ]

        # JSONファイルに保存
        with json_file.open("w", encoding="utf-8") as f:
            json.dump(large_dataset, f, ensure_ascii=False)

        # インポート
        import_result = terminology_service.import_from_json(json_file)
        expected_count = 100
        assert import_result.success_count == expected_count
        assert import_result.failed_count == 0

        # エクスポート
        export_file = tmp_path / "exported_terms.json"
        export_count = terminology_service.export_to_json(export_file)
        assert export_count == expected_count

        # エクスポートデータの検証
        with export_file.open(encoding="utf-8") as f:
            exported_data = json.load(f)
        assert len(exported_data) == expected_count

        # データ一致の確認（キーでソート）
        exported_data.sort(key=lambda x: x["key"])
        large_dataset.sort(key=lambda x: x["key"])

        for original, exported in zip(large_dataset, exported_data, strict=True):
            assert original["key"] == exported["key"]
            assert original["title"] == exported["title"]
            assert original["description"] == exported["description"]
            assert original["status"] == exported["status"]
