"""Application Service基底クラス

Application Service層の共通機能を提供する基底クラス
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from logic.unit_of_work import UnitOfWork


class BaseApplicationService:
    """Application Service基底クラス

    全てのApplication Serviceが継承すべき基底クラス。
    Unit of Workを使用してトランザクション管理を行います。
    """

    def __init__(self, unit_of_work_factory: type[UnitOfWork]) -> None:
        """BaseApplicationServiceの初期化

        Args:
            unit_of_work_factory: Unit of Workファクトリー
        """
        self._unit_of_work_factory = unit_of_work_factory
