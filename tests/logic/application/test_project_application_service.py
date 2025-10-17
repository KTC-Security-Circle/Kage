"""ProjectApplicationService の軽量テスト（現行API）。

Unit of Work をモックして Application Service の主要フローのみを検証する。
外部依存はモック化し、ビジネスフローの連携が行われることだけを確認する。
"""

from __future__ import annotations

import uuid
from unittest.mock import Mock

import pytest

from logic.application.project_application_service import ProjectApplicationService, ProjectValidationError
from models import ProjectRead, ProjectStatus, ProjectUpdate


@pytest.fixture
def mock_unit_of_work() -> Mock:
    """モックの Unit of Work を作成する。"""
    mock_uow = Mock()
    mock_service_factory = Mock()
    mock_project_service = Mock()

    mock_uow.service_factory = mock_service_factory
    mock_uow.get_service = Mock(return_value=mock_project_service)
    mock_service_factory.get_service.return_value = mock_project_service

    mock_uow.__enter__ = Mock(return_value=mock_uow)
    mock_uow.__exit__ = Mock(return_value=None)
    return mock_uow


@pytest.fixture
def mock_unit_of_work_factory(mock_unit_of_work: Mock) -> Mock:
    """モックの Unit of Work Factory を作成する。"""
    return Mock(return_value=mock_unit_of_work)


@pytest.fixture
def project_app_service(mock_unit_of_work_factory: Mock) -> ProjectApplicationService:
    """ProjectApplicationService のインスタンスを返す。"""
    return ProjectApplicationService(mock_unit_of_work_factory)  # type: ignore[arg-type]


@pytest.fixture
def sample_project_read() -> ProjectRead:
    """ProjectRead のサンプルを返す。"""
    return ProjectRead(id=uuid.uuid4(), title="P", description=None, status=ProjectStatus.ACTIVE)


def test_create_success(
    project_app_service: ProjectApplicationService,
    mock_unit_of_work: Mock,
    sample_project_read: ProjectRead,
) -> None:
    """正常系: プロジェクト作成成功。"""
    mock_proj_service = mock_unit_of_work.service_factory.get_service.return_value
    mock_proj_service.create.return_value = sample_project_read

    result = project_app_service.create(title="P", description=None)

    assert isinstance(result, ProjectRead)
    assert result.title == "P"
    mock_proj_service.create.assert_called_once()


def test_create_validation_error(project_app_service: ProjectApplicationService) -> None:
    """異常系: プロジェクト作成時のバリデーションエラー。"""
    with pytest.raises(ProjectValidationError, match="プロジェクトタイトルを入力してください"):
        project_app_service.create(title="   ")


def test_delete_success(project_app_service: ProjectApplicationService, mock_unit_of_work: Mock) -> None:
    """正常系: プロジェクト削除成功。"""
    mock_proj_service = mock_unit_of_work.service_factory.get_service.return_value
    mock_proj_service.delete.return_value = True

    pid = uuid.uuid4()
    assert project_app_service.delete(pid) is True
    mock_proj_service.delete.assert_called_once_with(pid)


def test_delete_failure(project_app_service: ProjectApplicationService, mock_unit_of_work: Mock) -> None:
    """異常系: プロジェクト削除失敗時は False を返す。"""
    mock_proj_service = mock_unit_of_work.service_factory.get_service.return_value
    mock_proj_service.delete.return_value = False

    pid = uuid.uuid4()
    assert project_app_service.delete(pid) is False
    mock_proj_service.delete.assert_called_once_with(pid)


def test_update_success(
    project_app_service: ProjectApplicationService,
    mock_unit_of_work: Mock,
    sample_project_read: ProjectRead,
) -> None:
    """正常系: プロジェクト更新成功。"""
    mock_proj_service = mock_unit_of_work.service_factory.get_service.return_value
    mock_proj_service.update.return_value = sample_project_read

    update_data = ProjectUpdate(title="更新", description="desc")

    result = project_app_service.update(sample_project_read.id, update_data)

    assert result is sample_project_read
    mock_proj_service.update.assert_called_once_with(sample_project_read.id, update_data)


def test_get_by_id_success(
    project_app_service: ProjectApplicationService,
    mock_unit_of_work: Mock,
    sample_project_read: ProjectRead,
) -> None:
    """正常系: ID指定取得成功。"""
    mock_proj_service = mock_unit_of_work.service_factory.get_service.return_value
    mock_proj_service.get_by_id.return_value = sample_project_read

    res = project_app_service.get_by_id(sample_project_read.id)
    assert res is sample_project_read
    mock_proj_service.get_by_id.assert_called_once_with(sample_project_read.id)


def test_get_all_projects(
    project_app_service: ProjectApplicationService,
    mock_unit_of_work: Mock,
    sample_project_read: ProjectRead,
) -> None:
    """正常系: プロジェクト全件取得。"""
    mock_proj_service = mock_unit_of_work.service_factory.get_service.return_value
    mock_proj_service.get_all.return_value = [sample_project_read]

    res = project_app_service.get_all_projects()

    assert res == [sample_project_read]
    mock_proj_service.get_all.assert_called_once_with()


def test_list_by_status(
    project_app_service: ProjectApplicationService,
    mock_unit_of_work: Mock,
) -> None:
    """正常系: ステータス別取得で Service へパラメータを透過。"""
    mock_proj_service = mock_unit_of_work.service_factory.get_service.return_value

    project_app_service.list_by_status(ProjectStatus.COMPLETED)

    mock_proj_service.list_by_status.assert_called_once_with(ProjectStatus.COMPLETED)
