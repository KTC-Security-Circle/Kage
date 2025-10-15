"""Application Service基底クラス

Application Service層の共通機能を提供する基底クラス
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from logic.unit_of_work import UnitOfWork


class BaseApplicationService[T: type[UnitOfWork] | None]:
    """Application Service基底クラス

    全てのApplication Serviceが継承すべき基底クラス。
    Unit of Workを使用してトランザクション管理を行います。
    """

    def __init__(self, unit_of_work_factory: T = None) -> None:
        """BaseApplicationServiceの初期化

        Args:
            unit_of_work_factory: Unit of Workファクトリー
        """
        self._unit_of_work_factory = unit_of_work_factory

    @classmethod
    def get_instance(cls, *args: Any, **kwargs: Any) -> BaseApplicationService:  # noqa: ANN401
        """Application Serviceのインスタンスを生成するファクトリメソッド

        Args:
            *args: コンストラクタ引数
            **kwargs: コンストラクタキーワード引数

        Returns:
            BaseApplicationService: Application Serviceのインスタンス
        """
        if not hasattr(cls, "_instance"):
            cls._instance = cls(*args, **kwargs)
        else:
            cls._instance.__init__(*args, **kwargs)
        return cls._instance
